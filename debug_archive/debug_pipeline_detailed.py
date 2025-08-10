#!/usr/bin/env python3
"""
Comprehensive pipeline debugging to identify where website generation breaks
Focus on finding why we get "major icons, insanely long pages, left-aligned text with 0 UI"
"""
import requests
import json
from app.services.scrape import scrape_site
from app.services.parse import parse_html_sections, SectionData
from app.services.analyze import analyze_sections
from app.services.brand_extraction import extract_brand_identity
from app.services.proportional_sizing import apply_proportional_sizing_to_sections
from app.services.render import render_site_with_brand, prepare_section_for_rendering

def debug_comprehensive_pipeline():
    url = "https://desentopecanalizacoes.pt/"
    print(f"🔍 COMPREHENSIVE PIPELINE DEBUG for {url}")
    print("="*80)
    
    # === PHASE 1: DATA EXTRACTION VERIFICATION ===
    print("\n📋 PHASE 1: DATA EXTRACTION VERIFICATION")
    print("-" * 50)
    
    # Step 1: Scraping
    print("1️⃣ SCRAPING...")
    try:
        scrape_result = scrape_site(url)
        html = scrape_result.pages[0].html
        print(f"   ✅ HTML Length: {len(html):,} characters")
        print(f"   📄 HTML Preview: {html[:150]}...")
        print(f"   🔍 Contains Portuguese: {'Portuguese' if 'português' in html.lower() or 'canalizações' in html.lower() else 'No clear Portuguese content'}")
    except Exception as e:
        print(f"   ❌ SCRAPING FAILED: {e}")
        return
    
    # Step 2: Parsing (DETAILED)
    print("\n2️⃣ PARSING (DETAILED ANALYSIS)...")
    try:
        sections = parse_html_sections(html)
        print(f"   ✅ Created {len(sections)} sections")
        
        for i, section in enumerate(sections):
            print(f"\n   📊 SECTION {i} ANALYSIS:")
            print(f"      • Words: {len(section.text.split())}")
            print(f"      • Characters: {len(section.text)}")
            print(f"      • Images: {len(section.img_urls)}")
            print(f"      • Classes: {section.classes}")
            print(f"      • Heading: '{section.heading}'" if section.heading else "      • No heading")
            print(f"      • Text Preview: {section.text[:100]}..." if section.text else "      • No text")
            
            # Check for potential issues
            issues = []
            if len(section.text.split()) < 10:
                issues.append("Very short text")
            if not section.heading and len(section.text.split()) > 20:
                issues.append("No heading for substantial content")
            if len(section.img_urls) > 5:
                issues.append("Too many images - might cause icon issues")
            
            if issues:
                print(f"      ⚠️  Issues: {', '.join(issues)}")
            else:
                print(f"      ✅ Section looks good")
                
    except Exception as e:
        print(f"   ❌ PARSING FAILED: {e}")
        return
        
    # Convert to dicts for next steps
    section_dicts = [s.__dict__ for s in sections]
    
    # Step 3: Analysis Quality Check
    print("\n3️⃣ ANALYSIS QUALITY CHECK...")
    try:
        analyses = analyze_sections(section_dicts)
        print(f"   ✅ Analyzed {len(analyses)} sections")
        
        category_distribution = {}
        confidence_scores = []
        
        for analysis in analyses:
            cat = analysis.category
            category_distribution[cat] = category_distribution.get(cat, 0) + 1
            confidence = getattr(analysis, 'confidence', 0.5)
            confidence_scores.append(confidence)
            
            print(f"\n   📈 ANALYSIS {analysis.section_id}:")
            print(f"      • Category: {analysis.category}")
            print(f"      • Confidence: {confidence:.2f}")
            print(f"      • Short Copy: {analysis.short_copy[:80]}...")
            print(f"      • Original Text Preview: {analysis.original_text[:80]}...")
            
            # Check for analysis issues
            if confidence < 0.6:
                print(f"      ⚠️  Low confidence classification")
            if analysis.category == "other":
                print(f"      ⚠️  Generic 'other' category - might lack proper UI")
        
        avg_confidence = sum(confidence_scores) / len(confidence_scores)
        print(f"\n   📊 ANALYSIS SUMMARY:")
        print(f"      • Category Distribution: {category_distribution}")
        print(f"      • Average Confidence: {avg_confidence:.2f}")
        print(f"      • Quality Level: {'Good' if avg_confidence > 0.8 else 'Fair' if avg_confidence > 0.6 else 'Poor'}")
        
    except Exception as e:
        print(f"   ❌ ANALYSIS FAILED: {e}")
        return
    
    # === PHASE 2: TEMPLATE SYSTEM INVESTIGATION ===
    print("\n\n🎨 PHASE 2: TEMPLATE SYSTEM INVESTIGATION")  
    print("-" * 50)
    
    # Step 4: Brand Extraction Check
    print("4️⃣ BRAND EXTRACTION CHECK...")
    try:
        brand_identity = extract_brand_identity(url, html)
        print(f"   ✅ Brand identity extracted successfully")
        print(f"   🎨 Primary Color: {brand_identity.colors.primary}")
        print(f"   🎨 Secondary Color: {brand_identity.colors.secondary}")
        print(f"   🎨 Accent Color: {brand_identity.colors.accent}")
        print(f"   📝 Primary Font: {brand_identity.typography.primary_font}")
        print(f"   🏢 Industry: {brand_identity.industry}")
        
        # Check for problematic colors
        problematic = brand_identity.colors.primary.lower() in ['#ffffff', '#fff', 'white']
        print(f"   {'❌ WHITE PRIMARY COLOR - WILL LOOK BAD' if problematic else '✅ Good primary color'}")
        
    except Exception as e:
        print(f"   ❌ BRAND EXTRACTION FAILED: {e}")
        return
    
    # Step 5: Proportional Sizing Application
    print("\n5️⃣ PROPORTIONAL SIZING APPLICATION...")
    try:
        sections_with_sizing = apply_proportional_sizing_to_sections([a.__dict__ for a in analyses])
        print(f"   ✅ Applied proportional sizing to {len(sections_with_sizing)} sections")
        
        for section in sections_with_sizing:
            sizing_info = section.get('sizing', {})
            print(f"   📏 Section {section.get('section_id', 'N/A')}: {section.get('category', 'unknown')} -> {sizing_info.get('section_padding', 'no-padding')}")
            
    except Exception as e:
        print(f"   ❌ SIZING APPLICATION FAILED: {e}")
        return
    
    # Step 6: Template Context Preparation  
    print("\n6️⃣ TEMPLATE CONTEXT PREPARATION...")
    try:
        prepared_sections = []
        for section in sections_with_sizing:
            prepared = prepare_section_for_rendering(section)
            prepared_sections.append(prepared)
            
            print(f"   🔧 Section {prepared.get('section_id', 'N/A')}:")
            print(f"      • Template Context Keys: {list(prepared.keys())}")
            print(f"      • Has Sizing: {'sizing' in prepared}")
            print(f"      • Has Images: {len(prepared.get('img_urls', []))}")
            print(f"      • Has Business Data: {bool(prepared.get('business_data'))}")
            
    except Exception as e:
        print(f"   ❌ TEMPLATE PREPARATION FAILED: {e}")
        return
    
    print("\n🎯 DEBUGGING COMPLETE")
    print("="*80)
    print("Next: Examine template selection and rendering logic...")

if __name__ == "__main__":
    debug_comprehensive_pipeline()