#!/usr/bin/env python3
"""
Focused Template Rendering Debugging Script

This script focuses specifically on template rendering issues that cause:
- Major icons appearing too large
- Excessively long pages
- Left-aligned text with no UI styling
- Poor template utilization of extracted data

Tests with sample data to isolate template rendering problems.
"""

import os
import sys
import json
import tempfile
import zipfile
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from app.services.render import render_site_with_brand, prepare_section_for_rendering
    from app.services.image_processing import process_section_images
    from app.services.proportional_sizing import apply_proportional_sizing_to_sections
    from app.services.css_generator import generate_brand_css
    from app.services.typography import create_typography_system
except ImportError as e:
    print(f"Import error: {e}")
    print("This script needs to be run from the project root with dependencies installed")
    sys.exit(1)


def create_sample_analysis_data():
    """Create sample analysis data that mimics what analyze_sections would produce"""
    return [
        {
            'section_id': 0,
            'category': 'hero',
            'heading': 'Professional Drain Cleaning Services',
            'short_copy': 'Expert plumbing solutions available 24/7 for all your drainage needs.',
            'original_text': 'Professional Drain Cleaning Services - Expert plumbing solutions available 24/7 for all your drainage needs. Licensed and insured technicians.',
            'img_urls': ['https://via.placeholder.com/800x600/0066CC/FFFFFF?text=Plumbing+Service'],
            'classes': ['hero-section', 'main-content'],
            'id': 'hero-main',
            'business_data': {
                'phones': ['+351 123 456 789'],
                'emails': ['info@desentopecanalizacoes.pt'],
                'ctas': ['Call Now', 'Get Quote']
            },
            'confidence': 0.9,
            'reasoning': 'Clear hero section with company branding'
        },
        {
            'section_id': 1,
            'category': 'about',
            'heading': 'About Our Company',
            'short_copy': 'With over 20 years of experience in professional plumbing services.',
            'original_text': 'About Our Company - With over 20 years of experience in professional plumbing services, we provide reliable solutions for residential and commercial clients across Portugal.',
            'img_urls': ['https://via.placeholder.com/600x400/00AA44/FFFFFF?text=Team+Photo'],
            'classes': ['about-section'],
            'id': 'about-us',
            'business_data': {
                'phones': ['+351 123 456 789'],
                'emails': [],
                'ctas': []
            },
            'confidence': 0.85,
            'reasoning': 'Company background information'
        },
        {
            'section_id': 2,
            'category': 'services',
            'heading': 'Our Services',
            'short_copy': 'Complete drainage and plumbing solutions.',
            'original_text': 'Our Services - Complete drainage and plumbing solutions including emergency repairs, maintenance, installation, and inspection services.',
            'img_urls': [
                'https://via.placeholder.com/400x300/FF6600/FFFFFF?text=Service+1',
                'https://via.placeholder.com/400x300/FF6600/FFFFFF?text=Service+2',
                'https://via.placeholder.com/400x300/FF6600/FFFFFF?text=Service+3'
            ],
            'classes': ['services-section'],
            'id': 'services',
            'business_data': {
                'phones': ['+351 123 456 789'],
                'emails': ['services@desentopecanalizacoes.pt'],
                'ctas': ['Request Service', 'Get Quote']
            },
            'confidence': 0.92,
            'reasoning': 'Services listing with clear CTAs'
        },
        {
            'section_id': 3,
            'category': 'contact',
            'heading': 'Contact Us',
            'short_copy': 'Get in touch for professional plumbing services.',
            'original_text': 'Contact Us - Get in touch for professional plumbing services. Available 24/7 for emergency calls.',
            'img_urls': [],
            'classes': ['contact-section'],
            'id': 'contact',
            'business_data': {
                'phones': ['+351 123 456 789', '+351 987 654 321'],
                'emails': ['info@desentopecanalizacoes.pt', 'emergency@desentopecanalizacoes.pt'],
                'ctas': ['Call Now', 'Email Us', 'Schedule Service']
            },
            'confidence': 0.95,
            'reasoning': 'Clear contact information and CTAs'
        },
        {
            'section_id': 4,
            'category': 'other',
            'heading': 'Additional Information',
            'short_copy': 'Various policies and additional details about our services.',
            'original_text': 'Additional Information - Various policies and additional details about our services including terms of service, privacy policy, and service area information.',
            'img_urls': ['https://via.placeholder.com/300x200/CCCCCC/333333?text=Info'],
            'classes': ['info-section', 'secondary'],
            'id': 'additional-info',
            'business_data': {
                'phones': [],
                'emails': [],
                'ctas': []
            },
            'confidence': 0.6,
            'reasoning': 'General information section'
        }
    ]


