#!/usr/bin/env python3
"""
Debug categorization to understand why class matching isn't working
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.services.analyze import determine_fallback_category

# Test the contact case that's failing
contact_test = {
    "section_id": 5,
    "text": "Contact us today for all your plumbing needs. Call us at (555) PLUMBER or email info@expertplumbing.com. Located at 123 Main Street. We offer free estimates and 24/7 emergency service.",
    "heading": "Get in Touch",
    "business_data": {"phones": ["+1-555-PLUMBER"], "emails": ["info@expertplumbing.com"], "ctas": ["Call Now"]},
    "classes": ["contact", "contact-info"],
    "id": "contact-section",
    "img_urls": [],
}

print("🔍 Debug Contact Test Case")
print("=" * 50)

# Debug what the function sees
text = str(contact_test.get("text") or "").lower()
heading = str(contact_test.get("heading") or "").lower()
section_classes = " ".join(contact_test.get("classes", [])).lower()
section_id = str(contact_test.get("id", "")).lower()
combined_text = text + " " + heading + " " + section_classes + " " + section_id

print(f"Text: {text[:100]}...")
print(f"Heading: {heading}")
print(f"Classes: {section_classes}")
print(f"ID: {section_id}")
print(f"Combined: {combined_text[:200]}...")

# Check if "contact" is in combined text
print(f"\nClass Detection:")
print(f"'contact' in combined_text: {'contact' in combined_text}")
print(f"'touch' in combined_text: {'touch' in combined_text}")
print(f"'reach' in combined_text: {'reach' in combined_text}")
print(f"'footer' in combined_text: {'footer' in combined_text}")

# Check business data
print(f"\nBusiness Data:")
print(f"Phones: {contact_test['business_data'].get('phones')}")
print(f"Emails: {contact_test['business_data'].get('emails')}")

# Run the categorization
result = determine_fallback_category(contact_test)
print(f"\nResult: {result}")

print("\n" + "=" * 50)

# Test the gallery case
gallery_test = {
    "section_id": 4,
    "text": "See our work in action. Here are some examples of recent plumbing projects completed by our expert team. Customer testimonials and before/after photos showcase our quality workmanship.",
    "heading": "Our Work Gallery",
    "business_data": {"phones": [], "ctas": [], "emails": []},
    "classes": ["gallery", "portfolio"],
    "id": "gallery-section",
    "img_urls": ["before1.jpg", "after1.jpg", "project2.jpg", "testimonial.jpg"],
}

print("🔍 Debug Gallery Test Case")
print("=" * 50)

text = str(gallery_test.get("text") or "").lower()
heading = str(gallery_test.get("heading") or "").lower()
section_classes = " ".join(gallery_test.get("classes", [])).lower()
section_id = str(gallery_test.get("id", "")).lower()
combined_text = text + " " + heading + " " + section_classes + " " + section_id

print(f"Text: {text[:100]}...")
print(f"Heading: {heading}")
print(f"Classes: {section_classes}")
print(f"ID: {section_id}")
print(f"Combined: {combined_text[:200]}...")

print(f"\nClass Detection:")
print(f"'gallery' in combined_text: {'gallery' in combined_text}")
print(f"'portfolio' in combined_text: {'portfolio' in combined_text}")
print(f"'showcase' in combined_text: {'showcase' in combined_text}")

print(f"\nImages: {len(gallery_test['img_urls'])} images")

result = determine_fallback_category(gallery_test)
print(f"\nResult: {result}")