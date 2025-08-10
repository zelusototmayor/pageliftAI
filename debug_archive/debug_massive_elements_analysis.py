#!/usr/bin/env python3
"""
Debug Massive Elements Analysis
Analyzes generated HTML to identify oversized images, icons, and sections causing long pages.
"""

import os
import sys
import re
from pathlib import Path
from bs4 import BeautifulSoup
from typing import Dict, List, Tuple, Any

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def analyze_oversized_elements(html_content: str) -> Dict[str, Any]:
    """Analyze HTML for oversized elements causing layout issues."""
    
    soup = BeautifulSoup(html_content, 'html.parser')
    issues = []
    recommendations = []
    
    print("🔍 Analyzing for Oversized Elements...")
    
    # 1. Check SVG icon sizes
    svg_elements = soup.find_all('svg')
    oversized_svgs = []
    
    for i, svg in enumerate(svg_elements):
        classes = svg.get('class', [])
        class_str = ' '.join(classes) if classes else ''
        
        # Check for oversized SVG classes
        oversized_patterns = [
            r'w-\d{2,}',  # width-20 and above (80px+)
            r'h-\d{2,}',  # height-20 and above (80px+)
            'w-full', 'h-full', 'w-screen', 'h-screen'
        ]
        
        is_oversized = any(re.search(pattern, class_str) for pattern in oversized_patterns)
        
        # Check parent container for size constraints
        parent = svg.parent
        parent_classes = parent.get('class', []) if parent else []
        parent_str = ' '.join(parent_classes) if parent_classes else ''
        has_size_constraint = any(cls in parent_str for cls in ['w-', 'h-', 'max-w-', 'max-h-'])
        
        if is_oversized or (not has_size_constraint and not any(cls.startswith(('w-', 'h-')) for cls in classes)):
            oversized_svgs.append({
                'index': i + 1,
                'classes': class_str,
                'parent_classes': parent_str,
                'issue': 'Potentially oversized or unconstrained SVG'
            })
    
    # 2. Check IMG elements
    img_elements = soup.find_all('img')
    oversized_imgs = []
    
    for i, img in enumerate(img_elements):
        classes = img.get('class', [])
        class_str = ' '.join(classes) if classes else ''
        
        # Check for problematic image sizing
        problematic_patterns = [
            r'h-\d{3,}',  # Very large fixed heights
            r'w-\d{3,}',  # Very large fixed widths
            'h-screen', 'w-screen', 'min-h-screen'
        ]
        
        # Check for missing responsive sizing
        has_responsive = any('sm:' in cls or 'md:' in cls or 'lg:' in cls for cls in classes)
        has_object_fit = any('object-' in cls for cls in classes)
        has_aspect_ratio = any('aspect-' in cls for cls in classes)
        
        is_problematic = any(re.search(pattern, class_str) for pattern in problematic_patterns)
        
        if is_problematic or not has_responsive or not has_object_fit:
            oversized_imgs.append({
                'index': i + 1,
                'classes': class_str,
                'src': img.get('src', '')[:50] + '...' if img.get('src') else 'No src',
                'has_responsive': has_responsive,
                'has_object_fit': has_object_fit,
                'has_aspect_ratio': has_aspect_ratio,
                'issue': 'Missing responsive sizing or object-fit'
            })
    
    # 3. Check section heights and padding
    sections = soup.find_all(['section', 'div'])
    oversized_sections = []
    
    for i, section in enumerate(sections):
        classes = section.get('class', [])
        class_str = ' '.join(classes) if classes else ''
        
        # Look for excessive padding/height classes
        excessive_patterns = [
            r'py-\d{2,}',   # padding-y 20+ (80px+)
            r'px-\d{2,}',   # padding-x 20+ (80px+)
            r'p-\d{2,}',    # padding 20+ (80px+)
            r'h-\d{3,}',    # height 100+ (400px+)
            r'min-h-\[\d{4,}px\]',  # min-height 1000px+
            'min-h-screen', 'h-screen'
        ]
        
        is_excessive = any(re.search(pattern, class_str) for pattern in excessive_patterns)
        
        if is_excessive:
            # Get section content length to see if size is justified
            text_content = section.get_text().strip()
            content_length = len(text_content)
            
            oversized_sections.append({
                'index': i + 1,
                'classes': class_str[:100] + '...' if len(class_str) > 100 else class_str,
                'tag': section.name,
                'content_length': content_length,
                'issue': 'Excessive padding or height classes'
            })
    
    # 4. Check for container width issues
    containers = soup.find_all(['div', 'section'])
    width_issues = []
    
    for i, container in enumerate(containers):
        classes = container.get('class', [])
        class_str = ' '.join(classes) if classes else ''
        
        # Look for containers without proper width constraints
        has_width_constraint = any(cls in class_str for cls in ['max-w-', 'w-full', 'container'])
        has_responsive_width = any(breakpoint in class_str for breakpoint in ['sm:', 'md:', 'lg:', 'xl:'])
        
        # Check if it's a main content container (likely to need constraints)
        is_content_container = any(keyword in class_str.lower() for keyword in ['section', 'container', 'wrapper', 'content'])
        
        if is_content_container and not has_width_constraint:
            width_issues.append({
                'index': i + 1,
                'classes': class_str[:100] + '...' if len(class_str) > 100 else class_str,
                'tag': container.name,
                'issue': 'Missing width constraints'
            })
    
    # 5. Analyze overall page height
    total_sections = len(soup.find_all(['section']))
    total_height_estimate = 0
    
    # Estimate page height based on sections and their padding
    for section in soup.find_all(['section']):
        classes = section.get('class', [])
        class_str = ' '.join(classes) if classes else ''
        
        # Estimate section height based on padding classes
        base_height = 200  # Base section height
        
        # Add padding estimates
        padding_matches = re.findall(r'py-(\d+)', class_str)
        for match in padding_matches:
            padding_value = int(match)
            base_height += padding_value * 8  # Tailwind: py-1 = 8px total
        
        # Add min-height estimates
        min_height_matches = re.findall(r'min-h-\[(\d+)px\]', class_str)
        for match in min_height_matches:
            min_height = int(match)
            base_height = max(base_height, min_height)
            
        if 'min-h-screen' in class_str:
            base_height = max(base_height, 800)  # Assume 800px screen
            
        total_height_estimate += base_height
    
    # Generate comprehensive analysis
    analysis = {
        'svg_analysis': {
            'total_svgs': len(svg_elements),
            'oversized_svgs': len(oversized_svgs),
            'oversized_details': oversized_svgs[:10]  # Show first 10
        },
        'img_analysis': {
            'total_imgs': len(img_elements),
            'oversized_imgs': len(oversized_imgs),
            'oversized_details': oversized_imgs[:10]  # Show first 10
        },
        'section_analysis': {
            'total_sections': len(sections),
            'oversized_sections': len(oversized_sections),
            'oversized_details': oversized_sections[:10],
            'estimated_total_height': total_height_estimate
        },
        'container_analysis': {
            'total_containers': len(containers),
            'width_issues': len(width_issues),
            'width_issues_details': width_issues[:10]
        }
    }
    
    return analysis

