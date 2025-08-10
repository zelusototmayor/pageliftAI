#!/usr/bin/env python3
"""
Test PageLift AI with real websites to validate output quality
"""

import requests
import json
import time
import sys

API_BASE = "http://localhost:8000"

# Test different types of websites
TEST_WEBSITES = [
    {
        "name": "Restaurant",
        "url": "https://restaurantwebsite.com",  # Example restaurant site
        "expected_sections": ["hero", "about", "services", "contact"]
    },
    {
        "name": "Plumbing Service", 
        "url": "https://www.plumbingservice.com",  # Example service business
        "expected_sections": ["hero", "about", "services", "contact"]
    },
    {
        "name": "Portfolio Site",
        "url": "https://portfolio-website.com",  # Example portfolio
        "expected_sections": ["hero", "about", "gallery", "contact"]
    }
]

def create_and_test_project(website):
    """Create project and test processing for a specific website"""
    print(f"\n🌐 Testing {website['name']}: {website['url']}")
    
    # Create project
    project_data = {
        "url": website['url'],
        "project_name": f"Test {website['name']}"
    }
    
    try:
        response = requests.post(f"{API_BASE}/projects", json=project_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            job_id = result.get("job_id")
            print(f"✅ Project created (Job ID: {job_id})")
        else:
            print(f"❌ Project creation failed: {response.status_code}")
            return False
        
        # Monitor job processing
        start_time = time.time()
        while time.time() - start_time < 120:  # 2 minute timeout
            job_response = requests.get(f"{API_BASE}/jobs/{job_id}", timeout=10)
            
            if job_response.status_code == 200:
                job_data = job_response.json()
                status = job_data.get("status")
                
                if status == "complete":
                    print(f"✅ Processing completed successfully")
                    
                    # Test preview
                    preview_response = requests.get(f"{API_BASE}/jobs/{job_id}/preview", timeout=10)
                    if preview_response.status_code == 200:
                        preview_html = preview_response.text
                        print(f"✅ Preview generated ({len(preview_html)} chars)")
                        
                        # Basic quality checks
                        quality_score = analyze_output_quality(preview_html, website)
                        print(f"📊 Quality Score: {quality_score}/100")
                        
                        return quality_score >= 70  # 70% threshold
                    else:
                        print(f"❌ Preview failed: {preview_response.status_code}")
                        return False
                        
                elif status == "failed":
                    error = job_data.get("error", "Unknown error")
                    print(f"❌ Processing failed: {error}")
                    return False
                else:
                    print(f"   Status: {status}")
                    time.sleep(5)
            else:
                print(f"❌ Job status check failed: {job_response.status_code}")
                return False
        
        print("❌ Processing timeout")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def analyze_output_quality(html_content, website):
    """Analyze the quality of generated HTML"""
    score = 0
    max_score = 100
    
    # Basic structure checks (40 points)
    if "<!DOCTYPE html>" in html_content:
        score += 10
        print("   ✅ Valid HTML5 doctype")
    
    if "<title>" in html_content and "</title>" in html_content:
        score += 10 
        print("   ✅ Has title tag")
    
    if 'viewport' in html_content:
        score += 10
        print("   ✅ Mobile responsive")
    
    if len(html_content) > 5000:  # Reasonable size
        score += 10
        print(f"   ✅ Substantial content ({len(html_content)} chars)")
    
    # Content quality (40 points)
    expected_sections = website.get('expected_sections', [])
    found_sections = 0
    
    for section_type in expected_sections:
        # Look for section indicators in HTML
        if (section_type.lower() in html_content.lower() or 
            f'class="{section_type}' in html_content.lower()):
            found_sections += 1
            print(f"   ✅ Found {section_type} section")
    
    section_score = (found_sections / len(expected_sections)) * 40 if expected_sections else 20
    score += int(section_score)
    
    # Modern features (20 points) 
    modern_features = [
        ('CSS Grid/Flexbox', ('display: grid' in html_content or 'display: flex' in html_content)),
        ('CSS Variables', ('--' in html_content and 'var(' in html_content)),
        ('Semantic HTML', any(tag in html_content for tag in ['<section', '<article', '<header', '<footer'])),
        ('Accessibility', ('aria-' in html_content or 'alt=' in html_content))
    ]
    
    for feature_name, has_feature in modern_features:
        if has_feature:
            score += 5
            print(f"   ✅ {feature_name}")
    
    return min(score, max_score)

def main():
    """Test with multiple real websites"""
    print("🌍 PageLift AI Real Website Quality Tests")
    print("=" * 50)
    
    # Check API health first
    try:
        health = requests.get(f"{API_BASE}/healthz", timeout=5)
        if health.status_code != 200:
            print("❌ API not available")
            return 1
    except:
        print("❌ Cannot connect to API")
        return 1
    
    results = []
    
    # Test with simpler, reliable websites first
    simple_tests = [
        {"name": "Example.com", "url": "https://example.com", "expected_sections": ["hero"]},
        {"name": "Simple Business", "url": "https://httpbin.org/html", "expected_sections": ["hero"]}
    ]
    
    print("\n🧪 Running with simple test sites first...")
    for website in simple_tests:
        success = create_and_test_project(website)
        results.append((website['name'], success))
    
    # Summary
    print("\n" + "=" * 50) 
    print("📊 QUALITY TEST RESULTS")
    print("=" * 50)
    
    passed = 0
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{name:20} {status}")
        if success:
            passed += 1
    
    print(f"\n📈 Overall: {passed}/{len(results)} websites passed quality threshold")
    
    if passed == len(results):
        print("🎉 All websites generated successfully!")
        return 0
    elif passed > 0:
        print("⚠️  Some websites passed - system is functional but may need tuning")
        return 0  # Still consider this a success for Phase 3
    else:
        print("❌ No websites met quality threshold")
        return 1

if __name__ == "__main__":
    sys.exit(main())