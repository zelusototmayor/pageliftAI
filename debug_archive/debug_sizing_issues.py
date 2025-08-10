#!/usr/bin/env python3
"""
Debug Image and Icon Sizing Issues

This script analyzes the generated HTML and CSS to identify why images and icons
appear oversized, causing poor UI quality and long pages.
"""

import sys
import re
import os
from pathlib import Path
from bs4 import BeautifulSoup

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

def analyze_svg_sizing(html_content):
    """Analyze SVG icons for sizing issues"""
    print("\n🔍 SVG ICON SIZING ANALYSIS")
    print("-" * 40)
    
    soup = BeautifulSoup(html_content, 'html.parser')
    svgs = soup.find_all('svg')
    
    sizing_issues = []
    
    print(f"📊 Found {len(svgs)} SVG elements")
    
    for i, svg in enumerate(svgs):
        classes = svg.get('class', [])
        class_str = ' '.join(classes) if isinstance(classes, list) else classes
        
        print(f"\n📐 SVG {i+1}:")
        print(f"   Classes: {class_str}")
        
        # Check for sizing classes
        width_classes = [c for c in class_str.split() if c.startswith('w-')]
        height_classes = [c for c in class_str.split() if c.startswith('h-')]
        
        print(f"   Width classes: {width_classes}")
        print(f"   Height classes: {height_classes}")
        
        # Check for problematic sizing
        if 'w-full' in class_str and 'h-full' in class_str:
            parent = svg.parent
            if parent and not any(limit in str(parent.get('class', '')) for limit in ['w-6', 'w-8', 'w-12', 'max-w', 'container']):
                sizing_issues.append(f"SVG {i+1}: Full-width/height without container limits")
        
        # Check for missing size constraints
        if not width_classes and not height_classes:
            style = svg.get('style', '')
            if 'width:' not in style and 'height:' not in style:
                sizing_issues.append(f"SVG {i+1}: No explicit size constraints")
        
        # Check for oversized classes
        oversized_classes = ['w-24', 'w-32', 'w-48', 'w-64', 'w-96', 'h-24', 'h-32', 'h-48', 'h-64', 'h-96']
        if any(cls in class_str for cls in oversized_classes):
            sizing_issues.append(f"SVG {i+1}: Potentially oversized ({[c for c in oversized_classes if c in class_str]})")
    
    return sizing_issues


def analyze_image_sizing(html_content):
    """Analyze IMG elements for sizing issues"""
    print("\n🔍 IMAGE SIZING ANALYSIS")
    print("-" * 40)
    
    soup = BeautifulSoup(html_content, 'html.parser')
    images = soup.find_all('img')
    
    sizing_issues = []
    
    print(f"📊 Found {len(images)} IMG elements")
    
    for i, img in enumerate(images):
        classes = img.get('class', [])
        class_str = ' '.join(classes) if isinstance(classes, list) else classes
        src = img.get('src', '')
        
        print(f"\n🖼️  IMG {i+1}:")
        print(f"   Classes: {class_str}")
        print(f"   Source: {src[:50]}...")
        
        # Check for sizing classes
        width_classes = [c for c in class_str.split() if c.startswith('w-')]
        height_classes = [c for c in class_str.split() if c.startswith('h-')]
        
        print(f"   Width classes: {width_classes}")
        print(f"   Height classes: {height_classes}")
        
        # Check for problematic sizing
        if 'w-full' in class_str:
            container_classes = ['max-w-', 'container', 'w-64', 'w-96']
            parent = img.parent
            has_container_limit = False
            
            # Check parent chain for size limits
            current = parent
            for _ in range(3):  # Check up to 3 levels up
                if current:
                    parent_classes = ' '.join(current.get('class', []))
                    if any(limit in parent_classes for limit in container_classes):
                        has_container_limit = True
                        break
                    current = current.parent
                else:
                    break
            
            if not has_container_limit:
                sizing_issues.append(f"IMG {i+1}: Full-width without container limits")
        
        # Check for explicit oversized dimensions
        oversized_heights = ['h-96', 'h-screen', 'min-h-screen', 'h-[500px]', 'h-[600px]', 'h-[800px]']
        if any(cls in class_str for cls in oversized_heights):
            sizing_issues.append(f"IMG {i+1}: Potentially oversized height ({[c for c in oversized_heights if c in class_str]})")
        
        # Check for missing object-fit classes
        if 'w-full' in class_str or 'h-' in class_str:
            if not any(fit in class_str for fit in ['object-cover', 'object-contain', 'object-fit']):
                sizing_issues.append(f"IMG {i+1}: Missing object-fit class for responsive image")
    
    return sizing_issues


