#!/usr/bin/env python3
"""
Debug hero detection specifically
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.services.analyze import determine_fallback_category

# Test case that should be hero but is detected as services
hero_test = {
    "section_id": 0,  # First section
    "text": "Welcome to Expert Plumbing Services. Professional plumbing solutions for your home and business needs. Leading provider in the area.",
    "heading": "Expert Plumbing Services - Professional Quality",
    "business_data": {"phones": ["+1-555-PLUMBER"], "ctas": ["Call Now"], "emails": []},
    "classes": ["hero", "main-banner"],
    "id": "hero-section",
    "img_urls": ["hero.jpg"],
}

print("🔍 Debug Hero Detection")
print("=" * 50)

# Check individual conditions
text = str(hero_test.get("text") or "").lower()
heading = str(hero_test.get("heading") or "").lower()
section_classes = " ".join(hero_test.get("classes", [])).lower()
section_id = str(hero_test.get("id", "")).lower()
combined_text = text + " " + heading + " " + section_classes + " " + section_id

print(f"Section ID: {hero_test['section_id']}")
print(f"Combined text: {combined_text[:100]}...")

# Check hero keywords
hero_keywords = {
    # English
    "welcome", "leading", "best", "top", "quality", "trusted", "professional", "expert",
    "choose", "why", "premier", "excellence", "outstanding", "reliable", "experienced",
    # Portuguese  
    "bem-vindo", "bem-vindos", "líder", "melhor", "qualidade", "confiança", "profissional",
    "especialista", "escolher", "porquê", "excelência", "excepcional", "fiável", 
    "experiente", "confiável", "anos de experiência"
}

print(f"\nHero keyword matches:")
hero_matches = [keyword for keyword in hero_keywords if keyword in combined_text]
print(f"Found: {hero_matches}")
print(f"Count: {len(hero_matches)}")

print(f"\nClass hints:")
print(f"'hero' in combined_text: {'hero' in combined_text}")
print(f"'banner' in combined_text: {'banner' in combined_text}")
print(f"'main' in combined_text: {'main' in combined_text}")

# Check services keywords
services_keywords = {
    # English
    "services", "service", "solutions", "repairs", "installation", "maintenance",
    "repair", "install", "fix", "replace", "cleaning", "emergency", "plumbing", 
    "electrical", "hvac", "construction", "residential", "commercial",
    # Portuguese
    "serviços", "serviço", "soluções", "reparações", "instalação", "manutenção",
    "reparar", "instalar", "consertar", "substituir", "limpeza", "emergência",
    "canalizador", "eletricista", "aquecimento", "construção", "residencial", "comercial"
}

print(f"\nServices keyword matches:")
services_matches = [keyword for keyword in services_keywords if keyword in combined_text]
print(f"Found: {services_matches}")
print(f"Count: {len(services_matches)}")

# Test the actual function
result = determine_fallback_category(hero_test)
print(f"\nActual result: {result}")
print(f"Expected: hero")
print(f"Match: {'✅' if result == 'hero' else '❌'}")