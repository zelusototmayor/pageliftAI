#!/usr/bin/env python3
"""
Debug which keywords are matching
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Copy the keyword sets from analyze.py to debug
hero_keywords = {
    # English
    "welcome", "leading", "best", "top", "quality", "trusted", "professional", "expert",
    "choose", "why", "premier", "excellence", "outstanding", "reliable", "experienced",
    # Portuguese  
    "bem-vindo", "bem-vindos", "líder", "melhor", "qualidade", "confiança", "profissional",
    "especialista", "escolher", "porquê", "excelência", "excepcional", "fiável", 
    "experiente", "confiável", "anos de experiência"
}

contact_keywords = {
    # English
    "contact", "phone", "email", "address", "location", "call", "reach", "get in touch",
    "telephone", "mobile", "fax", "office", "hours", "schedule", "appointment",
    # Portuguese  
    "contacto", "contato", "telefone", "email", "morada", "endereço", "localização",
    "ligar", "contactar", "horário", "horarios", "marcação", "agendamento",
    "escritório", "gabinete", "atendimento", "fale connosco", "fale conosco",
}

# Test text
test_text = "contact us today for all your plumbing needs. call us at (555) plumber or email info@expertplumbing.com. located at 123 main street. we offer free estimates and 24/7 emergency service. get in touch contact contact-info contact-section"

print("🔍 Keyword Matching Debug")
print("=" * 50)

print("Hero keyword matches:")
hero_matches = [keyword for keyword in hero_keywords if keyword in test_text]
print(f"Found: {hero_matches}")

print("\nContact keyword matches:")
contact_matches = [keyword for keyword in contact_keywords if keyword in test_text]  
print(f"Found: {contact_matches}")

print(f"\nHero matches: {len(hero_matches)}")
print(f"Contact matches: {len(contact_matches)}")

# Test the has_keywords function logic
def has_keywords(keyword_set, minimum_matches=1):
    """Check if text contains keywords from the set"""
    matches = sum(1 for keyword in keyword_set if keyword in test_text)
    return matches >= minimum_matches

print(f"\nhas_keywords(hero_keywords, 1): {has_keywords(hero_keywords, 1)}")
print(f"has_keywords(contact_keywords, 1): {has_keywords(contact_keywords, 1)}")