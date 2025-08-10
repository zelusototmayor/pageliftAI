#!/usr/bin/env python3
"""
Fallback Categorization Test
Tests the enhanced fallback categorization logic without needing OpenAI API
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from typing import List, Dict, Any
from app.services.analyze import determine_fallback_category

def create_test_cases() -> List[Dict[str, Any]]:
    """Create comprehensive test cases for fallback categorization"""
    
    return [
        # HERO sections
        {
            "section_id": 0,  # First section
            "text": "Welcome to Expert Plumbing Services. Professional plumbing solutions for your home and business needs. Leading provider in the area.",
            "heading": "Expert Plumbing Services - Professional Quality",
            "business_data": {"phones": ["+1-555-PLUMBER"], "ctas": ["Call Now"], "emails": []},
            "classes": ["hero", "main-banner"],
            "id": "hero-section",
            "img_urls": ["hero.jpg"],
            "expected": "hero"
        },
        
        # ABOUT sections  
        {
            "section_id": 2,
            "text": "About Our Company: With over 15 years of experience serving the local community, our team of licensed and insured professionals brings expertise to every job. Founded in 2008, we are family-owned and operated, committed to honest pricing and quality workmanship.",
            "heading": "About Our Expert Team",
            "business_data": {"phones": [], "ctas": [], "emails": []},
            "classes": ["about", "company-info"],
            "id": "about-section", 
            "img_urls": ["team-photo.jpg"],
            "expected": "about"
        },
        
        # SERVICES sections
        {
            "section_id": 3,
            "text": "Our services include emergency plumbing repairs, drain cleaning, pipe installation, water heater repair and replacement, bathroom remodeling, kitchen plumbing, commercial solutions. We offer comprehensive plumbing services for residential and commercial properties.",
            "heading": "Professional Plumbing Services",
            "business_data": {"phones": [], "ctas": ["Learn More"], "emails": []},
            "classes": ["services", "service-list"],
            "id": "services-section",
            "img_urls": ["services.jpg"],
            "expected": "services"
        },
        
        # CONTACT sections
        {
            "section_id": 5,
            "text": "Contact us today for all your plumbing needs. Call us at (555) PLUMBER or email info@expertplumbing.com. Located at 123 Main Street. We offer free estimates and 24/7 emergency service.",
            "heading": "Get in Touch",
            "business_data": {"phones": ["+1-555-PLUMBER"], "emails": ["info@expertplumbing.com"], "ctas": ["Call Now"]},
            "classes": ["contact", "contact-info"],
            "id": "contact-section",
            "img_urls": [],
            "expected": "contact"
        },
        
        # GALLERY sections
        {
            "section_id": 4,
            "text": "See our work in action. Here are some examples of recent plumbing projects completed by our expert team. Customer testimonials and before/after photos showcase our quality workmanship.",
            "heading": "Our Work Gallery",
            "business_data": {"phones": [], "ctas": [], "emails": []},
            "classes": ["gallery", "portfolio"],
            "id": "gallery-section",
            "img_urls": ["before1.jpg", "after1.jpg", "project2.jpg", "testimonial.jpg"],
            "expected": "gallery"
        },
        
        # OTHER sections
        {
            "section_id": 8,
            "text": "Privacy Policy: This website collects information to provide better service. We respect your privacy and do not share personal information with third parties. Cookie policy applies.",
            "heading": "Privacy Policy",
            "business_data": {"phones": [], "ctas": [], "emails": []},
            "classes": ["footer", "legal"],
            "id": "privacy-policy",
            "img_urls": [],
            "expected": "other"
        },
        
        # EDGE CASES
        
        # Empty content with images
        {
            "section_id": 6,
            "text": "",
            "heading": "",
            "business_data": {"phones": [], "ctas": [], "emails": []},
            "classes": [],
            "id": "",
            "img_urls": ["decoration.jpg"],
            "expected": "other"  # Should default to other for empty content
        },
        
        # Mixed content (should use keywords and position)
        {
            "section_id": 1,
            "text": "Professional quality service. About our team: we provide expert solutions. Contact us today for services.",
            "heading": "Mixed Content Section",
            "business_data": {"phones": [], "ctas": ["Contact"], "emails": []},
            "classes": ["mixed"],
            "id": "mixed-section",
            "img_urls": [],
            "expected": "hero"  # First position with professional language
        },
        
        # Portuguese content
        {
            "section_id": 2,
            "text": "Sobre nossa empresa: Com mais de 15 anos de experiência, nossa equipa de profissionais licenciados traz expertise para cada trabalho. Somos uma empresa familiar, comprometida com preços honestos.",
            "heading": "Sobre Nossa Equipa",
            "business_data": {"phones": [], "ctas": [], "emails": []},
            "classes": ["sobre", "empresa"],
            "id": "sobre-secao",
            "img_urls": ["equipa.jpg"],
            "expected": "about"  # Portuguese "sobre" should trigger about
        },
        
        # Class-based detection
        {
            "section_id": 7,
            "text": "Some content here that doesn't have strong keywords.",
            "heading": "Generic Heading",
            "business_data": {"phones": [], "ctas": [], "emails": []},
            "classes": ["service-cards", "offerings"],
            "id": "service-grid",
            "img_urls": [],
            "expected": "services"  # Should be detected by class hints
        }
    ]

def test_fallback_categorization():
    """Test the fallback categorization with comprehensive test cases"""
    
    test_cases = create_test_cases()
    
    print("🧪 Testing Enhanced Fallback Categorization")
    print("=" * 70)
    
    correct = 0
    total = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        expected = test_case.pop("expected")  # Remove expected from test data
        
        # Run the categorization
        result = determine_fallback_category(test_case)
        
        # Check if correct
        is_correct = result == expected
        if is_correct:
            correct += 1
        
        status = "✅" if is_correct else "❌"
        print(f"{status} Test {i:2d}: {result:8s} (expected: {expected:8s})")
        
        # Show details for failed tests
        if not is_correct:
            print(f"         Text: {test_case['text'][:60]}...")
            print(f"         Heading: {test_case['heading']}")
            print(f"         Classes: {test_case['classes']}")
            print(f"         Position: {test_case['section_id']}")
        
        print()
    
    # Results summary
    accuracy = (correct / total) * 100
    print("=" * 70)
    print(f"📊 Fallback Categorization Results")
    print(f"   Accuracy: {correct}/{total} ({accuracy:.1f}%)")
    
    if accuracy >= 90:
        print("   🎉 EXCELLENT: Fallback logic is highly accurate!")
    elif accuracy >= 80:
        print("   ✅ GOOD: Fallback logic performs well")
    elif accuracy >= 70:
        print("   ⚠️  AVERAGE: Fallback logic needs some improvement")
    else:
        print("   ❌ POOR: Fallback logic needs significant work")
    
    return accuracy >= 80

def test_edge_cases():
    """Test additional edge cases"""
    
    print("\n🧪 Testing Edge Cases")
    print("=" * 70)
    
    edge_cases = [
        # Very short content
        {"section_id": 0, "text": "Hi", "heading": "", "business_data": {}, "classes": [], "id": "", "img_urls": []},
        
        # Very long content
        {"section_id": 3, "text": "Lorem ipsum " * 100, "heading": "Long Content", "business_data": {}, "classes": [], "id": "", "img_urls": []},
        
        # Only business data, no text
        {"section_id": 5, "text": "", "heading": "", "business_data": {"phones": ["+1-555-1234"], "emails": ["test@test.com"]}, "classes": [], "id": "", "img_urls": []},
        
        # Only images, no text
        {"section_id": 4, "text": "", "heading": "", "business_data": {}, "classes": [], "id": "", "img_urls": ["img1.jpg", "img2.jpg", "img3.jpg"]},
    ]
    
    for i, case in enumerate(edge_cases, 1):
        result = determine_fallback_category(case)
        print(f"   Edge case {i}: {result}")
        print(f"     Text length: {len(case['text'])}")
        print(f"     Images: {len(case['img_urls'])}")
        print(f"     Business data: {bool(case['business_data'])}")
        print()

if __name__ == "__main__":
    success = test_fallback_categorization()
    test_edge_cases()
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 Fallback categorization test PASSED!")
        print("   The enhanced logic should handle cases when AI fails")
    else:
        print("⚠️  Fallback categorization needs more work")
        print("   Review the failed test cases above")