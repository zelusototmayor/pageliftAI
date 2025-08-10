#!/usr/bin/env python3
"""
Debug specific test failures
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.services.analyze import determine_fallback_category

# Test 6: Privacy policy
privacy_test = {
    "section_id": 8,
    "text": "Privacy Policy: This website collects information to provide better service. We respect your privacy and do not share personal information with third parties. Cookie policy applies.",
    "heading": "Privacy Policy",
    "business_data": {"phones": [], "ctas": [], "emails": []},
    "classes": ["footer", "legal"],
    "id": "privacy-policy",
    "img_urls": [],
}

# Test 8: Mixed content
mixed_test = {
    "section_id": 1,
    "text": "Professional quality service. About our team: we provide expert solutions. Contact us today for services.",
    "heading": "Mixed Content Section",
    "business_data": {"phones": [], "ctas": ["Contact"], "emails": []},
    "classes": ["mixed"],
    "id": "mixed-section",
    "img_urls": [],
}

# Test 9: Portuguese content
portuguese_test = {
    "section_id": 2,
    "text": "Sobre nossa empresa: Com mais de 15 anos de experiência, nossa equipa de profissionais licenciados traz expertise para cada trabalho. Somos uma empresa familiar, comprometida com preços honestos.",
    "heading": "Sobre Nossa Equipa",
    "business_data": {"phones": [], "ctas": [], "emails": []},
    "classes": ["sobre", "empresa"],
    "id": "sobre-secao",
    "img_urls": ["equipa.jpg"],
}

tests = [
    ("Privacy Policy", privacy_test, "other"),
    ("Mixed Content", mixed_test, "hero"),
    ("Portuguese About", portuguese_test, "about")
]

for name, test_case, expected in tests:
    print(f"🔍 Debug {name}")
    print("=" * 50)
    
    text = str(test_case.get("text") or "").lower()
    heading = str(test_case.get("heading") or "").lower()
    section_classes = " ".join(test_case.get("classes", [])).lower()
    section_id = str(test_case.get("id", "")).lower()
    combined_text = text + " " + heading + " " + section_classes + " " + section_id
    
    print(f"Position: {test_case['section_id']}")
    print(f"Combined: {combined_text[:100]}...")
    print(f"Business data: {test_case['business_data']}")
    
    # Check for specific keywords
    print(f"\nKeyword checks:")
    print(f"'policy' in text: {'policy' in combined_text}")
    print(f"'legal' in text: {'legal' in combined_text}")
    print(f"'privacy' in text: {'privacy' in combined_text}")
    print(f"'sobre' in text: {'sobre' in combined_text}")
    print(f"'team' in text: {'team' in combined_text}")
    print(f"'equipa' in text: {'equipa' in combined_text}")
    
    result = determine_fallback_category(test_case)
    print(f"\nResult: {result}")
    print(f"Expected: {expected}")
    print(f"Match: {'✅' if result == expected else '❌'}")
    print()