def main():
    """Main execution function."""
    
    print("🔍 Analyzing Massive Elements in Generated Website...")
    print("=" * 60)
    
    # Read the generated website HTML
    html_file = project_root / "debug_output" / "debug_generated_website.html"
    
    if not html_file.exists():
        print(f"❌ HTML file not found: {html_file}")
        print("Run the pipeline debug script first to generate the HTML.")
        return
    
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        print(f"📄 Analyzing HTML file: {html_file}")
        print(f"📊 File size: {len(html_content):,} characters")
        print()
        
        # Analyze oversized elements
        analysis = analyze_oversized_elements(html_content)
        
        # Print SVG Analysis
        print("🎭 SVG ICON ANALYSIS")
        print("-" * 30)
        svg_data = analysis['svg_analysis']
        print(f"Total SVGs found: {svg_data['total_svgs']}")
        print(f"Potentially oversized: {svg_data['oversized_svgs']}")
        
        if svg_data['oversized_details']:
            print("\nOversized SVG Details:")
            for svg in svg_data['oversized_details']:
                print(f"  SVG {svg['index']}: {svg['issue']}")
                print(f"    Classes: {svg['classes'] or 'None'}")
                print(f"    Parent: {svg['parent_classes'] or 'None'}")
                print()
        
        # Print IMG Analysis
        print("🖼️  IMAGE ANALYSIS")
        print("-" * 30)
        img_data = analysis['img_analysis']
        print(f"Total images found: {img_data['total_imgs']}")
        print(f"Images with sizing issues: {img_data['oversized_imgs']}")
        
        if img_data['oversized_details']:
            print("\nImage Sizing Issues:")
            for img in img_data['oversized_details']:
                print(f"  IMG {img['index']}: {img['issue']}")
                print(f"    Classes: {img['classes'] or 'None'}")
                print(f"    Responsive: {img['has_responsive']}")
                print(f"    Object-fit: {img['has_object_fit']}")
                print()
        
        # Print Section Analysis  
        print("📏 SECTION HEIGHT ANALYSIS")
        print("-" * 30)
        section_data = analysis['section_analysis']
        print(f"Total sections: {section_data['total_sections']}")
        print(f"Oversized sections: {section_data['oversized_sections']}")
        print(f"Estimated page height: {section_data['estimated_total_height']:,}px")
        
        if section_data['estimated_total_height'] > 3000:
            print("⚠️  WARNING: Page height is excessive (>3000px)")
        elif section_data['estimated_total_height'] > 2000:
            print("⚠️  CAUTION: Page height is quite long (>2000px)")
        else:
            print("✅ Page height seems reasonable")
        
        if section_data['oversized_details']:
            print("\nOversized Section Details:")
            for section in section_data['oversized_details']:
                print(f"  {section['tag'].upper()} {section['index']}: {section['issue']}")
                print(f"    Classes: {section['classes']}")
                print(f"    Content length: {section['content_length']} chars")
                print()
        
        # Print Container Analysis
        print("📦 CONTAINER WIDTH ANALYSIS")
        print("-" * 30)
        container_data = analysis['container_analysis']
        print(f"Total containers: {container_data['total_containers']}")
        print(f"Width constraint issues: {container_data['width_issues']}")
        
        # Generate recommendations
        recommendations = []
        
        if svg_data['oversized_svgs'] > 0:
            recommendations.append("Fix SVG icon sizing by adding explicit w-4 h-4, w-6 h-6, or w-8 h-8 classes")
            
        if img_data['oversized_imgs'] > 0:
            recommendations.append("Add responsive image sizing (h-48 md:h-64 lg:h-80) and object-fit classes")
            
        if section_data['oversized_sections'] > 0:
            recommendations.append("Reduce excessive section padding from py-20+ to py-8 or py-12")
            
        if section_data['estimated_total_height'] > 2500:
            recommendations.append("Optimize section heights to reduce overall page length")
            
        if container_data['width_issues'] > 0:
            recommendations.append("Add max-width constraints to prevent horizontal overflow")
        
        if recommendations:
            print("\n💡 CRITICAL RECOMMENDATIONS")
            print("-" * 30)
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec}")
            print()
        
        # Save detailed report
        report_file = project_root / "debug_output" / "massive_elements_analysis_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Massive Elements Analysis Report\n\n")
            f.write(f"Generated from: {html_file}\n\n")
            
            f.write("## Summary Statistics\n\n")
            f.write(f"- Total SVGs: {svg_data['total_svgs']} ({svg_data['oversized_svgs']} oversized)\n")
            f.write(f"- Total Images: {img_data['total_imgs']} ({img_data['oversized_imgs']} with issues)\n")
            f.write(f"- Total Sections: {section_data['total_sections']} ({section_data['oversized_sections']} oversized)\n")
            f.write(f"- Estimated Page Height: {section_data['estimated_total_height']:,}px\n\n")
            
            if recommendations:
                f.write(f"## Critical Issues Found ({len(recommendations)})\n\n")
                for i, rec in enumerate(recommendations, 1):
                    f.write(f"{i}. {rec}\n")
                f.write("\n")
        
        print(f"📄 Detailed report saved: {report_file}")
        print("✅ Massive elements analysis complete!")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()