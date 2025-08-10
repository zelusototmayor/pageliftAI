#!/usr/bin/env python3
"""
Test script to verify the template context fix for image_set and typography
"""

import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from app.services.render import prepare_section_for_rendering
    from app.services.typography import create_typography_system
except ImportError as e:
    print(f"Import error: {e}")
    print("This script needs to be run from the project root with dependencies installed")
    sys.exit(1)


def test_prepare_section_with_defaults():
    """Test prepare_section_for_rendering with default parameters"""
    print("🔍 Testing prepare_section_for_rendering with defaults...")
    
    sample_section = {
        'section_id': 0,
        'category': 'hero',
        'heading': 'Test Heading',
        'short_copy': 'Test short copy',
        'original_text': 'Test original text',
        'img_urls': ['https://example.com/image.jpg'],
        'business_data': {
            'phones': ['+351 123 456 789'],
            'emails': ['test@example.com']
        }
    }
    
    # Test with no additional parameters (should use defaults)
    context = prepare_section_for_rendering(sample_section)
    
    print(f"✅ Context keys: {list(context.keys())}")
    
    # Check that image_set and typography are present with defaults
    assert 'image_set' in context, "❌ Missing image_set in context"
    assert 'typography' in context, "❌ Missing typography in context"
    
    image_set = context['image_set']
    print(f"📷 image_set keys: {list(image_set.keys())}")
    assert image_set['primary_image'] is None, "❌ primary_image should be None by default"
    assert isinstance(image_set['all_images'], list), "❌ all_images should be a list"
    
    typography = context['typography']
    print(f"📝 typography keys: {list(typography.keys())}")
    assert 'primary_font' in typography, "❌ Missing primary_font in typography"
    assert 'heading_font' in typography, "❌ Missing heading_font in typography"
    
    print("✅ prepare_section_for_rendering with defaults: PASSED")
    return True


def test_prepare_section_with_brand_identity():
    """Test prepare_section_for_rendering with brand identity"""
    print("\n🔍 Testing prepare_section_for_rendering with brand identity...")
    
    sample_section = {
        'section_id': 0,
        'category': 'hero',
        'heading': 'Test Heading',
        'short_copy': 'Test short copy',
        'img_urls': ['https://via.placeholder.com/800x600.jpg'],
        'business_data': {
            'phones': ['+351 123 456 789'],
            'emails': ['test@example.com']
        }
    }
    
    sample_brand_identity = {
        'colors': {
            'primary': '#0066CC',
            'secondary': '#004499',
            'accent': '#FF6600'
        },
        'typography': {
            'primary_font': 'Inter',
            'heading_font': 'Inter'
        }
    }
    
    # Create typography system
    typography = create_typography_system(sample_brand_identity)
    
    # Test with brand identity and typography
    context = prepare_section_for_rendering(sample_section, sample_brand_identity, typography)
    
    print(f"✅ Context keys: {list(context.keys())}")
    
    # Check that image_set and typography are present with real data
    assert 'image_set' in context, "❌ Missing image_set in context"
    assert 'typography' in context, "❌ Missing typography in context"
    
    image_set = context['image_set']
    print(f"📷 image_set keys: {list(image_set.keys())}")
    
    typography_ctx = context['typography']
    print(f"📝 typography keys: {list(typography_ctx.keys())}")
    print(f"📝 primary_font: {typography_ctx['primary_font']}")
    print(f"📝 heading_font: {typography_ctx['heading_font']}")
    
    print("✅ prepare_section_for_rendering with brand identity: PASSED")
    return True


def test_template_rendering():
    """Test the complete template rendering process"""
    print("\n🔍 Testing complete template rendering process...")
    
    from app.services.render import render_site_with_brand
    
    sample_sections = [{
        'section_id': 0,
        'category': 'hero',
        'heading': 'Professional Services',
        'short_copy': 'Expert solutions for all your needs',
        'original_text': 'Professional Services - Expert solutions for all your needs with 24/7 support.',
        'img_urls': ['https://via.placeholder.com/800x600/0066CC/FFFFFF?text=Hero+Image'],
        'business_data': {
            'phones': ['+351 123 456 789'],
            'emails': ['info@example.com'],
            'ctas': ['Call Now', 'Get Quote']
        },
        'confidence': 0.9,
        'reasoning': 'Clear hero section'
    }]
    
    sample_brand_identity = {
        'brand': {
            'industry': 'professional services',
            'tone': 'professional',
            'name': 'Test Company',
            'description': 'Professional services company'
        },
        'colors': {
            'primary': '#0066CC',
            'secondary': '#004499',
            'accent': '#FF6600',
            'background': '#FFFFFF',
            'text_primary': '#333333',
            'text_secondary': '#666666',
            'success': '#00AA44',
            'error': '#CC0000'
        },
        'typography': {
            'primary_font': 'Inter',
            'secondary_font': 'Inter',
            'heading_font': 'Inter'
        },
        'style': {
            'border_radius': 'rounded-lg',
            'shadow_style': 'modern'
        }
    }
    
    try:
        # Test the complete rendering process
        zip_path = render_site_with_brand(sample_sections, sample_brand_identity, "Test Site")
        print(f"✅ Site rendered successfully to: {zip_path}")
        print("✅ Complete template rendering: PASSED")
        return True
    except Exception as e:
        print(f"❌ Template rendering failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🧪 TESTING TEMPLATE CONTEXT FIXES")
    print("="*50)
    
    tests_passed = 0
    total_tests = 3
    
    try:
        if test_prepare_section_with_defaults():
            tests_passed += 1
    except Exception as e:
        print(f"❌ Test 1 failed: {e}")
    
    try:
        if test_prepare_section_with_brand_identity():
            tests_passed += 1
    except Exception as e:
        print(f"❌ Test 2 failed: {e}")
    
    try:
        if test_template_rendering():
            tests_passed += 1
    except Exception as e:
        print(f"❌ Test 3 failed: {e}")
    
    print(f"\n📊 RESULTS: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED! Template context fix is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Template context fix needs more work.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)