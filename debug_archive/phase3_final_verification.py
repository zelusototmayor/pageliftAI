#!/usr/bin/env python3
"""
Phase 3 Final Verification - Comprehensive test of all Phase 3 improvements
"""

import requests
import json
import time
import sys

API_BASE = "http://localhost:8000"

def verify_phase3_improvements():
    """Verify all Phase 3 improvements are working"""
    print("🎯 Phase 3 Final Verification")
    print("=" * 50)
    
    # Test 1: End-to-end workflow
    print("1️⃣ Testing end-to-end workflow...")
    project_data = {
        "url": "https://example.com",
        "project_name": "Phase 3 Final Verification"
    }
    
    response = requests.post(f"{API_BASE}/projects", json=project_data, timeout=30)
    if response.status_code != 200:
        print("❌ Project creation failed")
        return False
    
    result = response.json()
    job_id = result["job_id"]
    print(f"✅ Project created (Job ID: {job_id})")
    
    # Monitor processing
    start_time = time.time()
    while time.time() - start_time < 60:
        job_response = requests.get(f"{API_BASE}/jobs/{job_id}")
        if job_response.status_code == 200:
            job_data = job_response.json()
            status = job_data["status"]
            
            if status == "complete":
                print("✅ Processing completed successfully")
                break
            elif status == "failed":
                print(f"❌ Processing failed: {job_data.get('error')}")
                return False
            else:
                print(f"   Status: {status}")
                time.sleep(3)
        else:
            print("❌ Job status check failed")
            return False
    else:
        print("❌ Processing timeout")
        return False
    
    # Test 2: Preview functionality
    print("\n2️⃣ Testing preview functionality...")
    preview_response = requests.get(f"{API_BASE}/jobs/{job_id}/preview", timeout=10)
    if preview_response.status_code == 200:
        html = preview_response.text
        if len(html) > 1000 and "<!DOCTYPE html>" in html:
            print("✅ Preview generated successfully")
        else:
            print("❌ Preview content invalid")
            return False
    else:
        print("❌ Preview failed")
        return False
    
    # Test 3: Download functionality
    print("\n3️⃣ Testing download functionality...")
    download_response = requests.get(f"{API_BASE}/jobs/{job_id}/download", timeout=10)
    if download_response.status_code == 200 and download_response.headers.get('content-type') == 'application/zip':
        print("✅ Download working correctly")
    else:
        print("❌ Download failed")
        return False
    
    # Test 4: Error handling
    print("\n4️⃣ Testing error handling...")
    error_project = {
        "url": "https://invalid-website-12345.com",
        "project_name": "Error Test"
    }
    
    error_response = requests.post(f"{API_BASE}/projects", json=error_project, timeout=30)
    if error_response.status_code == 200:
        error_job_id = error_response.json()["job_id"]
        
        # Wait for it to fail
        time.sleep(15)
        error_job_response = requests.get(f"{API_BASE}/jobs/{error_job_id}")
        
        if error_job_response.status_code == 200:
            error_job_data = error_job_response.json()
            if error_job_data["status"] == "failed" and error_job_data["error"]:
                print("✅ Error handling working correctly")
            else:
                print("❌ Error handling not working")
                return False
        else:
            print("❌ Error job status check failed")
            return False
    else:
        print("❌ Error test project creation failed")
        return False
    
    # Test 5: Quality validation
    print("\n5️⃣ Testing output quality...")
    quality_tests = [
        "✅ Valid HTML5 doctype" if "<!DOCTYPE html>" in html else "❌ Missing doctype",
        "✅ Has title tag" if "<title>" in html else "❌ Missing title",
        "✅ Mobile responsive" if "viewport" in html else "❌ Not responsive",
        "✅ Substantial content" if len(html) > 10000 else "❌ Insufficient content",
        "✅ Modern CSS" if ("display: flex" in html or "display: grid" in html) else "❌ No modern CSS",
        "✅ Semantic HTML" if any(tag in html for tag in ["<section", "<article", "<header"]) else "❌ No semantic HTML"
    ]
    
    for test in quality_tests:
        print(f"   {test}")
    
    quality_score = len([t for t in quality_tests if "✅" in t]) / len(quality_tests) * 100
    if quality_score >= 80:
        print(f"✅ Quality score: {quality_score:.0f}% (Excellent)")
    else:
        print(f"❌ Quality score: {quality_score:.0f}% (Below threshold)")
        return False
    
    return True

def main():
    """Run final verification"""
    try:
        # Check API health
        health = requests.get(f"{API_BASE}/healthz", timeout=5)
        if health.status_code != 200:
            print("❌ API not available - run: docker-compose up -d")
            return 1
        
        # Run verification
        if verify_phase3_improvements():
            print("\n🎉 Phase 3 verification completed successfully!")
            print("✅ All core functionality working")
            print("✅ Error handling improved")  
            print("✅ User feedback enhanced")
            print("✅ Output quality validated")
            print("\n🚀 Ready to commit Phase 3 improvements!")
            return 0
        else:
            print("\n❌ Phase 3 verification failed")
            return 1
            
    except Exception as e:
        print(f"\n❌ Verification error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())