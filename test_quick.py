# Quick test for LinkProxy API
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Test health check
print("Testing health check...")
response = client.get("/")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Test URL creation
print("\nTesting URL creation...")
test_url = {
    "original_url": "https://example.com",
    "title": "Test URL",
    "is_active": True
}

response = client.post("/shorten", json=test_url)
print(f"Status: {response.status_code}")
if response.status_code != 200:
    print(f"Error: {response.text}")
else:
    print(f"Response: {response.json()}")

    # Test redirect
    short_code = response.json()["short_code"]
    print(f"\nTesting redirect for {short_code}...")

    redirect_response = client.get(f"/{short_code}", follow_redirects=False)
    print(f"Redirect Status: {redirect_response.status_code}")
    print(f"Location: {redirect_response.headers.get('location', 'None')}")

    # Test analytics
    print(f"\nTesting analytics for {short_code}...")
    analytics_response = client.get(f"/analytics/{short_code}")
    print(f"Analytics Status: {analytics_response.status_code}")
    print(f"Analytics: {analytics_response.json()}")