def create_sample_brand_identity():
    """Create sample brand identity data"""
    return {
        'brand': {
            'industry': 'plumbing',
            'tone': 'professional',
            'layout_preference': 'modern',
            'image_style': 'realistic',
            'name': 'Desentope Canalizações',
            'description': 'Professional plumbing and drainage services'
        },
        'colors': {
            'primary': '#0066CC',    # Blue
            'secondary': '#004499',  # Darker blue
            'accent': '#FF6600',     # Orange
            'background': '#FFFFFF', # White
            'text_primary': '#333333',   # Dark gray
            'text_secondary': '#666666', # Medium gray
            'success': '#00AA44',    # Green
            'error': '#CC0000'       # Red
        },
        'typography': {
            'primary_font': 'Inter',
            'secondary_font': 'Inter',
            'heading_font': 'Inter',
            'font_sizes': {
                'xs': '12px',
                'sm': '14px',
                'base': '16px',
                'lg': '18px',
                'xl': '20px'
            },
            'font_weights': {
                'normal': 400,
                'medium': 500,
                'semibold': 600,
                'bold': 700
            },
            'line_heights': {
                'tight': '1.25',
                'normal': '1.5',
                'relaxed': '1.75'
            }
        },
        'style': {
            'border_radius': 'rounded-lg',
            'shadow_style': 'modern',
            'spacing_scale': 'comfortable',
            'button_styles': ['solid', 'outline'],
            'card_styles': ['elevated', 'bordered'],
            'layout_patterns': ['grid', 'flexbox']
        }
    }


def analyze_template_context_preparation(sections_data, brand_identity):
    """Analyze how template context is prepared"""
    print("\n" + "="*60)
    print("  TEMPLATE CONTEXT PREPARATION ANALYSIS")
    print("="*60)
    
    issues = []
    
    for section in sections_data:
        print(f"\n📊 Section {section['section_id']} ({section['category']}):")
        
        try:
            # Test context preparation
            prepared = prepare_section_for_rendering(section)
            
            print(f"   ✅ Context prepared successfully")
            print(f"   📋 Context keys: {list(prepared.keys())}")
            
            # Check for specific issues
            if 'sizing' not in prepared:
                issues.append(f"Section {section['section_id']}: Missing sizing data")
                print("   ❌ Missing sizing data")
            else:
                sizing = prepared['sizing']
                print(f"   📏 Sizing: {list(sizing.keys()) if sizing else 'Empty'}")
            
            if 'image_set' not in prepared:
                issues.append(f"Section {section['section_id']}: Missing image_set")
                print("   ❌ Missing image_set")
            
            if 'typography' not in prepared:
                issues.append(f"Section {section['section_id']}: Missing typography")
                print("   ❌ Missing typography")
            
            # Check business data propagation
            business_data = prepared.get('business_data', {})
            phone = prepared.get('phone_number')
            email = prepared.get('email')
            
            print(f"   📞 Phone: {phone}")
            print(f"   📧 Email: {email}")
            
            if section['business_data']['phones'] and not phone:
                issues.append(f"Section {section['section_id']}: Phone not propagated to template")
            
        except Exception as e:
            issues.append(f"Section {section['section_id']}: Context preparation failed - {e}")
            print(f"   ❌ Preparation failed: {e}")
    
    return issues


