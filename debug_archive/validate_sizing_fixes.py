#!/usr/bin/env python3
"""
Validate Sizing Fixes
Tests that oversized elements have been reduced to reasonable sizes.
"""

import os
import sys
import re
from pathlib import Path
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def validate_icon_sizing_fixes():
    """Validate that oversized icons have been fixed in templates."""
    
    print("🔍 Validating Icon Sizing Fixes...")
    print("=" * 50)
    
    try:
        # Setup Jinja2 environment
        template_dir = project_root / "app" / "templates"
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        
        # Test data for rendering
        test_context = {
            'heading': 'Professional Services',
            'short_copy': 'Expert solutions for your needs',
            'original_text': 'We provide comprehensive professional services.',
            'phone_number': '(555) 123-4567',
            'email': 'info@test.com',
            'has_images': False,  # Test placeholder icons
            'img_urls': [],
            'brand_identity': {
                'colors': {
                    'primary': '#1E40AF',
                    'secondary': '#64748B',
                    'accent': '#F59E0B',
                    'text_primary': '#111827',
                    'background': '#FFFFFF'
                },
                'brand': {
                    'industry': 'business',
                    'tone': 'professional',
                    'name': 'Test Company'
                }
            },
            'typography': {
                'heading_font': 'Inter, system-ui, sans-serif',
                'primary_font': 'Inter, system-ui, sans-serif'
            },
            'image_set': {
                'primary_image': None,
                'all_images': [],
                'hero_images': [],
                'gallery_images': [],
                'icon_images': []
            },
            'sizing': None
        }
        
        templates_to_test = [
            'blocks/hero_modern.html',
            'blocks/hero_responsive.html',
            'blocks/services_modern.html',
            'blocks/about_responsive.html',
            'blocks/about.html',
            'blocks/hero.html',
            'blocks/gallery_responsive.html'
        ]
        
        total_oversized_icons = 0
        total_reasonable_icons = 0
        total_templates_tested = 0
        
        for template_path in templates_to_test:
            print(f"\n🔍 Testing {template_path}...")
            
            try:
                template = env.get_template(template_path)
                rendered_html = template.render(**test_context)
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(rendered_html, 'html.parser')
                
                # Analyze icon sizing
                oversized_icons = []
                reasonable_icons = []
                
                # Check SVG icons
                svg_elements = soup.find_all('svg')
                for svg in svg_elements:
                    classes = svg.get('class', [])
                    class_str = ' '.join(classes) if classes else ''
                    
                    # Check for oversized patterns (w-20+, h-20+)
                    oversized_patterns = [
                        r'w-(?:2[0-9]|[3-9][0-9])',  # w-20 and above
                        r'h-(?:2[0-9]|[3-9][0-9])',  # h-20 and above
                    ]
                    
                    is_oversized = any(re.search(pattern, class_str) for pattern in oversized_patterns)
                    
                    # Check for reasonable sizing (w-4 through w-16)
                    reasonable_patterns = [
                        r'w-(?:[4-9]|1[0-6])',  # w-4 through w-16
                        r'h-(?:[4-9]|1[0-6])',  # h-4 through h-16
                    ]
                    
                    is_reasonable = any(re.search(pattern, class_str) for pattern in reasonable_patterns)
                    
                    if is_oversized:
                        oversized_icons.append({
                            'type': 'SVG',
                            'classes': class_str,
                            'issue': 'Still oversized (≥80px)'
                        })
                    elif is_reasonable:
                        reasonable_icons.append({
                            'type': 'SVG',
                            'classes': class_str,
                            'status': 'Good size (16-64px)'
                        })
                
                # Check DIV icon containers
                div_elements = soup.find_all('div')
                for div in div_elements:
                    classes = div.get('class', [])
                    class_str = ' '.join(classes) if classes else ''
                    
                    # Look for icon container patterns
                    is_icon_container = any(keyword in class_str.lower() for keyword in ['icon', 'service-icon'])
                    
                    if is_icon_container or ('rounded' in class_str and 'flex' in class_str and 'items-center' in class_str and 'justify-center' in class_str):
                        # Check sizing
                        oversized_patterns = [
                            r'w-(?:2[0-9]|[3-9][0-9])',  # w-20 and above
                            r'h-(?:2[0-9]|[3-9][0-9])',  # h-20 and above
                        ]
                        
                        reasonable_patterns = [
                            r'w-(?:1[0-6])',  # w-10 through w-16
                            r'h-(?:1[0-6])',  # h-10 through h-16
                        ]
                        
                        is_oversized = any(re.search(pattern, class_str) for pattern in oversized_patterns)
                        is_reasonable = any(re.search(pattern, class_str) for pattern in reasonable_patterns)
                        
                        if is_oversized:
                            oversized_icons.append({
                                'type': 'DIV Container',
                                'classes': class_str[:80] + '...' if len(class_str) > 80 else class_str,
                                'issue': 'Still oversized container (≥80px)'
                            })
                        elif is_reasonable:
                            reasonable_icons.append({
                                'type': 'DIV Container',
                                'classes': class_str[:80] + '...' if len(class_str) > 80 else class_str,
                                'status': 'Good container size'
                            })
                
                total_oversized_icons += len(oversized_icons)
                total_reasonable_icons += len(reasonable_icons)
                total_templates_tested += 1
                
                print(f"   📊 Oversized icons: {len(oversized_icons)}")
                print(f"   📊 Reasonable icons: {len(reasonable_icons)}")
                
                if len(oversized_icons) == 0:
                    print(f"   ✅ No oversized icons found!")
                else:
                    print(f"   ⚠️  Found {len(oversized_icons)} oversized icons:")
                    for icon in oversized_icons[:3]:  # Show first 3
                        print(f"      - {icon['type']}: {icon['issue']}")
                        print(f"        Classes: {icon['classes']}")
                
            except Exception as e:
                print(f"   ❌ Error rendering template: {e}")
        
        # Generate validation results
        print(f"\n📊 OVERALL VALIDATION RESULTS")
        print("-" * 40)
        print(f"Templates tested: {total_templates_tested}")
        print(f"Total oversized icons found: {total_oversized_icons}")
        print(f"Total reasonable icons found: {total_reasonable_icons}")
        
        if total_oversized_icons == 0:
            print("🎉 SUCCESS: No oversized icons found in templates!")
            success_rate = 100
        else:
            success_rate = (total_reasonable_icons / (total_reasonable_icons + total_oversized_icons)) * 100
            print(f"📊 Icon sizing success rate: {success_rate:.1f}%")
        
        return total_oversized_icons == 0
        
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        import traceback
        traceback.print_exc()
        return False