def analyze_section_sizing(html_content):
    """Analyze section height and padding for page length issues"""
    print("\n🔍 SECTION SIZING ANALYSIS")
    print("-" * 40)
    
    soup = BeautifulSoup(html_content, 'html.parser')
    sections = soup.find_all('section')
    
    sizing_issues = []
    total_estimated_height = 0
    
    print(f"📊 Found {len(sections)} sections")
    
    for i, section in enumerate(sections):
        classes = section.get('class', [])
        class_str = ' '.join(classes) if isinstance(classes, list) else classes
        section_id = section.get('data-section-id', i)
        category = section.get('data-category', 'unknown')
        
        print(f"\n📄 Section {section_id} ({category}):")
        print(f"   Classes: {class_str}")
        
        # Analyze height classes
        height_classes = [c for c in class_str.split() if 'h-' in c or 'min-h' in c]
        padding_classes = [c for c in class_str.split() if c.startswith('py-') or c.startswith('pt-') or c.startswith('pb-')]
        
        print(f"   Height classes: {height_classes}")
        print(f"   Padding classes: {padding_classes}")
        
        # Estimate section height in pixels (rough calculation)
        estimated_height = 0
        
        # Height estimation
        if 'min-h-screen' in class_str:
            estimated_height += 800  # Rough screen height
            sizing_issues.append(f"Section {section_id}: Uses screen height (may cause very long pages)")
        elif 'min-h-[600px]' in class_str or 'h-[600px]' in class_str:
            estimated_height += 600
        elif 'min-h-[500px]' in class_str or 'h-[500px]' in class_str:
            estimated_height += 500
        elif 'min-h-[400px]' in class_str or 'h-[400px]' in class_str:
            estimated_height += 400
        elif 'min-h-[300px]' in class_str:
            estimated_height += 300
        elif 'min-h-[250px]' in class_str:
            estimated_height += 250
        elif 'min-h-[200px]' in class_str:
            estimated_height += 200
        else:
            estimated_height += 150  # Default content height
        
        # Padding estimation (top + bottom)
        for cls in padding_classes:
            if 'py-24' in cls:
                estimated_height += 384  # 24 * 16px = 384px top+bottom
                sizing_issues.append(f"Section {section_id}: Excessive padding (py-24 = 384px)")
            elif 'py-20' in cls:
                estimated_height += 320
                sizing_issues.append(f"Section {section_id}: Very large padding (py-20 = 320px)")
            elif 'py-16' in cls:
                estimated_height += 256
            elif 'py-12' in cls:
                estimated_height += 192
            elif 'py-10' in cls:
                estimated_height += 160
            elif 'py-8' in cls:
                estimated_height += 128
            elif 'py-6' in cls:
                estimated_height += 96
        
        print(f"   Estimated height: ~{estimated_height}px")
        total_estimated_height += estimated_height
        
        if estimated_height > 600:
            sizing_issues.append(f"Section {section_id}: Very tall section (~{estimated_height}px)")
    
    print(f"\n📏 Total estimated page height: ~{total_estimated_height}px")
    if total_estimated_height > 5000:
        sizing_issues.append(f"Overall page: Extremely long page (~{total_estimated_height}px)")
    elif total_estimated_height > 3000:
        sizing_issues.append(f"Overall page: Very long page (~{total_estimated_height}px)")
    
    return sizing_issues


def analyze_responsive_breakpoints(html_content):
    """Analyze responsive design for mobile vs desktop sizing"""
    print("\n🔍 RESPONSIVE DESIGN ANALYSIS")
    print("-" * 40)
    
    # Count responsive classes
    responsive_patterns = {
        'sm:': re.findall(r'sm:[\w-]+', html_content),
        'md:': re.findall(r'md:[\w-]+', html_content),
        'lg:': re.findall(r'lg:[\w-]+', html_content),
        'xl:': re.findall(r'xl:[\w-]+', html_content),
    }
    
    issues = []
    
    for breakpoint, matches in responsive_patterns.items():
        print(f"📱 {breakpoint} classes: {len(matches)}")
        
        # Check for responsive sizing
        size_matches = [m for m in matches if any(prefix in m for prefix in ['w-', 'h-', 'text-', 'py-', 'px-'])]
        print(f"   Sizing responsive classes: {len(size_matches)}")
    
    total_responsive = sum(len(matches) for matches in responsive_patterns.values())
    
    # Count non-responsive classes that could benefit from responsiveness
    base_sizing_classes = re.findall(r'\b(?:w-\d+|h-\d+|py-\d+|px-\d+|text-\w+)\b', html_content)
    non_responsive_sizing = len([c for c in base_sizing_classes if not any(f'{bp}{c}' in html_content for bp in ['sm:', 'md:', 'lg:', 'xl:'])])
    
    print(f"\n📊 Total responsive classes: {total_responsive}")
    print(f"📊 Non-responsive sizing classes: {non_responsive_sizing}")
    
    if total_responsive < 50:
        issues.append("Low responsive class usage - may not scale well across devices")
    
    if non_responsive_sizing > total_responsive:
        issues.append("More non-responsive sizing than responsive - may cause mobile issues")
    
    return issues