def analyze_proportional_sizing(sections_data):
    """Analyze proportional sizing system"""
    print("\n" + "="*60)
    print("  PROPORTIONAL SIZING ANALYSIS")
    print("="*60)
    
    issues = []
    
    try:
        sections_with_sizing = apply_proportional_sizing_to_sections(sections_data)
        print(f"   ✅ Sizing applied to {len(sections_with_sizing)} sections")
        
        for section in sections_with_sizing:
            sizing = section.get('sizing', {})
            section_id = section.get('section_id', 'Unknown')
            category = section.get('category', 'unknown')
            
            print(f"\n   📏 Section {section_id} ({category}):")
            if sizing:
                print(f"      • Section padding: {sizing.get('section_padding', 'Missing')}")
                print(f"      • Height class: {sizing.get('height_class', 'Missing')}")
                print(f"      • Container spacing: {sizing.get('container_spacing', 'Missing')}")
                
                # Check for problematic sizing
                padding = sizing.get('section_padding', '')
                if 'py-20' in padding or 'py-24' in padding:
                    issues.append(f"Section {section_id}: Excessive padding ({padding}) may cause long pages")
                
                height = sizing.get('height_class', '')
                if 'min-h-screen' in height or '800px' in height:
                    issues.append(f"Section {section_id}: Excessive height ({height}) may cause long pages")
                    
            else:
                issues.append(f"Section {section_id}: No sizing data applied")
                print("      ❌ No sizing data")
        
        return sections_with_sizing, issues
        
    except Exception as e:
        issues.append(f"Proportional sizing failed: {e}")
        print(f"   ❌ Sizing failed: {e}")
        return sections_data, issues


def analyze_css_generation(brand_identity):
    """Analyze CSS generation for styling issues"""
    print("\n" + "="*60)
    print("  CSS GENERATION ANALYSIS")
    print("="*60)
    
    issues = []
    
    try:
        # Create typography system
        typography = create_typography_system(brand_identity)
        print("   ✅ Typography system created")
        
        # Generate brand CSS
        brand_css = generate_brand_css(brand_identity, typography)
        print(f"   ✅ Brand CSS generated ({len(brand_css)} chars)")
        
        # Analyze CSS content
        if len(brand_css) < 1000:
            issues.append("Generated CSS is very short - may be missing important styles")
        
        # Check for critical CSS components
        required_css_parts = [
            '--brand-primary',
            '--brand-secondary', 
            '--brand-accent',
            'font-family',
            '.btn',
            '.card'
        ]
        
        for part in required_css_parts:
            if part not in brand_css:
                issues.append(f"Missing critical CSS component: {part}")
        
        # Check for problematic colors
        colors = brand_identity.get('colors', {})
        primary = colors.get('primary', '').lower()
        background = colors.get('background', '').lower()
        
        if primary == background:
            issues.append("Primary color same as background - visibility issues")
        
        # Save CSS for inspection
        css_file = "/Users/zelu/Desktop/code/PageLift AI/debug_output/debug_generated_css.css"
        with open(css_file, 'w') as f:
            f.write(brand_css)
        print(f"   📁 CSS saved to: {css_file}")
        
        return typography, brand_css, issues
        
    except Exception as e:
        issues.append(f"CSS generation failed: {e}")
        print(f"   ❌ CSS generation failed: {e}")
        return None, "", issues


