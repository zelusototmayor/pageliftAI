#!/usr/bin/env python3
"""
Debug script to test the entire website generation pipeline step by step
"""
import requests
import json
from app.services.scrape import scrape_site
from app.services.parse import parse_html_sections
from app.services.analyze import analyze_sections
from app.services.brand_extraction import extract_brand_identity

def test_pipeline():
    url = "https://desentopecanalizacoes.pt/"
    print(f"=== Testing Pipeline for {url} ===\n")
    
    # Step 1: Test Scraping
    print("1. SCRAPING...")
    try:
        scrape_result = scrape_site(url)
        html = scrape_result.pages[0].html
        print(f"✅ HTML fetched: {len(html)} characters")
        print(f"HTML preview: {html[:200]}...")
        has_html = True
    except Exception as e:
        print(f"❌ Scraping failed: {e}")
        return
        
    # Step 2: Test Parsing  
    print("\n2. PARSING...")
    try:
        sections = parse_html_sections(html)
        section_dicts = [s.__dict__ for s in sections]
        print(f"✅ Parsed {len(sections)} sections")
        for i, section in enumerate(sections):
            print(f"  Section {i}: {len(section.text.split())} words, {len(section.img_urls)} images")
    except Exception as e:
        print(f"❌ Parsing failed: {e}")
        return
        
    # Step 3: Test Analysis
    print("\n3. ANALYSIS...")
    try:
        analyses = analyze_sections(section_dicts)
        print(f"✅ Analyzed {len(analyses)} sections")
        for analysis in analyses:
            confidence = getattr(analysis, 'confidence', 'N/A')
            print(f"  Section {analysis.section_id}: {analysis.category} (confidence: {confidence})")
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return
        
    # Step 4: Test Brand Extraction
    print("\n4. BRAND EXTRACTION...")
    try:
        brand_identity = extract_brand_identity(url, html)
        print(f"✅ Brand identity extracted")
        print(f"  Primary color: {brand_identity.colors.primary}")
        print(f"  Secondary color: {brand_identity.colors.secondary}")
        print(f"  Accent color: {brand_identity.colors.accent}")
        print(f"  Primary font: {brand_identity.typography.primary_font}")
        print(f"  Industry: {brand_identity.industry}")
        print(f"  Tone: {brand_identity.tone}")
        
        # Check if these are defaults
        is_default = (brand_identity.colors.primary == "#3B82F6" and 
                     brand_identity.colors.secondary == "#64748B")
        print(f"  Using defaults: {'YES (❌ PROBLEM!)' if is_default else 'NO (✅ GOOD)'}")
        
    except Exception as e:
        print(f"❌ Brand extraction failed: {e}")
        return
        
    print("\n=== Pipeline Test Complete ===")

if __name__ == "__main__":
    test_pipeline()