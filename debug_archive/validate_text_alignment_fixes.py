#!/usr/bin/env python3
"""
Validate Text Alignment Fixes
Directly tests template rendering with text alignment improvements.
"""

import os
import sys
from pathlib import Path
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def validate_template_fixes():
    """Validate that templates now have proper text alignment."""
    
    print("✅ Validating Text Alignment Fixes in Templates")
    print("=" * 60)
    
    try:
        # Setup Jinja2 environment
        template_dir = project_root / "app" / "templates"
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        
        # Test data for rendering
        test_context = {
            'heading': 'Professional Drain Cleaning Services',
            'short_copy': 'Expert drain cleaning services available 24/7',
            'original_text': 'We provide comprehensive drain cleaning services for residential and commercial properties.',
            'phone_number': '(555) 123-4567',
            'email': 'info@test.com',
            'brand_identity': {
                'colors': {
                    'primary': '#1E40AF',
                    'secondary': '#64748B',
                    'accent': '#F59E0B',
                    'text_primary': '#111827',
                    'background': '#FFFFFF'
                },
                'brand': {
                    'industry': 'plumbing',
                    'tone': 'professional',
                    'name': 'Test Plumbing Co'
                }
            },
            'typography': {
                'heading_font': 'Inter, system-ui, sans-serif',
                'primary_font': 'Inter, system-ui, sans-serif'
            },
            'image_set': {
                'primary_image': {'url': 'test.jpg', 'alt_text': 'Test image'},
                'all_images': [],
                'hero_images': [],
                'gallery_images': [],
                'icon_images': []
            },
            'sizing': None
        }
        
        templates_to_test = [
            'blocks/hero_modern.html',
            'blocks/services_modern.html', 
            'blocks/about_responsive.html',
            'blocks/contact_modern.html'
        ]
        
        total_headers = 0
        aligned_headers = 0
        center_aligned_headers = 0
        responsive_headers = 0
        overflow_protected_text = 0
        
        for template_path in templates_to_test:
            print(f"\n🔍 Testing {template_path}...")
            
            try:
                template = env.get_template(template_path)
                rendered_html = template.render(**test_context)
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(rendered_html, 'html.parser')
                
                # Analyze headers
                headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                template_total_headers = len(headers)
                template_aligned = 0
                template_center = 0
                template_responsive = 0
                
                for header in headers:
                    classes = header.get('class', [])
                    class_str = ' '.join(classes)
                    
                    # Check for explicit alignment
                    if any(cls in classes for cls in ['text-left', 'text-center', 'text-right', 'text-justify']):
                        template_aligned += 1
                        aligned_headers += 1
                        
                        if 'text-center' in classes:
                            template_center += 1
                            center_aligned_headers += 1
                    
                    # Check for responsive alignment
                    responsive_classes = [cls for cls in classes if any(breakpoint in cls for breakpoint in ['sm:', 'md:', 'lg:', 'xl:']) and 'text-' in cls]
                    if responsive_classes:
                        template_responsive += 1
                        responsive_headers += 1
                
                # Analyze text overflow protection
                text_elements = soup.find_all(['p', 'div', 'span'])
                template_protected = 0
                
                for elem in text_elements:
                    classes = elem.get('class', [])
                    class_str = ' '.join(classes)
                    if any(cls in class_str for cls in ['break-words', 'overflow-hidden', 'text-ellipsis']):
                        template_protected += 1
                        overflow_protected_text += 1
                
                total_headers += template_total_headers
                
                print(f"   📊 Headers: {template_total_headers} total, {template_aligned} aligned ({template_aligned/template_total_headers*100:.1f}% if template_total_headers > 0 else 0)")
                print(f"   📊 Center-aligned: {template_center}")
                print(f"   📊 Responsive: {template_responsive}")
                print(f"   📊 Overflow protected: {template_protected}")
                
                if template_total_headers > 0 and template_aligned >= template_total_headers * 0.8:
                    print(f"   ✅ Good alignment coverage!")
                elif template_total_headers > 0:
                    print(f"   ⚠️  Needs more alignment classes")
                else:
                    print(f"   ℹ️  No headers in this template")
                    
            except Exception as e:
                print(f"   ❌ Error rendering template: {e}")
        
        print(f"\n📈 OVERALL RESULTS")
        print("-" * 30)
        print(f"Total headers analyzed: {total_headers}")
        print(f"Headers with alignment: {aligned_headers} ({aligned_headers/total_headers*100:.1f}%)")
        print(f"Center-aligned headers: {center_aligned_headers}")
        print(f"Responsive headers: {responsive_headers}")
        print(f"Text with overflow protection: {overflow_protected_text}")
        
        # Calculate improvement score
        alignment_score = aligned_headers / total_headers if total_headers > 0 else 0
        center_score = center_aligned_headers / aligned_headers if aligned_headers > 0 else 0
        
        print(f"\n🎯 IMPROVEMENT ANALYSIS")
        print("-" * 30)
        
        if alignment_score >= 0.8:
            print("✅ Excellent text alignment coverage (≥80%)")
        elif alignment_score >= 0.6:
            print("✅ Good text alignment coverage (≥60%)")
        elif alignment_score >= 0.4:
            print("⚠️  Fair text alignment coverage (≥40%)")
        else:
            print("❌ Poor text alignment coverage (<40%)")
            
        if center_score >= 0.5:
            print("✅ Good use of center alignment for visual hierarchy")
        else:
            print("⚠️  Could use more center alignment")
            
        if responsive_headers > 0:
            print("✅ Some responsive text alignment implemented")
        else:
            print("⚠️  No responsive text alignment found")
            
        if overflow_protected_text >= 10:
            print("✅ Good text overflow protection")
        else:
            print("⚠️  Limited text overflow protection")
        
        # Overall assessment
        fixes_working = alignment_score >= 0.7 and center_score >= 0.3
        
        if fixes_working:
            print(f"\n🎉 TEXT ALIGNMENT FIXES ARE WORKING!")
            print("Templates now have significantly improved text alignment.")
        else:
            print(f"\n⚠️  TEXT ALIGNMENT FIXES NEED MORE WORK")
            print("Some templates still lack proper text alignment classes.")
            
        return fixes_working
        
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = validate_template_fixes()
    exit(0 if success else 1)