def test_site_rendering(sections_data, brand_identity, title="Test Plumbing Site"):
    """Test the complete site rendering process"""
    print("\n" + "="*60)
    print("  SITE RENDERING TEST")
    print("="*60)
    
    issues = []
    
    try:
        # Render the site
        print("   🎨 Rendering website...")
        zip_path = render_site_with_brand(sections_data, brand_identity, title)
        print(f"   ✅ Site rendered to: {zip_path}")
        
        # Extract and analyze the HTML
        extract_dir = "/Users/zelu/Desktop/code/PageLift AI/debug_output/debug_extracted_site"
        os.makedirs(extract_dir, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        html_path = os.path.join(extract_dir, 'index.html')
        
        if os.path.exists(html_path):
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            print(f"   📄 Generated HTML: {len(html_content):,} characters")
            
            # Analyze HTML for issues
            if len(html_content) < 10000:
                issues.append("Generated HTML is very short - content may be missing")
            elif len(html_content) > 200000:
                issues.append("Generated HTML is extremely long - may have excessive content/duplication")
            
            # Check for specific problems
            svg_count = html_content.count('<svg')
            img_count = html_content.count('<img')
            section_count = html_content.count('<section')
            
            print(f"   🖼️  SVG icons: {svg_count}")
            print(f"   📷 Images: {img_count}")  
            print(f"   📄 Sections: {section_count}")
            
            if svg_count > 100:
                issues.append(f"Excessive SVG icons ({svg_count}) - may cause visual overload")
            
            # Check for styling classes
            if 'text-left' in html_content and html_content.count('text-left') > html_content.count('text-center'):
                issues.append("Most text appears to be left-aligned - may lack responsive design")
            
            # Check for responsive classes
            responsive_classes = ['sm:', 'md:', 'lg:', 'xl:']
            responsive_count = sum(html_content.count(cls) for cls in responsive_classes)
            if responsive_count < 20:
                issues.append("Low responsive class usage - may not be mobile-friendly")
            
            # Check for brand CSS integration
            if '--brand-primary' not in html_content:
                issues.append("Brand CSS variables not integrated into HTML")
            
            # Copy HTML for inspection
            debug_html = "/Users/zelu/Desktop/code/PageLift AI/debug_output/debug_generated_website.html"
            with open(debug_html, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"   📁 HTML saved to: {debug_html}")
            
            print(f"   📁 Full site extracted to: {extract_dir}")
            
        else:
            issues.append("Generated ZIP does not contain index.html")
        
    except Exception as e:
        issues.append(f"Site rendering failed: {e}")
        print(f"   ❌ Rendering failed: {e}")
    
    return issues


def main():
    """Run the focused template rendering debugging"""
    print("🔍 FOCUSED TEMPLATE RENDERING DEBUGGING")
    print("Testing with sample Portuguese plumbing site data\n")
    
    all_issues = []
    
    # Create sample data
    sections_data = create_sample_analysis_data()
    brand_identity = create_sample_brand_identity()
    
    print(f"📊 Testing with {len(sections_data)} sections")
    print(f"🎨 Brand: {brand_identity['brand']['name']}")
    print(f"🎨 Colors: {brand_identity['colors']['primary']} / {brand_identity['colors']['accent']}")
    
    # Analyze template context preparation
    context_issues = analyze_template_context_preparation(sections_data, brand_identity)
    all_issues.extend(context_issues)
    
    # Analyze proportional sizing
    sections_with_sizing, sizing_issues = analyze_proportional_sizing(sections_data)
    all_issues.extend(sizing_issues)
    
    # Analyze CSS generation
    typography, brand_css, css_issues = analyze_css_generation(brand_identity)
    all_issues.extend(css_issues)
    
    # Test site rendering
    rendering_issues = test_site_rendering(sections_with_sizing, brand_identity)
    all_issues.extend(rendering_issues)
    
    # Final summary
    print("\n" + "="*80)
    print("  DEBUGGING RESULTS SUMMARY")
    print("="*80)
    
    if all_issues:
        print("\n❌ ISSUES IDENTIFIED:")
        for i, issue in enumerate(all_issues, 1):
            print(f"   {i:2d}. {issue}")
    else:
        print("\n✅ No major issues detected!")
    
    print(f"\n📊 Total Issues Found: {len(all_issues)}")
    print("\n📁 Generated files for manual inspection (in debug_output/):")
    print("   • debug_generated_css.css - Generated CSS")
    print("   • debug_generated_website.html - Generated HTML")
    print("   • debug_extracted_site/ - Complete extracted site")
    
    return all_issues


if __name__ == "__main__":
    issues = main()
    
    # Update todo list with findings
    print(f"\nTemplate rendering debugging complete.")
    print(f"Found {len(issues)} specific issues to address.")