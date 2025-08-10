#!/usr/bin/env python3
"""
Debug mixed content specifically
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.services.analyze import determine_fallback_category

# Mixed content test
mixed_test = {
    "section_id": 1,
    "text": "Professional quality service. About our team: we provide expert solutions. Contact us today for services.",
    "heading": "Mixed Content Section",
    "business_data": {"phones": [], "ctas": ["Contact"], "emails": []},
    "classes": ["mixed"],
    "id": "mixed-section",
    "img_urls": [],
}

print("🔍 Debug Mixed Content Issue")
print("=" * 50)

text = str(mixed_test.get("text") or "").lower()
heading = str(mixed_test.get("heading") or "").lower()
section_classes = " ".join(mixed_test.get("classes", [])).lower()
section_id = str(mixed_test.get("id", "")).lower()
combined_text = text + " " + heading + " " + section_classes + " " + section_id

print(f"Position: {mixed_test['section_id']}")
print(f"Text: {text}")
print(f"Combined: {combined_text}")

# Check hero keywords
hero_keywords = {
    # English
    "welcome", "leading", "best", "top", "quality", "trusted", "professional", "expert",
    "choose", "why", "premier", "excellence", "outstanding", "reliable", "experienced",
}

# Check contact keywords
contact_keywords = {
    # English
    "contact", "phone", "email", "address", "location", "call", "reach", "get in touch",
    "telephone", "mobile", "fax", "office", "hours", "schedule", "appointment",
}

hero_matches = [keyword for keyword in hero_keywords if keyword in combined_text]
contact_matches = [keyword for keyword in contact_keywords if keyword in combined_text]

print(f"\nHero matches: {hero_matches}")
print(f"Hero count: {len(hero_matches)}")
print(f"Contact matches: {contact_matches}")
print(f"Contact count: {len(contact_matches)}")

print(f"\nCondition checks:")
print(f"section_id <= 1: {mixed_test['section_id'] <= 1}")
print(f"has hero keywords: {len(hero_matches) >= 1}")
print(f"has contact keywords: {len(contact_matches) >= 1}")
print(f"Business phones/emails: {mixed_test['business_data'].get('phones')} / {mixed_test['business_data'].get('emails')}")

result = determine_fallback_category(mixed_test)
print(f"\nResult: {result}")
print(f"Expected: hero")