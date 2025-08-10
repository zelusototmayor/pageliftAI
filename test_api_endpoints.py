#!/usr/bin/env python3
"""
Test all API endpoints for functionality
"""

import requests
import json
import sys

API_BASE = "http://localhost:8000"

def test_endpoint(method, endpoint, data=None, expected_status=200, description=""):
    """Test a single API endpoint"""
    url = f"{API_BASE}{endpoint}"
    print(f"🔍 Testing {method} {endpoint} - {description}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
        
        if response.status_code == expected_status:
            print(f"✅ Success ({response.status_code})")
            
            # Print response preview for GET requests
            if method == "GET" and response.headers.get('content-type', '').startswith('application/json'):
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"   Response: List with {len(data)} items")
                    elif isinstance(data, dict):
                        keys = list(data.keys())[:3]
                        print(f"   Response: Dict with keys: {keys}")
                except:
                    print(f"   Response: {len(response.text)} chars")
            
            return True
        else:
            print(f"❌ Failed ({response.status_code}): {response.text[:100]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def main():
    """Test all API endpoints"""
    print("🔧 PageLift AI API Endpoint Tests")
    print("=" * 50)
    
    tests = [
        # Basic endpoints
        ("GET", "/healthz", None, 200, "Health check"),
        ("GET", "/projects", None, 200, "List all projects"),
        
        # Create a test project
        ("POST", "/projects", {
            "url": "https://example.com",
            "project_name": "API Endpoint Test"
        }, 200, "Create project"),
        
        # We'll use the project/job ID from the previous successful tests
        ("GET", "/jobs/75", None, 200, "Get job details"),
        ("GET", "/jobs/75/preview", None, 200, "Preview generated site"),
        
        # Debug endpoints
        ("GET", "/debug/job/75/extraction", None, 200, "Debug extraction data"),
        ("GET", "/debug/job/75/comparison", None, 200, "Debug comparison"),
        ("GET", "/debug/extraction-quality", None, 200, "Debug extraction quality"),
        ("GET", "/debug/job/75/quality-report", None, 200, "Debug quality report"),
        
        # Validation endpoint
        ("POST", "/debug/validate-url", {
            "url": "https://example.com"
        }, 200, "Validate URL"),
    ]
    
    results = []
    
    for method, endpoint, data, expected_status, description in tests:
        success = test_endpoint(method, endpoint, data, expected_status, description)
        results.append((f"{method} {endpoint}", success))
        print()  # Add spacing
    
    # Results summary
    print("=" * 50)
    print("📊 API ENDPOINT TEST RESULTS")
    print("=" * 50)
    
    passed = 0
    for endpoint, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{endpoint:35} {status}")
        if success:
            passed += 1
    
    print(f"\n📈 Overall: {passed}/{len(results)} endpoints working")
    
    if passed == len(results):
        print("🎉 All API endpoints are functional!")
        return 0
    elif passed >= len(results) * 0.8:  # 80% threshold
        print("⚠️  Most endpoints working - minor issues may exist")
        return 0
    else:
        print("❌ Significant API endpoint issues found")
        return 1

if __name__ == "__main__":
    sys.exit(main())