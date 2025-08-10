#!/usr/bin/env python3
"""
Quick test of brand color extraction improvements
"""
import requests
from app.services.brand_extraction import extract_brand_identity

def test_colors():
    url = "https://desentopecanalizacoes.pt/"
    print(f"Testing brand color extraction for {url}")
    
    # Fetch HTML
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
    response = requests.get(url, headers=headers, timeout=15)
    html = response.text
    
    # Extract brand identity
    brand_identity = extract_brand_identity(url, html)
    
    print(f"Results:")
    print(f"  Primary: {brand_identity.colors.primary}")
    print(f"  Secondary: {brand_identity.colors.secondary}")  
    print(f"  Accent: {brand_identity.colors.accent}")
    
    # Check if primary is still white/neutral
    is_bad_primary = brand_identity.colors.primary.lower() in ['#ffffff', '#fff', 'white']
    print(f"  Primary is white: {'YES (❌ BAD)' if is_bad_primary else 'NO (✅ GOOD)'}")

if __name__ == "__main__":
    test_colors()