#!/usr/bin/env python3
"""
Test script to validate fallback strategies with synthetic edge cases
"""
import sys
import os
sys.path.insert(0, '/app')

from app.services.analyze import (
    analyze_sections, 
    apply_progressive_classification,
    create_mixed_content_section,
    apply_content_splitting_strategy,
    SectionAnalysis
)

def test_progressive_classification():
    """Test progressive classification with uncertain content"""
    print("\n🧪 TESTING PROGRESSIVE CLASSIFICATION")
    
    # Create a section with mixed signals
    test_analysis = SectionAnalysis(
        section_id=1,
        category="other",
        short_copy="Mixed content section",
        original_text="Our company has years of experience in professional services. Contact us for expert solutions. We offer comprehensive support.",
        heading="Professional Services",
        img_urls=[],
        classes=[],
        id="test1"
    )
    
    # Apply progressive classification
    result = apply_progressive_classification(test_analysis)
    
    print(f"✅ Original category: other")
    print(f"✅ Progressive result: {result.category}")
    print(f"✅ Confidence: {result.confidence:.2f}")
    print(f"✅ Reasoning: {result.reasoning}")
    
    return result.category != "other"

def test_mixed_content_creation():
    """Test mixed content section creation"""
    print("\n🧪 TESTING MIXED CONTENT CREATION")
    
    test_analysis = SectionAnalysis(
        section_id=2,
        category="other",
        short_copy="Uncertain content",
        original_text="Content that could be multiple categories",
        heading="Mixed Section",
        img_urls=[],
        classes=[],
        id="test2"
    )
    
    # Create mixed content
    potential_categories = ["hero", "about", "services"]
    result = create_mixed_content_section(test_analysis, potential_categories)
    
    print(f"✅ Mixed category: {result.category}")
    print(f"✅ Confidence: {result.confidence:.2f}")
    print(f"✅ Is hybrid: {getattr(result, 'is_hybrid', False)}")
    print(f"✅ Hybrid categories: {getattr(result, 'hybrid_categories', [])}")
    
    return "_mixed" in result.category

def test_content_splitting():
    """Test content splitting for large uncertain sections"""
    print("\n🧪 TESTING CONTENT SPLITTING")
    
    # Create a large section with mixed content
    large_text = """
    Welcome to our professional business services company. We have been providing excellent solutions for over 20 years with experienced teams.
    
    About our company: We specialize in comprehensive business solutions and have built a reputation for reliability and expertise. Our team consists of certified professionals.
    
    Our services include consulting, implementation, and ongoing support. We offer customized solutions for businesses of all sizes and industries.
    
    Contact us today for a free consultation. Call us at 123-456-7890 or email info@company.com. We are available 24/7 to assist you with your needs.
    
    Additional information about our policies, terms of service, and privacy policy can be found on our website. We are committed to transparency and customer satisfaction.
    """ * 3  # Make it very long
    
    test_analysis = SectionAnalysis(
        section_id=3,
        category="other",
        short_copy="Large mixed content",
        original_text=large_text,
        heading="Company Information",
        img_urls=[],
        classes=[],
        id="test3"
    )
    
    # Set low confidence to trigger splitting
    test_analysis.confidence = 0.3
    
    # Apply content splitting
    result = apply_content_splitting_strategy(test_analysis)
    
    print(f"✅ Original sections: 1")
    print(f"✅ Split sections: {len(result)}")
    print(f"✅ Section IDs: {[s.section_id for s in result]}")
    
    for i, section in enumerate(result):
        print(f"   Sub-section {i}: {section.category} (confidence: {getattr(section, 'confidence', 0.5):.2f})")
    
    return len(result) > 1

def test_synthetic_challenging_content():
    """Test with synthetic challenging content that should trigger fallbacks"""
    print("\n🧪 TESTING SYNTHETIC CHALLENGING CONTENT")
    
    # Create sections that should challenge the system
    challenging_sections = [
        {
            'section_id': 0,
            'text': 'Welcome business professional expert solutions company services',  # Very short, mixed signals
            'heading': '',
            'img_urls': [],
            'strategy': 'test',
            'priority': 1,
            'business_data': {},
            'ctas': [],
            'forms': [],
            'tag': 'div',
            'classes': [],
            'id': 'challenge1'
        },
        {
            'section_id': 1,
            'text': 'Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua ut enim ad minim veniam quis nostrud exercitation ullamco',  # Lorem ipsum - should be very uncertain
            'heading': 'Lorem Ipsum',
            'img_urls': [],
            'strategy': 'test',
            'priority': 1,
            'business_data': {},
            'ctas': [],
            'forms': [],
            'tag': 'div',
            'classes': [],
            'id': 'challenge2'
        },
        {
            'section_id': 2,
            'text': 'a b c d e f g h i j k l m n o p q r s t u v w x y z',  # Nonsensical content
            'heading': 'Random',
            'img_urls': [],
            'strategy': 'test',
            'priority': 1,
            'business_data': {},
            'ctas': [],
            'forms': [],
            'tag': 'div',
            'classes': [],
            'id': 'challenge3'
        }
    ]
    
    # Run analysis
    analyses = analyze_sections(challenging_sections)
    
    # Check results
    fallback_strategies_used = 0
    other_count = 0
    low_confidence_count = 0
    
    for analysis in analyses:
        confidence = getattr(analysis, 'confidence', 0.5)
        reasoning = getattr(analysis, 'reasoning', '')
        
        if analysis.category == "other":
            other_count += 1
        
        if confidence < 0.6:
            low_confidence_count += 1
        
        if ('Progressive classification' in reasoning or 
            '_mixed' in analysis.category or
            getattr(analysis, 'is_hybrid', False)):
            fallback_strategies_used += 1
        
        print(f"✅ Section {analysis.section_id}: {analysis.category} (confidence: {confidence:.2f})")
        print(f"   Reasoning: {reasoning[:100]}...")
    
    print(f"\n📊 CHALLENGING CONTENT RESULTS:")
    print(f"   Fallback strategies used: {fallback_strategies_used}/{len(analyses)}")
    print(f"   'Other' classifications: {other_count}/{len(analyses)}")
    print(f"   Low confidence sections: {low_confidence_count}/{len(analyses)}")
    
    # Success: at least some fallback strategies were used, not everything is "other"
    success = (fallback_strategies_used > 0 or other_count < len(analyses))
    return success

def main():
    print("🚀 TESTING FALLBACK STRATEGIES - EDGE CASES")
    
    test_results = []
    
    # Test progressive classification
    test_results.append(test_progressive_classification())
    
    # Test mixed content creation
    test_results.append(test_mixed_content_creation())
    
    # Test content splitting
    test_results.append(test_content_splitting())
    
    # Test synthetic challenging content
    test_results.append(test_synthetic_challenging_content())
    
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    print(f"\n🏁 FALLBACK EDGE CASE TESTS SUMMARY:")
    print(f"   Tests passed: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("✅ All fallback strategy edge case tests PASSED!")
        return True
    else:
        print("❌ Some fallback strategy edge case tests FAILED!")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)