#!/usr/bin/env python3
"""
Test script to validate enhanced semantic categorization
"""
import sys
import os
sys.path.insert(0, '/app')

from app.services.scrape import extract_sections
from app.services.analyze import analyze_sections
import requests
import json

def test_categorization(url):
    print(f"Testing semantic categorization on: {url}")
    
    try:
        # Fetch the webpage
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        print(f"✅ Successfully fetched HTML ({len(response.text)} characters)")
        
        # Extract sections using enhanced logic
        sections = extract_sections(response.text, url)
        
        print(f"\n📊 EXTRACTION RESULTS:")
        print(f"Total sections extracted: {len(sections)}")
        
        # Convert Section objects to dictionaries for analysis
        sections_data = []
        for section in sections:
            section_dict = {
                'section_id': section.section_id,
                'text': section.text,
                'heading': section.heading,
                'img_urls': section.img_urls,
                'strategy': section.strategy,
                'priority': section.priority,
                'business_data': section.business_data,
                'ctas': section.ctas,
                'forms': section.forms,
                'tag': section.tag,
                'classes': section.classes,
                'id': section.id
            }
            sections_data.append(section_dict)
        
        print(f"\n🤖 RUNNING SEMANTIC CATEGORIZATION...")
        
        # Run semantic categorization
        analyses = analyze_sections(sections_data)
        
        print(f"\n📋 CATEGORIZATION RESULTS:")
        print(f"Total sections analyzed: {len(analyses)}")
        
        # Count categories
        category_counts = {}
        total_confidence = 0
        other_count = 0
        
        for analysis in analyses:
            category = analysis.category
            category_counts[category] = category_counts.get(category, 0) + 1
            
            confidence = getattr(analysis, 'confidence', 0.5)
            total_confidence += confidence
            
            if category == "other":
                other_count += 1
        
        avg_confidence = total_confidence / len(analyses) if analyses else 0
        other_percentage = (other_count / len(analyses) * 100) if analyses else 0
        
        print(f"\n📈 CATEGORY DISTRIBUTION:")
        for category, count in sorted(category_counts.items()):
            percentage = (count / len(analyses) * 100) if analyses else 0
            print(f"  {category.upper()}: {count} sections ({percentage:.1f}%)")
        
        print(f"\n📊 QUALITY METRICS:")
        print(f"Average confidence: {avg_confidence:.2f}")
        print(f"'Other' percentage: {other_percentage:.1f}%")
        
        # Detailed section analysis
        print(f"\n🔍 DETAILED SECTION ANALYSIS:")
        hybrid_count = 0
        for analysis in analyses:
            confidence = getattr(analysis, 'confidence', 0.5)
            reasoning = getattr(analysis, 'reasoning', 'No reasoning provided')
            is_hybrid = getattr(analysis, 'is_hybrid', False)
            hybrid_categories = getattr(analysis, 'hybrid_categories', [])
            
            if is_hybrid:
                hybrid_count += 1
            
            print(f"\nSection {analysis.section_id}: {analysis.category.upper()}")
            print(f"  Confidence: {confidence:.2f}")
            if is_hybrid:
                print(f"  🔄 HYBRID CONTENT - Alternative categories: {', '.join(hybrid_categories)}")
            print(f"  Heading: {analysis.heading[:50]}..." if analysis.heading else "  Heading: None")
            print(f"  Content: {analysis.original_text[:100]}..." if analysis.original_text else "  Content: None")
            print(f"  Short Copy: {analysis.short_copy[:100]}..." if analysis.short_copy else "  Short Copy: None")
            print(f"  Reasoning: {reasoning}")
        
        print(f"\n🔄 HYBRID CATEGORIZATION:")
        print(f"Sections with multiple category potential: {hybrid_count}/{len(analyses)} ({hybrid_count/len(analyses)*100:.1f}%)")
        
        # Success criteria: less than 50% "other" classifications
        success = other_percentage < 50 and avg_confidence > 0.6
        
        print(f"\n{'✅' if success else '❌'} CATEGORIZATION TEST {'PASSED' if success else 'FAILED'}")
        print(f"Success criteria: <50% 'other' ({other_percentage:.1f}%), >0.6 confidence ({avg_confidence:.2f})")
        
        return success
        
    except Exception as e:
        print(f"❌ Error testing categorization: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Test on the problematic site
    success = test_categorization("https://desentopecanalizacoes.pt/")
    
    if success:
        print("\n🎉 Semantic categorization test PASSED!")
    else:
        print("\n💥 Semantic categorization test FAILED!")
        sys.exit(1)