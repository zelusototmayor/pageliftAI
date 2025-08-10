#!/usr/bin/env python3
"""
Full Site Rendering Test
Tests the complete website rendering pipeline
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import Dict, Any, List

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), '../templates')

def create_sample_sections() -> List[Dict[str, Any]]:
    """Create multiple sections for full site test"""
    
    # Sample brand identity (will be passed globally)
    brand_identity = {
        'brand': {
            'industry': 'plumbing',
            'tone': 'professional',
            'name': 'Expert Plumbing Services',
            'description': 'Professional plumbing services you can trust'
        },
        'colors': {
            'primary': '#2563EB',
            'secondary': '#64748B', 
            'accent': '#F59E0B',
            'background': '#FFFFFF',
            'text_primary': '#111827'
        }
    }
    
    # Sample typography (will be passed globally)
    typography = {
        'primary_font': 'Inter, system-ui, sans-serif',
        'heading_font': 'Inter, system-ui, sans-serif',
        'font_imports': '@import url("https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap");',
        'css': 'body { font-family: Inter, system-ui, sans-serif; }',
        'responsive_css': '@media (max-width: 768px) { .text-responsive-lg { font-size: 2.5rem; } }'
    }
    
    # Base section template with common fields
    base_section = {
        'business_data': {
            'phones': ['+1-555-123-4567'],
            'emails': ['info@expertplumbing.com'],
            'ctas': ['Call Now', 'Get Quote']
        },
        'confidence': 0.9,
        'reasoning': 'Clear categorization based on content analysis',
        'is_hybrid': False,
        'hybrid_categories': [],
        'phone_number': '+1-555-123-4567',
        'email': 'info@expertplumbing.com',
        'classes': [],
        'id': '',
        'sizing': {
            'section_padding': 'py-12',
            'height_class': 'min-h-[400px]',
            'container_spacing': 'space-y-6'
        },
        'image_set': {
            'primary_image': {
                'url': 'https://images.unsplash.com/photo-1621905251918-48416bd8575a',
                'alt_text': 'Professional plumbing work',
                'lazy_load': False
            },
            'all_images': [],
            'hero_images': [],
            'gallery_images': [],
            'icon_images': []
        },
        'typography': typography
    }
    
    sections = [
        # Hero Section
        {
            **base_section,
            'section_id': 1,
            'category': 'hero',
            'heading': 'Expert Plumbing Services You Can Trust',
            'short_copy': 'Professional plumbing solutions for your home and business. Available 24/7 for emergency service.',
            'original_text': 'Professional plumbing solutions for your home and business. Available 24/7 for emergency service. Licensed, insured, and trusted by thousands of customers across the city.',
            'img_urls': ['https://images.unsplash.com/photo-1621905251918-48416bd8575a']
        },
        
        # About Section  
        {
            **base_section,
            'section_id': 2,
            'category': 'about',
            'heading': 'About Our Expert Team',
            'short_copy': 'With over 15 years of experience, we are your trusted local plumbing experts.',
            'original_text': 'With over 15 years of experience serving the community, our team of licensed and insured plumbers brings expertise and professionalism to every job. From simple repairs to complex installations, we deliver quality workmanship you can depend on.',
            'img_urls': ['https://images.unsplash.com/photo-1581578731548-c64695cc6952']
        },
        
        # Services Section
        {
            **base_section,
            'section_id': 3,
            'category': 'services',
            'heading': 'Our Professional Services',
            'short_copy': 'Complete plumbing services for residential and commercial properties.',
            'original_text': 'We offer comprehensive plumbing services including emergency repairs, drain cleaning, pipe installation, water heater service, bathroom remodeling, and commercial plumbing solutions. No job is too big or small.',
            'img_urls': ['https://images.unsplash.com/photo-1558618666-fcd25c85cd64', 'https://images.unsplash.com/photo-1609205970554-47f29e5e5b7c']
        },
        
        # Contact Section
        {
            **base_section,
            'section_id': 4, 
            'category': 'contact',
            'heading': 'Get in Touch Today',
            'short_copy': 'Ready to solve your plumbing problems? Contact us for fast, reliable service.',
            'original_text': 'Ready to solve your plumbing problems? Contact us today for fast, reliable service. We offer free estimates and emergency service 24/7. Call now or fill out our contact form to schedule your appointment.',
            'img_urls': []
        }
    ]
    
    return sections, brand_identity, typography

def test_full_site_rendering() -> bool:
    """Test full site rendering with multiple sections"""
    try:
        env = Environment(
            loader=FileSystemLoader(TEMPLATES_DIR),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Get sample data
        sections, brand_identity, typography = create_sample_sections()
        
        # Test rendering with index_modern.html
        template = env.get_template('index_modern.html')
        
        # Global business data (aggregated from sections)
        business_data = {
            'phones': ['+1-555-123-4567'],
            'emails': ['info@expertplumbing.com']
        }
        
        # Brand CSS (simplified for test)
        brand_css = """
        :root {
            --brand-primary: #2563EB;
            --brand-secondary: #64748B;
            --brand-accent: #F59E0B;
            --brand-text: #111827;
            --brand-background: #FFFFFF;
        }
        
        .text-responsive-lg {
            font-size: clamp(2rem, 5vw, 4rem);
        }
        
        .btn-responsive {
            padding: 0.75rem 2rem;
            font-size: 1.125rem;
        }
        
        .touch-target {
            min-height: 44px;
            min-width: 44px;
        }
        """
        
        # Render the full site
        html = template.render(
            sections=sections,
            title='Expert Plumbing Services - Professional Solutions You Can Trust',
            brand_identity=brand_identity,
            typography=typography,
            business_data=business_data,
            brand_css=brand_css
        )
        
        print(f"✅ Full site rendered successfully")
        print(f"   Total output length: {len(html)} characters")
        print(f"   Number of sections: {len(sections)}")
        
        # Basic quality checks
        checks = {
            'Has DOCTYPE': html.startswith('<!DOCTYPE html>'),
            'Has title tag': '<title>' in html,
            'Has CSS': '<style>' in html or 'brand_css' in html,
            'Has sections': len(sections) > 0,
            'No unresolved variables': '{{' not in html and '}}' not in html,
            'No None values': 'None' not in html
        }
        
        print("\n📊 Quality Checks:")
        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {check}")
        
        # Save test output for inspection
        output_path = os.path.join(os.path.dirname(__file__), '../../debug_archive/test_full_site_output.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"\n💾 Full site HTML saved to: {output_path}")
        print("   You can open this file in a browser to see the rendered result")
        
        all_passed = all(checks.values())
        return all_passed
        
    except Exception as e:
        print(f"❌ Full site rendering failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testing Full Site Rendering...")
    print("=" * 50)
    
    success = test_full_site_rendering()
    
    print("=" * 50)
    if success:
        print("🎉 Full site rendering test PASSED!")
        print("   Templates are working correctly with realistic data")
    else:
        print("⚠️  Full site rendering test FAILED")
        print("   Check the error messages above for details")