def generate_sizing_fix_recommendations(all_issues):
    """Generate specific recommendations to fix sizing issues"""
    print("\n🔧 SIZING FIX RECOMMENDATIONS")
    print("=" * 50)
    
    recommendations = []
    
    # Analyze issue patterns
    svg_issues = [issue for issue in all_issues if 'SVG' in issue]
    img_issues = [issue for issue in all_issues if 'IMG' in issue]
    section_issues = [issue for issue in all_issues if 'Section' in issue]
    page_issues = [issue for issue in all_issues if 'Overall page' in issue]
    
    if svg_issues:
        print("\n🎯 SVG Icon Fixes:")
        recommendations.extend([
            "Add max-width/max-height constraints to SVG containers",
            "Use consistent icon sizing classes (w-4 h-4, w-6 h-6, w-8 h-8)",
            "Add default SVG size limits in CSS variables",
            "Implement icon size variants based on context (button, card, hero)"
        ])
        for issue in svg_issues[:3]:  # Show top 3 issues
            print(f"   • {issue}")
    
    if img_issues:
        print("\n🎯 Image Sizing Fixes:")
        recommendations.extend([
            "Add object-cover/object-contain classes to all responsive images",
            "Implement consistent image aspect ratios",
            "Add max-height constraints to prevent oversized images",
            "Use responsive image sizing (sm:h-48 md:h-64 lg:h-80)"
        ])
        for issue in img_issues[:3]:
            print(f"   • {issue}")
    
    if section_issues:
        print("\n🎯 Section Sizing Fixes:")
        recommendations.extend([
            "Reduce excessive padding (py-24 → py-12, py-20 → py-16)",
            "Use responsive padding (py-6 sm:py-8 lg:py-12)",
            "Replace min-h-screen with reasonable fixed heights",
            "Implement content-based height instead of fixed heights"
        ])
        for issue in section_issues[:3]:
            print(f"   • {issue}")
    
    if page_issues:
        print("\n🎯 Page Length Fixes:")
        recommendations.extend([
            "Implement section height limits based on content",
            "Use compact layouts for sections with minimal content",
            "Add scroll-based lazy loading for long pages",
            "Optimize vertical spacing between sections"
        ])
    
    print(f"\n📋 Total recommendations: {len(recommendations)}")
    return recommendations


def main():
    """Run comprehensive sizing analysis"""
    print("🔍 IMAGE & ICON SIZING ISSUE ANALYSIS")
    print("=" * 60)
    
    # Read the generated HTML
    html_file = "/Users/zelu/Desktop/code/PageLift AI/debug_output/debug_generated_website.html"
    
    if not os.path.exists(html_file):
        print(f"❌ HTML file not found: {html_file}")
        print("Please run debug_template_rendering_issues.py first to generate the HTML")
        return False
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print(f"📄 Analyzing HTML file: {len(html_content):,} characters")
    
    all_issues = []
    
    # Run all analyses
    all_issues.extend(analyze_svg_sizing(html_content))
    all_issues.extend(analyze_image_sizing(html_content))
    all_issues.extend(analyze_section_sizing(html_content))
    all_issues.extend(analyze_responsive_breakpoints(html_content))
    
    # Generate recommendations
    recommendations = generate_sizing_fix_recommendations(all_issues)
    
    # Final summary
    print(f"\n📊 ANALYSIS SUMMARY")
    print("=" * 30)
    print(f"Total sizing issues found: {len(all_issues)}")
    print(f"Fix recommendations: {len(recommendations)}")
    
    if all_issues:
        print(f"\n❌ TOP ISSUES:")
        for i, issue in enumerate(all_issues[:10], 1):
            print(f"   {i:2d}. {issue}")
    else:
        print(f"\n✅ No major sizing issues detected!")
    
    # Save detailed report
    report_file = "/Users/zelu/Desktop/code/PageLift AI/debug_output/sizing_analysis_report.md"
    with open(report_file, 'w') as f:
        f.write("# Image & Icon Sizing Analysis Report\n\n")
        f.write(f"Generated from: {html_file}\n\n")
        f.write(f"## Issues Found ({len(all_issues)})\n\n")
        for i, issue in enumerate(all_issues, 1):
            f.write(f"{i}. {issue}\n")
        f.write(f"\n## Recommendations ({len(recommendations)})\n\n")
        for i, rec in enumerate(recommendations, 1):
            f.write(f"{i}. {rec}\n")
    
    print(f"\n📁 Detailed report saved to: {report_file}")
    
    return len(all_issues) == 0


if __name__ == "__main__":
    success = main()
    print(f"\nSizing analysis complete.")
    sys.exit(0 if success else 1)