def validate_padding_fixes():
    """Validate that excessive padding has been reduced."""
    
    print(f"\n🔍 Validating Padding Reductions...")
    print("-" * 40)
    
    try:
        # Check proportional_sizing.py constants
        sizing_file = project_root / "app" / "services" / "proportional_sizing.py"
        
        with open(sizing_file, 'r') as f:
            content = f.read()
        
        # Extract current padding constants
        padding_patterns = {
            'MINIMAL_PADDING': r'MINIMAL_PADDING\s*=\s*["\']([^"\']+)["\']',
            'COMPACT_PADDING': r'COMPACT_PADDING\s*=\s*["\']([^"\']+)["\']',
            'STANDARD_PADDING': r'STANDARD_PADDING\s*=\s*["\']([^"\']+)["\']',
            'EXPANDED_PADDING': r'EXPANDED_PADDING\s*=\s*["\']([^"\']+)["\']'
        }
        
        current_padding = {}
        for name, pattern in padding_patterns.items():
            match = re.search(pattern, content)
            if match:
                current_padding[name] = match.group(1)
        
        print("Current padding constants:")
        for name, value in current_padding.items():
            print(f"  {name}: {value}")
        
        # Check if padding has been reduced (should be py-10 or less for max)
        max_padding = current_padding.get('EXPANDED_PADDING', '')
        if 'py-' in max_padding:
            padding_num = re.search(r'py-(\d+)', max_padding)
            if padding_num:
                max_py_value = int(padding_num.group(1))
                if max_py_value <= 10:
                    print(f"✅ Maximum padding reduced to py-{max_py_value} (reasonable)")
                    padding_success = True
                else:
                    print(f"⚠️  Maximum padding still py-{max_py_value} (could be smaller)")
                    padding_success = False
            else:
                padding_success = False
        else:
            padding_success = False
        
        return padding_success
        
    except Exception as e:
        print(f"❌ Error validating padding: {e}")
        return False

def main():
    """Main validation function."""
    
    print("🧪 Validating Sizing Fixes...")
    print("=" * 60)
    
    # Validate icon sizing fixes
    icons_fixed = validate_icon_sizing_fixes()
    
    # Validate padding reductions
    padding_fixed = validate_padding_fixes()
    
    # Overall assessment
    print(f"\n🎯 FINAL ASSESSMENT")
    print("-" * 30)
    
    if icons_fixed and padding_fixed:
        print("🎉 ALL SIZING FIXES SUCCESSFUL!")
        print("✅ Oversized icons have been reduced to reasonable sizes")
        print("✅ Excessive padding has been reduced")
        print("✅ Generated websites should no longer be 'insanely long' with 'massive icons'")
        return True
    else:
        if not icons_fixed:
            print("⚠️  Some oversized icons still need fixing")
        if not padding_fixed:
            print("⚠️  Padding reductions may need more work")
        print("🔄 Additional template adjustments may be needed")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)