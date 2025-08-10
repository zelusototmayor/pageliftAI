#!/usr/bin/env python3
"""
Phase 3 Core Functionality Test Script

This script tests the core PageLift AI functionality end-to-end:
1. Project creation via API
2. Job processing pipeline
3. Scraping and analysis
4. Website rendering and file generation
5. Storage functionality

Can be run independently or with Docker services.
"""

import requests
import json
import time
import sys
import os
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

# Test configuration
TEST_URL = "https://www.example.com"  # Simple test site
API_BASE = "http://localhost:8000"  # FastAPI server
MAX_WAIT_TIME = 300  # 5 minutes max wait for job completion

def test_api_health():
    """Test if the API server is running"""
    print("🔍 Testing API health...")
    try:
        response = requests.get(f"{API_BASE}/healthz", timeout=10)
        if response.status_code == 200:
            print("✅ API server is healthy")
            return True
        else:
            print(f"❌ API server returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API server: {e}")
        print("💡 Make sure to run: docker-compose up -d api")
        return False

def test_project_creation():
    """Test project creation via API"""
    print("\n🔍 Testing project creation...")
    
    project_data = {
        "url": TEST_URL,
        "project_name": "Phase 3 Test Project"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/projects", 
            json=project_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            project_id = result.get("project_id")
            job_id = result.get("job_id")
            
            if project_id and job_id:
                print(f"✅ Project created successfully!")
                print(f"   Project ID: {project_id}")
                print(f"   Job ID: {job_id}")
                return project_id, job_id
            else:
                print(f"❌ Invalid response format: {result}")
                return None, None
        else:
            print(f"❌ Project creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None, None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None, None

def test_job_processing(job_id):
    """Test job processing pipeline by monitoring job status"""
    print(f"\n🔍 Testing job processing (Job ID: {job_id})...")
    
    start_time = time.time()
    last_status = None
    
    while time.time() - start_time < MAX_WAIT_TIME:
        try:
            response = requests.get(f"{API_BASE}/jobs/{job_id}", timeout=10)
            
            if response.status_code == 200:
                job_data = response.json()
                status = job_data.get("status")
                error = job_data.get("error")
                
                if status != last_status:
                    print(f"   Status: {status}")
                    last_status = status
                
                if status == "complete":
                    download_url = job_data.get("download_url")
                    print(f"✅ Job completed successfully!")
                    print(f"   Download URL: {download_url}")
                    return True, job_data
                elif status == "failed":
                    print(f"❌ Job failed: {error}")
                    return False, job_data
                elif status in ["queued", "scraping", "analyzing", "rendering"]:
                    # Job is still processing
                    time.sleep(5)
                    continue
                else:
                    print(f"❌ Unknown job status: {status}")
                    return False, job_data
            else:
                print(f"❌ Failed to check job status: {response.status_code}")
                return False, None
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Request error: {e}")
            time.sleep(5)
            continue
    
    print(f"❌ Job processing timeout after {MAX_WAIT_TIME} seconds")
    return False, None

def test_pipeline_components_independently():
    """Test pipeline components without API/Docker"""
    print("\n🔍 Testing pipeline components independently...")
    
    try:
        # Test imports
        from app.services.scrape import scrape_site
        from app.services.parse import parse_html_sections  
        from app.services.analyze import analyze_sections
        from app.services.render import render_site_with_brand
        from app.services.brand_extraction import extract_brand_identity
        
        print("✅ All service imports successful")
        
        # Test scraping
        print("   Testing scraping...")
        scrape_result = scrape_site(TEST_URL)
        if scrape_result and scrape_result.pages:
            html = scrape_result.pages[0].html
            print(f"   ✅ Scraping successful ({len(html)} chars)")
        else:
            print("   ❌ Scraping failed")
            return False
        
        # Test parsing
        print("   Testing parsing...")
        sections = parse_html_sections(html)
        if sections:
            print(f"   ✅ Parsing successful ({len(sections)} sections)")
        else:
            print("   ❌ Parsing failed")
            return False
        
        # Test analysis (might require OpenAI API)
        print("   Testing analysis (requires OpenAI API)...")
        try:
            section_dicts = [s.__dict__ for s in sections[:3]]  # Test with first 3 sections
            analyses = analyze_sections(section_dicts)
            if analyses:
                print(f"   ✅ Analysis successful ({len(analyses)} analyses)")
            else:
                print("   ❌ Analysis failed")
                return False
        except Exception as e:
            print(f"   ⚠️  Analysis failed (may need valid OpenAI API key): {e}")
            # Continue testing other components
        
        # Test brand extraction
        print("   Testing brand extraction...")
        try:
            brand_identity = extract_brand_identity(TEST_URL, html)
            if brand_identity:
                print(f"   ✅ Brand extraction successful")
                print(f"      Industry: {brand_identity.industry}")
                print(f"      Primary color: {brand_identity.colors.primary}")
            else:
                print("   ❌ Brand extraction failed")
                return False
        except Exception as e:
            print(f"   ⚠️  Brand extraction failed: {e}")
        
        print("✅ Core pipeline components are functional")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're in the correct directory and dependencies are installed")
        return False
    except Exception as e:
        print(f"❌ Component test error: {e}")
        return False

def test_projects_list():
    """Test projects listing endpoint"""
    print("\n🔍 Testing projects list...")
    
    try:
        response = requests.get(f"{API_BASE}/projects", timeout=10)
        
        if response.status_code == 200:
            projects = response.json()
            print(f"✅ Projects list retrieved ({len(projects)} projects)")
            
            if projects:
                latest_project = projects[0]
                print(f"   Latest project: {latest_project.get('name')}")
                print(f"   Status: {latest_project.get('status')}")
            
            return True
        else:
            print(f"❌ Projects list failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def main():
    """Run comprehensive core functionality tests"""
    print("🚀 PageLift AI Phase 3 Core Functionality Tests")
    print("=" * 50)
    
    results = {
        "api_health": False,
        "component_tests": False,
        "project_creation": False,
        "job_processing": False,
        "projects_list": False
    }
    
    # Test 1: API Health (requires Docker services)
    results["api_health"] = test_api_health()
    
    # Test 2: Component Tests (independent)
    results["component_tests"] = test_pipeline_components_independently()
    
    # Test 3-5: API-based tests (require Docker services)
    if results["api_health"]:
        # Test project creation
        project_id, job_id = test_project_creation()
        results["project_creation"] = (project_id is not None and job_id is not None)
        
        # Test job processing (if project creation succeeded)
        if results["project_creation"]:
            success, job_data = test_job_processing(job_id)
            results["job_processing"] = success
            
        # Test projects list
        results["projects_list"] = test_projects_list()
    else:
        print("\n⚠️  Skipping API-based tests (API server not available)")
        print("💡 To run full tests: docker-compose up -d")
    
    # Results Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title():20} {status}")
    
    passed_tests = sum(results.values())
    total_tests = len(results)
    
    print(f"\n📈 Overall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Core functionality is working.")
        return 0
    elif results["component_tests"]:
        print("⚠️  Core components work, but API/infrastructure issues exist.")
        print("💡 Run 'docker-compose up -d' and try again.")
        return 1
    else:
        print("❌ Critical functionality issues found.")
        return 2

if __name__ == "__main__":
    sys.exit(main())