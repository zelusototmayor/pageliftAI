#!/usr/bin/env python3
"""
Template Rendering Test Utility
Tests if templates render properly with sample data
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import Dict, Any

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), '../templates')

def create_sample_brand_identity() -> Dict[str, Any]:
    """Create sample brand identity data for testing"""
    return {
        'brand': {
            'industry': 'plumbing',
            'tone': 'professional',
            'layout_preference': 'modern',
            'image_style': 'professional',
            'name': 'Test Plumbing Services',
            'description': 'Professional plumbing services you can trust'
        },
        'colors': {
            'primary': '#2563EB',
            'secondary': '#64748B',
            'accent': '#F59E0B',
            'background': '#FFFFFF',
            'text_primary': '#111827',
            'text_secondary': '#6B7280',
            'success': '#10B981',
            'error': '#EF4444'
        },
        'typography': {
            'primary_font': 'Inter, system-ui, sans-serif',
            'secondary_font': 'Inter, system-ui, sans-serif',
            'heading_font': 'Inter, system-ui, sans-serif',
            'font_sizes': {
                'xs': '0.75rem',
                'sm': '0.875rem',
                'base': '1rem',
                'lg': '1.125rem',
                'xl': '1.25rem',
                '2xl': '1.5rem',
                '3xl': '1.875rem',
                '4xl': '2.25rem',
                '5xl': '3rem'
            },
            'font_weights': {
                'light': '300',
                'normal': '400',
                'medium': '500',
                'semibold': '600',
                'bold': '700'
            },
            'line_heights': {
                'tight': '1.25',
                'normal': '1.5',
                'relaxed': '1.75'
            }
        },
        'style': {
            'border_radius': '0.75rem',
            'shadow_style': 'modern',
            'spacing_scale': 'comfortable',
            'button_styles': ['rounded', 'shadow'],
            'card_styles': ['rounded', 'shadow'],
            'layout_patterns': ['grid', 'modern']
        }
    }

def create_sample_section() -> Dict[str, Any]:
    """Create sample section data for testing"""
    return {
        'section_id': 1,
        'category': 'hero',
        'heading': 'Professional Plumbing Services',
        'short_copy': 'Expert plumbing solutions for your home and business needs. Available 24/7 for emergency service.',
        'original_text': 'Expert plumbing solutions for your home and business needs. Available 24/7 for emergency service. Licensed, insured, and trusted by thousands of customers.',
        'img_urls': ['https://example.com/plumber.jpg'],
        'classes': ['hero', 'main'],
        'id': 'hero-section',
        'business_data': {
            'phones': ['+1-555-123-4567'],
            'emails': ['info@testplumbing.com'],
            'ctas': ['Call Now', 'Get Quote']
        },
        'confidence': 0.95,
        'reasoning': 'Clear hero section with company name and value proposition',
        'is_hybrid': False,
        'hybrid_categories': [],
        'phone_number': '+1-555-123-4567',
        'email': 'info@testplumbing.com',
        'sizing': {
            'section_padding': 'py-16',
            'height_class': 'min-h-[500px]',
            'container_spacing': 'space-y-8'
        },
        'image_set': {
            'primary_image': {
                'url': 'https://example.com/plumber.jpg',
                'alt_text': 'Professional plumber at work',
                'lazy_load': False
            },
            'all_images': [
                {
                    'url': 'https://example.com/plumber.jpg',
                    'alt_text': 'Professional plumber at work'
                }
            ],
            'hero_images': [
                {
                    'url': 'https://example.com/plumber.jpg',
                    'alt_text': 'Professional plumber at work'
                }
            ],
            'gallery_images': [],
            'icon_images': []
        },
        'typography': {
            'primary_font': 'Inter, system-ui, sans-serif',
            'heading_font': 'Inter, system-ui, sans-serif',
            'semantic_styles': {}
        }
    }

def test_template_rendering(template_name: str = 'hero_modern.html') -> bool:
    """Test if a template renders without errors"""
    try:
        env = Environment(
            loader=FileSystemLoader(TEMPLATES_DIR),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Create sample data
        brand_identity = create_sample_brand_identity()
        section = create_sample_section()
        
        # Render the specific template
        if template_name.startswith('blocks/'):
            template_path = template_name
        else:
            template_path = f'blocks/{template_name}'
        
        template = env.get_template(template_path)
        
        # Render with all required context
        html = template.render(
            section_id=section['section_id'],
            category=section['category'],
            heading=section['heading'],
            short_copy=section['short_copy'],
            original_text=section['original_text'],
            img_urls=section['img_urls'],
            phone_number=section['phone_number'],
            email=section['email'],
            business_data=section['business_data'],
            classes=section['classes'],
            id=section['id'],
            confidence=section['confidence'],
            reasoning=section['reasoning'],
            is_hybrid=section['is_hybrid'],
            hybrid_categories=section['hybrid_categories'],
            brand_identity=brand_identity,
            typography=section['typography'],
            image_set=section['image_set'],
            sizing=section['sizing']
        )
        
        print(f"✅ Template '{template_name}' rendered successfully")
        print(f"   Output length: {len(html)} characters")
        
        # Check for common template errors
        if 'None' in html:
            print("⚠️  Warning: 'None' found in output - may indicate missing variables")
        
        if '{{' in html or '}}' in html:
            print("⚠️  Warning: Unresolved template variables found")
        
        return True
        
    except Exception as e:
        print(f"❌ Template '{template_name}' failed to render: {str(e)}")
        return False

def test_all_templates() -> Dict[str, bool]:
    """Test all main template blocks"""
    templates_to_test = [
        'hero_modern.html',
        'about_responsive.html',
        'services_modern.html',
        'contact_modern.html',
        'gallery_responsive.html',
        'other.html'
    ]
    
    results = {}
    print("🧪 Testing Template Rendering...")
    print("=" * 50)
    
    for template_name in templates_to_test:
        results[template_name] = test_template_rendering(template_name)
        print()
    
    # Summary
    successful = sum(results.values())
    total = len(results)
    
    print("=" * 50)
    print(f"📊 Results: {successful}/{total} templates rendered successfully")
    
    if successful == total:
        print("🎉 All templates are working correctly!")
    else:
        print("⚠️  Some templates need attention")
        
    return results

if __name__ == "__main__":
    test_all_templates()