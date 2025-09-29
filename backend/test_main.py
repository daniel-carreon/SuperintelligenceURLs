"""
E2E Tests for LinkProxy FastAPI endpoints
Testing redirect service performance and functionality
"""

import pytest
from fastapi.testclient import TestClient
import time

# Import the FastAPI app
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))
from main import app

# Create test client
client = TestClient(app)


class TestLinkProxyEndpoints:
    """E2E tests for LinkProxy API endpoints"""

    def test_health_check(self):
        """Test basic health check endpoint"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "LinkProxy"
        assert data["status"] == "active"
        assert "timestamp" in data

    def test_create_short_url(self):
        """Test URL shortening endpoint"""
        test_url = {
            "original_url": "https://example.com",
            "title": "Test URL",
            "is_active": True
        }

        response = client.post("/shorten", json=test_url)

        assert response.status_code == 200
        data = response.json()

        # Validate response structure
        assert "short_code" in data
        assert "original_url" in data
        assert data["original_url"] == test_url["original_url"]
        assert data["title"] == test_url["title"]
        assert data["is_active"] is True
        assert data["click_count"] == 0

        # Validate short code format
        short_code = data["short_code"]
        assert len(short_code) >= 4
        assert len(short_code) <= 8
        assert short_code.isalnum()

        return data

    def test_redirect_functionality(self):
        """Test redirect endpoint performance and functionality"""
        # First create a URL
        test_url = {
            "original_url": "https://google.com",
            "title": "Google",
            "is_active": True
        }

        create_response = client.post("/shorten", json=test_url)
        assert create_response.status_code == 200

        short_code = create_response.json()["short_code"]

        # Test redirect performance
        start_time = time.perf_counter()

        redirect_response = client.get(
            f"/{short_code}",
            follow_redirects=False  # Don't follow redirect to test response
        )

        redirect_time = (time.perf_counter() - start_time) * 1000

        # Validate redirect response
        assert redirect_response.status_code == 301  # Permanent redirect
        assert redirect_response.headers["location"] == test_url["original_url"]

        # Validate performance target (< 50ms)
        assert redirect_time < 50, f"Redirect too slow: {redirect_time:.2f}ms"

        print(f"✅ Redirect performance: {redirect_time:.2f}ms")

    def test_analytics_tracking(self):
        """Test that clicks are tracked properly"""
        # Create URL
        test_url = {
            "original_url": "https://github.com",
            "title": "GitHub",
            "is_active": True
        }

        create_response = client.post("/shorten", json=test_url)
        short_code = create_response.json()["short_code"]

        # Simulate multiple clicks
        for i in range(3):
            client.get(f"/{short_code}", follow_redirects=False)

        # Check analytics
        analytics_response = client.get(f"/analytics/{short_code}")
        assert analytics_response.status_code == 200

        analytics_data = analytics_response.json()
        assert analytics_data["short_code"] == short_code
        assert analytics_data["total_clicks"] == 3
        assert "device_breakdown" in analytics_data
        assert "recent_clicks" in analytics_data

    def test_invalid_short_code(self):
        """Test error handling for invalid short codes"""
        # Test non-existent code
        response = client.get("/NONEXIST", follow_redirects=False)
        assert response.status_code == 404

        # Test invalid format
        response = client.get("/invalid-format!", follow_redirects=False)
        assert response.status_code == 404

    def test_invalid_url_creation(self):
        """Test validation for URL creation"""
        # Test invalid URL format
        invalid_url = {
            "original_url": "not-a-url",
            "title": "Invalid",
            "is_active": True
        }

        response = client.post("/shorten", json=invalid_url)
        assert response.status_code == 400

    def test_health_endpoint(self):
        """Test detailed health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "metrics" in data

    def test_performance_benchmark(self):
        """Test performance of multiple operations"""
        urls_to_test = [
            "https://google.com",
            "https://github.com",
            "https://stackoverflow.com",
            "https://python.org",
            "https://fastapi.tiangolo.com"
        ]

        creation_times = []
        redirect_times = []

        for url in urls_to_test:
            # Time URL creation
            start_time = time.perf_counter()

            create_response = client.post("/shorten", json={
                "original_url": url,
                "title": f"Test {url}",
                "is_active": True
            })

            creation_time = (time.perf_counter() - start_time) * 1000
            creation_times.append(creation_time)

            assert create_response.status_code == 200
            short_code = create_response.json()["short_code"]

            # Time redirect
            start_time = time.perf_counter()

            redirect_response = client.get(f"/{short_code}", follow_redirects=False)

            redirect_time = (time.perf_counter() - start_time) * 1000
            redirect_times.append(redirect_time)

            assert redirect_response.status_code == 301

        # Performance validation
        avg_creation = sum(creation_times) / len(creation_times)
        avg_redirect = sum(redirect_times) / len(redirect_times)

        print(f"📊 Performance Results:")
        print(f"  Average creation time: {avg_creation:.2f}ms")
        print(f"  Average redirect time: {avg_redirect:.2f}ms")
        print(f"  Max creation time: {max(creation_times):.2f}ms")
        print(f"  Max redirect time: {max(redirect_times):.2f}ms")

        # Validate performance targets
        assert avg_creation < 100, f"URL creation too slow: {avg_creation:.2f}ms"
        assert avg_redirect < 50, f"Redirect too slow: {avg_redirect:.2f}ms"

        print("✅ All performance targets met!")

    def test_concurrent_url_creation(self):
        """Test concurrent URL creation for uniqueness"""
        import concurrent.futures
        import threading

        urls_created = []
        lock = threading.Lock()

        def create_url(index):
            response = client.post("/shorten", json={
                "original_url": f"https://example.com/page{index}",
                "title": f"Page {index}",
                "is_active": True
            })

            if response.status_code == 200:
                with lock:
                    urls_created.append(response.json()["short_code"])

        # Create URLs concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_url, i) for i in range(20)]
            concurrent.futures.wait(futures)

        # Validate all codes are unique
        assert len(urls_created) == 20
        assert len(set(urls_created)) == 20  # All unique

        print(f"✅ Created {len(urls_created)} unique URLs concurrently")


if __name__ == "__main__":
    # Run tests directly
    print("🧪 Running LinkProxy E2E Tests")
    print("=" * 40)

    test_suite = TestLinkProxyEndpoints()

    try:
        test_suite.test_health_check()
        print("✅ Health check: PASSED")

        test_suite.test_create_short_url()
        print("✅ URL creation: PASSED")

        test_suite.test_redirect_functionality()
        print("✅ Redirect functionality: PASSED")

        test_suite.test_analytics_tracking()
        print("✅ Analytics tracking: PASSED")

        test_suite.test_invalid_short_code()
        print("✅ Error handling: PASSED")

        test_suite.test_performance_benchmark()
        print("✅ Performance benchmark: PASSED")

        test_suite.test_concurrent_url_creation()
        print("✅ Concurrent creation: PASSED")

        print("\n🎉 All E2E tests PASSED!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise