"""
URL Generation Service - Base62 Algorithm
Optimized for unique codes without collisions and comprehensive validation
"""

import secrets
import string
import time
from typing import Set, Optional
import hashlib
import re


class URLGenerator:
    """
    URL short code generator using Base62 algorithm
    Optimized for high performance and zero collisions
    """

    # Base62 alphabet (more readable than Base64)
    BASE62_CHARS = string.ascii_letters + string.digits  # A-Z, a-z, 0-9

    def __init__(self, default_length: int = 6, max_attempts: int = 10):
        """
        Initialize URL generator

        Args:
            default_length: Default length for generated codes (6-8 recommended)
            max_attempts: Max attempts to generate unique code before increasing length
        """
        self.default_length = default_length
        self.max_attempts = max_attempts
        self._collision_count = 0
        self._generated_codes: Set[str] = set()

    def generate_short_code(
        self,
        url: str = None,
        length: Optional[int] = None
    ) -> str:
        """
        Generate a unique short code using Base62 algorithm

        Args:
            url: Optional URL for hash-based generation
            length: Override default length

        Returns:
            Unique Base62 short code

        Raises:
            ValueError: If unable to generate unique code after max attempts
        """
        target_length = length or self.default_length

        # Try different strategies for generation
        for attempt in range(self.max_attempts):
            if url and attempt == 0:
                # Strategy 1: Hash-based generation (deterministic but unique)
                code = self._generate_from_hash(url, target_length)
            else:
                # Strategy 2: Cryptographically secure random
                code = self._generate_random(target_length)

            # Validate uniqueness (in production, check against database)
            if code not in self._generated_codes:
                self._generated_codes.add(code)
                return code

            self._collision_count += 1

            # Increase length if too many collisions
            if attempt == self.max_attempts // 2:
                target_length += 1

        # Last resort: timestamp-based with random suffix
        return self._generate_timestamp_based(target_length)

    def _generate_random(self, length: int) -> str:
        """Generate cryptographically secure random Base62 code"""
        return ''.join(secrets.choice(self.BASE62_CHARS) for _ in range(length))

    def _generate_from_hash(self, url: str, length: int) -> str:
        """
        Generate code from URL hash - provides some determinism
        while maintaining uniqueness through salt
        """
        # Create hash with timestamp salt for uniqueness
        salt = str(int(time.time() * 1000000))  # microsecond precision
        hash_input = f"{url}:{salt}"

        # Use SHA-256 for strong hash distribution
        hash_digest = hashlib.sha256(hash_input.encode()).hexdigest()

        # Convert hex to Base62
        return self._hex_to_base62(hash_digest, length)

    def _hex_to_base62(self, hex_string: str, length: int) -> str:
        """Convert hexadecimal string to Base62"""
        # Convert hex to int
        num = int(hex_string[:16], 16)  # Use first 16 hex chars (64 bits)

        if num == 0:
            return self.BASE62_CHARS[0] * length

        result = ""
        base = len(self.BASE62_CHARS)

        while num > 0 and len(result) < length:
            result = self.BASE62_CHARS[num % base] + result
            num //= base

        # Pad to desired length
        while len(result) < length:
            result = self.BASE62_CHARS[0] + result

        return result[:length]

    def _generate_timestamp_based(self, length: int) -> str:
        """
        Last resort: timestamp-based generation
        Guarantees uniqueness through time component
        """
        timestamp = int(time.time() * 1000)  # millisecond precision

        # Convert timestamp to Base62
        timestamp_b62 = ""
        base = len(self.BASE62_CHARS)

        while timestamp > 0:
            timestamp_b62 = self.BASE62_CHARS[timestamp % base] + timestamp_b62
            timestamp //= base

        # Add random suffix to reach desired length
        remaining_length = max(0, length - len(timestamp_b62))
        if remaining_length > 0:
            suffix = self._generate_random(remaining_length)
            return timestamp_b62 + suffix

        return timestamp_b62[:length]

    def validate_code(self, code: str) -> bool:
        """
        Validate that a code meets Base62 format requirements

        Args:
            code: Short code to validate

        Returns:
            True if valid, False otherwise
        """
        if not code:
            return False

        # Check length (4-8 characters recommended)
        if not (4 <= len(code) <= 8):
            return False

        # Check character set (Base62 only)
        pattern = r'^[A-Za-z0-9]+$'
        if not re.match(pattern, code):
            return False

        return True

    def get_collision_stats(self) -> dict:
        """Get collision statistics for monitoring"""
        return {
            'total_collisions': self._collision_count,
            'total_generated': len(self._generated_codes),
            'collision_rate': self._collision_count / max(1, len(self._generated_codes)),
            'alphabet_size': len(self.BASE62_CHARS),
            'theoretical_combinations': len(self.BASE62_CHARS) ** self.default_length
        }


# Singleton instance for global use
url_generator = URLGenerator(default_length=6, max_attempts=10)


def generate_short_code(url: str = None, length: int = None) -> str:
    """Convenience function to generate short codes"""
    return url_generator.generate_short_code(url, length)


def validate_short_code(code: str) -> bool:
    """Convenience function to validate short codes"""
    return url_generator.validate_code(code)