#!/usr/bin/env python3
"""
Content Categorization Test
Tests AI categorization accuracy with sample content
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import json
from typing import List, Dict, Any
from app.services.analyze import analyze_sections

def create_test_sections() -> List[Dict[str, Any]]:
    """Create test sections with clear categorization expectations"""
    
    return [
        {
            "section_id": 1,
            "text": "Welcome to Expert Plumbing Services. Professional plumbing solutions for your home and business needs. Available 24/7 for emergency service. Call now for free estimate!",
            "heading": "Expert Plumbing Services - 24/7 Emergency Service",
            "business_data": {
                "phones": ["+1-555-PLUMBER"],
                "ctas": ["Call Now", "Free Estimate"],
                "emails": []
            },
            "ctas": [{"text": "Call Now", "href": "tel:+15557586237"}],
            "forms": [],
            "img_urls": ["hero-plumber.jpg"],
            "classes": ["hero", "main-banner"],
            "tag": "section",
            "id": "hero-section"
        },
        
        {
            "section_id": 2,
            "text": "About Our Company: With over 15 years of experience serving the local community, our team of licensed and insured plumbers brings expertise and professionalism to every job. We are family-owned and operated, committed to honest pricing and quality workmanship.",
            "heading": "About Our Expert Team",
            "business_data": {
                "phones": [],
                "ctas": [],
                "emails": []
            },
            "ctas": [],
            "forms": [],
            "img_urls": ["team-photo.jpg"],
            "classes": ["about", "company-info"],
            "tag": "section",
            "id": "about-section"
        },
        
        {
            "section_id": 3,
            "text": "Our Services Include: Emergency plumbing repairs, drain cleaning, pipe installation, water heater repair and replacement, bathroom remodeling, kitchen plumbing, commercial plumbing solutions. We handle residential and commercial projects of all sizes.",
            "heading": "Professional Plumbing Services",
            "business_data": {
                "phones": [],
                "ctas": ["Learn More"],
                "emails": []
            },
            "ctas": [{"text": "Learn More", "href": "#contact"}],
            "forms": [],
            "img_urls": ["services-grid.jpg", "plumbing-tools.jpg"],
            "classes": ["services", "service-list"],
            "tag": "section",
            "id": "services-section"
        },
        
        {
            "section_id": 4,
            "text": "Contact Us Today: Ready to solve your plumbing problems? Call us at (555) PLUMBER or email info@expertplumbing.com. We offer free estimates and emergency service 24/7. Located at 123 Main Street, serving all of Metro City.",
            "heading": "Get in Touch",
            "business_data": {
                "phones": ["+1-555-PLUMBER"],
                "emails": ["info@expertplumbing.com"],
                "ctas": ["Call Now", "Get Free Estimate"]
            },
            "ctas": [{"text": "Call Now", "href": "tel:+15557586237"}],
            "forms": [{"id": "contact-form", "fields": ["name", "email", "phone", "message"]}],
            "img_urls": [],
            "classes": ["contact", "contact-info"],
            "tag": "section", 
            "id": "contact-section"
        },
        
        {
            "section_id": 5,
            "text": "Privacy Policy: This website collects information to provide better service. We do not share personal information with third parties. Cookie policy applies to this site.",
            "heading": "Privacy Policy",
            "business_data": {
                "phones": [],
                "emails": [],
                "ctas": []
            },
            "ctas": [],
            "forms": [],
            "img_urls": [],
            "classes": ["footer", "legal"],
            "tag": "footer",
            "id": "privacy-policy"
        }
    ]

def test_categorization_accuracy():
    """Test how accurately the AI categorizes content"""
    
    # Expected results for validation
    expected_categories = {
        1: "hero",      # Clear hero section with company name and CTA
        2: "about",     # About company content
        3: "services",  # List of services offered
        4: "contact",   # Contact information and forms
        5: "other"      # Privacy policy should be "other"
    }
    
    print("🧪 Testing Content Categorization...")
    print("=" * 60)
    
    # Get test sections
    test_sections = create_test_sections()
    
    print(f"📝 Testing with {len(test_sections)} sections:")
    for section in test_sections:
        print(f"   Section {section['section_id']}: {section['heading']}")
    
    print("\n🤖 Running AI analysis...")
    
    try:
        # Run the actual analysis
        results = analyze_sections(test_sections)
        
        print(f"✅ Analysis completed successfully")
        print(f"   Processed {len(results)} sections")
        
        # Analyze results
        print("\n📊 Categorization Results:")
        print("-" * 60)
        
        correct = 0
        total = len(results)
        
        for result in results:
            section_id = int(result.section_id)
            predicted = result.category
            expected = expected_categories.get(section_id, "unknown")
            confidence = getattr(result, 'confidence', 0.0)
            reasoning = getattr(result, 'reasoning', '')
            
            is_correct = predicted == expected
            if is_correct:
                correct += 1
            
            status = "✅" if is_correct else "❌" 
            print(f"{status} Section {section_id}: {predicted} (expected: {expected})")
            print(f"     Confidence: {confidence:.2f}")
            print(f"     Reasoning: {reasoning[:100]}...")
            print()
        
        # Summary
        accuracy = (correct / total) * 100
        print("=" * 60)
        print(f"🎯 Categorization Accuracy: {correct}/{total} ({accuracy:.1f}%)")
        
        if accuracy >= 80:
            print("🎉 EXCELLENT: Categorization is working well!")
        elif accuracy >= 60:
            print("⚠️  GOOD: Categorization is mostly working, minor improvements needed")
        else:
            print("❌ POOR: Categorization needs significant improvement")
        
        # Category distribution
        category_counts = {}
        confidence_sum = 0
        for result in results:
            cat = result.category
            category_counts[cat] = category_counts.get(cat, 0) + 1
            confidence_sum += getattr(result, 'confidence', 0.5)
        
        avg_confidence = confidence_sum / len(results)
        
        print(f"\n📈 Category Distribution:")
        for category, count in category_counts.items():
            print(f"   {category}: {count} sections")
        
        print(f"\n🎪 Average Confidence: {avg_confidence:.2f}")
        
        return accuracy >= 80
        
    except Exception as e:
        print(f"❌ Categorization test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_edge_cases():
    """Test categorization with edge cases and ambiguous content"""
    
    edge_cases = [
        {
            "section_id": 101,
            "text": "Call us now! Get expert plumbing service today. About our services: we do everything from repairs to installations. Contact us for pricing information.",
            "heading": "Mixed Content Section",
            "business_data": {"phones": ["+1-555-1234"], "ctas": ["Call Now"], "emails": []},
            "ctas": [{"text": "Call Now"}],
            "forms": [],
            "img_urls": [],
            "classes": ["mixed"],
            "tag": "div",
            "id": "mixed-section"
        },
        
        {
            "section_id": 102, 
            "text": "",  # Empty content
            "heading": "",
            "business_data": {"phones": [], "ctas": [], "emails": []},
            "ctas": [],
            "forms": [],
            "img_urls": ["image.jpg"],
            "classes": [],
            "tag": "div",
            "id": "empty-section"
        }
    ]
    
    print("\n🧪 Testing Edge Cases...")
    print("=" * 60)
    
    try:
        results = analyze_sections(edge_cases)
        
        print("Edge Case Results:")
        for result in results:
            print(f"   Section {result.section_id}: {result.category}")
            print(f"     Confidence: {getattr(result, 'confidence', 0.0):.2f}")
            print(f"     Reasoning: {getattr(result, 'reasoning', 'No reasoning')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Edge case test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success1 = test_categorization_accuracy()
    success2 = test_edge_cases()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 All categorization tests PASSED!")
    else:
        print("⚠️  Some categorization tests FAILED - review results above")