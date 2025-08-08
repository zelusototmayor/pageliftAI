#!/usr/bin/env python3
"""
Test script to validate fallback strategies for uncertain content
"""
import sys
import os
sys.path.insert(0, '/app')

from app.services.scrape import extract_sections
from app.services.analyze import analyze_sections
import requests
import json

def test_fallback_strategies(url):
    print(f"Testing fallback strategies on: {url}")
    
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
        
        print(f"\n🤖 RUNNING SEMANTIC CATEGORIZATION WITH FALLBACK STRATEGIES...")
        
        # Run semantic categorization
        analyses = analyze_sections(sections_data)
        
        print(f"\n📋 CATEGORIZATION RESULTS:")
        print(f"Total sections analyzed: {len(analyses)}")
        
        # Count categories and analyze fallback effectiveness
        category_counts = {}
        confidence_levels = {'high': 0, 'medium': 0, 'low': 0}
        mixed_content_count = 0
        progressive_classification_count = 0
        content_splitting_count = 0
        
        for analysis in analyses:
            category = analysis.category
            category_counts[category] = category_counts.get(category, 0) + 1
            
            confidence = getattr(analysis, 'confidence', 0.5)
            reasoning = getattr(analysis, 'reasoning', '')
            
            # Classify confidence levels
            if confidence >= 0.8:
                confidence_levels['high'] += 1
            elif confidence >= 0.6:
                confidence_levels['medium'] += 1
            else:
                confidence_levels['low'] += 1
            
            # Check for fallback strategy usage
            if '_mixed' in category:
                mixed_content_count += 1
            if 'Progressive classification' in reasoning:
                progressive_classification_count += 1
            if '.' in str(analysis.section_id):  # Fractional IDs indicate content splitting
                content_splitting_count += 1
        
        avg_confidence = sum(getattr(analysis, 'confidence', 0.5) for analysis in analyses) / len(analyses)
        other_count = category_counts.get('other', 0)
        other_percentage = (other_count / len(analyses) * 100) if analyses else 0
        
        print(f"\n📈 CATEGORY DISTRIBUTION:")
        for category, count in sorted(category_counts.items()):
            percentage = (count / len(analyses) * 100) if analyses else 0
            print(f"  {category.upper()}: {count} sections ({percentage:.1f}%)")
        
        print(f"\n📊 CONFIDENCE DISTRIBUTION:")
        print(f"  High (≥0.8): {confidence_levels['high']} sections")
        print(f"  Medium (0.6-0.8): {confidence_levels['medium']} sections")
        print(f"  Low (<0.6): {confidence_levels['low']} sections")
        print(f"  Average confidence: {avg_confidence:.2f}")
        
        print(f"\n🔧 FALLBACK STRATEGY USAGE:")
        print(f"  Mixed content sections: {mixed_content_count}")
        print(f"  Progressive classifications: {progressive_classification_count}")
        print(f"  Content splitting applied: {content_splitting_count}")
        
        print(f"\n🎯 QUALITY METRICS:")
        print(f"  'Other' percentage: {other_percentage:.1f}%")
        print(f"  Sections with low confidence: {confidence_levels['low']}")
        print(f"  Fallback strategies activated: {mixed_content_count + progressive_classification_count + content_splitting_count}")
        
        # Detailed analysis of problematic sections
        print(f"\n🔍 DETAILED FALLBACK ANALYSIS:")
        for analysis in analyses:
            confidence = getattr(analysis, 'confidence', 0.5)
            reasoning = getattr(analysis, 'reasoning', 'No reasoning provided')
            is_hybrid = getattr(analysis, 'is_hybrid', False)
            
            # Only show sections that used fallback strategies
            if (confidence < 0.6 or '_mixed' in analysis.category or 
                'Progressive classification' in reasoning or is_hybrid):
                
                print(f"\nSection {analysis.section_id}: {analysis.category.upper()}")
                print(f"  ⚠️  FALLBACK APPLIED - Confidence: {confidence:.2f}")
                if is_hybrid:
                    hybrid_categories = getattr(analysis, 'hybrid_categories', [])
                    print(f"  🔄 Hybrid content - Categories: {', '.join(hybrid_categories)}")
                print(f"  Content: {analysis.original_text[:100]}...")
                print(f"  Strategy: {reasoning}")
        
        # Success criteria: robust handling of uncertain content
        success = (
            other_percentage < 50 and  # Less than 50% "other"
            avg_confidence > 0.5 and  # Reasonable average confidence
            confidence_levels['low'] < len(analyses) * 0.4  # Less than 40% low confidence
        )
        
        print(f"\n{'✅' if success else '❌'} FALLBACK STRATEGIES TEST {'PASSED' if success else 'FAILED'}")
        print(f"Success criteria: <50% 'other' ({other_percentage:.1f}%), >0.5 confidence ({avg_confidence:.2f}), <40% low confidence ({confidence_levels['low']}/{len(analyses)})")
        
        return success
        
    except Exception as e:
        print(f"❌ Error testing fallback strategies: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Test with the original problematic site
    print("=== TESTING ORIGINAL SITE ===")
    success1 = test_fallback_strategies("https://desentopecanalizacoes.pt/")
    
    # Test with a more complex business website
    print("\n\n=== TESTING COMPLEX WEBSITE ===")
    success2 = test_fallback_strategies("https://httpbin.org/html")
    
    overall_success = success1 and success2
    
    if overall_success:
        print("\n🎉 All fallback strategy tests PASSED!")
    else:
        print("\n💥 Some fallback strategy tests FAILED!")
        sys.exit(1)