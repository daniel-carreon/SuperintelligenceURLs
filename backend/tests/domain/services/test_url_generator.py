"""
Tests for URL Generator Service
Validación exhaustiva del algoritmo Base62
"""

import pytest
import time
import string
from unittest.mock import patch

# Add backend to Python path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from domain.services.url_generator import (
    URLGenerator,
    generate_short_code,
    validate_short_code
)


class TestURLGenerator:
    """Test suite for URL Generator with comprehensive validation"""

    def setup_method(self):
        """Setup fresh generator for each test"""
        self.generator = URLGenerator(default_length=6, max_attempts=10)

    def test_generate_basic_code(self):
        """Test basic code generation"""
        code = self.generator.generate_short_code()

        # Validate format
        assert len(code) == 6
        assert code.isalnum()
        assert all(c in string.ascii_letters + string.digits for c in code)

    def test_generate_with_custom_length(self):
        """Test code generation with custom length"""
        for length in [4, 5, 6, 7, 8]:
            code = self.generator.generate_short_code(length=length)
            assert len(code) == length
            assert validate_short_code(code)

    def test_uniqueness_validation(self):
        """Test that generated codes are unique"""
        codes = set()
        iterations = 1000

        for _ in range(iterations):
            code = self.generator.generate_short_code()
            assert code not in codes, f"Collision detected: {code}"
            codes.add(code)

        assert len(codes) == iterations

    def test_hash_based_generation(self):
        """Test hash-based generation produces valid codes"""
        test_urls = [
            "https://google.com",
            "https://github.com/user/repo",
            "https://very-long-domain-name.com/path/to/resource?query=param"
        ]

        for url in test_urls:
            code = self.generator.generate_short_code(url=url)
            assert validate_short_code(code)
            assert len(code) == 6

    def test_collision_resistance(self):
        """Test collision resistance with high iteration count"""
        generator = URLGenerator(default_length=6, max_attempts=5)
        codes = set()
        collision_count = 0
        iterations = 10000

        for _ in range(iterations):
            code = generator.generate_short_code()
            if code in codes:
                collision_count += 1
            codes.add(code)

        # With 6-character Base62, collision rate should be very low
        collision_rate = collision_count / iterations
        assert collision_rate < 0.01, f"Collision rate too high: {collision_rate:.4f}"
        print(f"✅ Collision rate: {collision_rate:.6f} ({collision_count}/{iterations})")

    def test_performance_benchmark(self):
        """Test generation performance meets requirements"""
        iterations = 1000
        start_time = time.perf_counter()

        for _ in range(iterations):
            self.generator.generate_short_code()

        end_time = time.perf_counter()
        avg_time_ms = ((end_time - start_time) * 1000) / iterations

        # Target: < 10ms per code generation
        assert avg_time_ms < 10, f"Generation too slow: {avg_time_ms:.2f}ms"
        print(f"✅ Avg generation time: {avg_time_ms:.3f}ms")

    def test_validation_function(self):
        """Test code validation function"""
        # Valid codes
        valid_codes = ["ABC123", "abcDEF", "123456", "aB3X9z"]
        for code in valid_codes:
            assert validate_short_code(code), f"Valid code rejected: {code}"

        # Invalid codes
        invalid_codes = [
            "",           # Empty
            "AB",         # Too short
            "123456789",  # Too long
            "ABC-123",    # Invalid character
            "ABC@123",    # Invalid character
            "ñ123",       # Invalid character
        ]
        for code in invalid_codes:
            assert not validate_short_code(code), f"Invalid code accepted: {code}"

    def test_timestamp_fallback(self):
        """Test timestamp-based generation as fallback"""
        # Mock high collision scenario
        generator = URLGenerator(default_length=4, max_attempts=2)

        # Fill up the internal collision set to force fallback
        with patch.object(generator, '_generated_codes', set(["AAAA", "BBBB", "CCCC"])):
            with patch.object(generator, '_generate_random', return_value="AAAA"):  # Force collision
                code = generator.generate_short_code()
                assert validate_short_code(code)
                assert len(code) >= 4

    def test_collision_statistics(self):
        """Test collision statistics tracking"""
        generator = URLGenerator()

        # Generate some codes to create stats
        for _ in range(100):
            generator.generate_short_code()

        stats = generator.get_collision_stats()
        assert 'total_collisions' in stats
        assert 'total_generated' in stats
        assert 'collision_rate' in stats
        assert stats['alphabet_size'] == 62

    def test_concurrent_generation(self):
        """Test thread safety (basic)"""
        import concurrent.futures

        def generate_batch(batch_size: int) -> list:
            generator = URLGenerator()  # Each thread gets own instance
            return [generator.generate_short_code() for _ in range(batch_size)]

        # Generate codes from multiple threads
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(generate_batch, 50) for _ in range(4)]
            all_codes = []

            for future in concurrent.futures.as_completed(futures):
                all_codes.extend(future.result())

        # Check all codes are unique across threads
        assert len(set(all_codes)) == len(all_codes)

    def test_edge_cases(self):
        """Test edge cases and error handling"""
        generator = URLGenerator()

        # Very long URL
        long_url = "https://example.com/" + "x" * 1000
        code = generator.generate_short_code(url=long_url)
        assert validate_short_code(code)

        # URL with special characters
        special_url = "https://example.com/path?query=value&other=123#fragment"
        code = generator.generate_short_code(url=special_url)
        assert validate_short_code(code)

    def test_deterministic_behavior(self):
        """Test that same URL can produce different codes (for uniqueness)"""
        url = "https://example.com"
        codes = {self.generator.generate_short_code(url=url) for _ in range(10)}

        # Should generate different codes each time due to timestamp salt
        assert len(codes) > 1, "Hash-based generation should vary due to timestamp"


class TestConvenienceFunctions:
    """Test standalone convenience functions"""

    def test_generate_short_code_function(self):
        """Test convenience function for code generation"""
        code = generate_short_code()
        assert validate_short_code(code)
        assert len(code) == 6

    def test_generate_with_url_and_length(self):
        """Test convenience function with parameters"""
        code = generate_short_code(url="https://example.com", length=8)
        assert validate_short_code(code)
        assert len(code) == 8

    def test_validate_function_comprehensive(self):
        """Comprehensive validation function testing"""
        # Test all valid Base62 characters
        all_chars = string.ascii_letters + string.digits
        test_code = ''.join(all_chars[i] for i in [0, 25, 26, 51, 52, 61])  # Sample across ranges
        assert validate_short_code(test_code)


if __name__ == "__main__":
    # Run basic tests if executed directly
    print("🧪 Running URL Generator Tests")
    print("=" * 40)

    # Quick validation
    test_generator = TestURLGenerator()
    test_generator.setup_method()

    try:
        test_generator.test_generate_basic_code()
        print("✅ Basic generation: PASSED")

        test_generator.test_uniqueness_validation()
        print("✅ Uniqueness validation: PASSED")

        test_generator.test_collision_resistance()
        print("✅ Collision resistance: PASSED")

        test_generator.test_performance_benchmark()
        print("✅ Performance benchmark: PASSED")

        print("\n🎉 All critical tests PASSED!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise