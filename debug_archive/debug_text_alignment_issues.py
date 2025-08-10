#!/usr/bin/env python3
"""
Debug Text Alignment and Layout Issues in Generated Sites
Analyzes HTML output for text alignment problems and layout issues.
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

def analyze_text_alignment_issues(html_content: str) -> Dict[str, Any]:
    """Analyze HTML for text alignment and layout issues."""
    
    soup = BeautifulSoup(html_content, 'html.parser')
    issues = []
    recommendations = []
    
    # 1. Check for left-aligned text issues
    text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div', 'span'])
    left_aligned_count = 0
    center_aligned_count = 0
    justified_count = 0
    no_alignment_count = 0
    
    for elem in text_elements:
        classes = elem.get('class', [])
        class_str = ' '.join(classes) if classes else ''
        
        # Check text alignment classes
        if 'text-left' in classes:
            left_aligned_count += 1
        elif 'text-center' in classes:
            center_aligned_count += 1
        elif 'text-justify' in classes:
            justified_count += 1
        else:
            no_alignment_count += 1
            # Check for missing text alignment on important elements
            if elem.name in ['h1', 'h2', 'h3'] and len(elem.get_text().strip()) > 0:
                issues.append(f"Header {elem.name.upper()} missing text alignment class: '{elem.get_text()[:50]}...'")
    
    # 2. Check for responsive text alignment
    responsive_text_classes = ['sm:text-center', 'md:text-center', 'lg:text-center', 
                               'sm:text-left', 'md:text-left', 'lg:text-left']
    responsive_text_count = 0
    for elem in text_elements:
        classes = elem.get('class', [])
        if any(cls in classes for cls in responsive_text_classes):
            responsive_text_count += 1
    
    # 3. Check for layout container issues
    containers = soup.find_all(['div', 'section', 'header', 'main'])
    container_issues = []
    proper_containers = 0
    
    for container in containers:
        classes = container.get('class', [])
        class_str = ' '.join(classes)
        
        # Check for proper container classes
        if 'container' in classes or 'max-w-' in class_str:
            proper_containers += 1
        elif container.name == 'section' and 'w-full' in classes:
            # Full-width sections should have inner containers
            inner_containers = container.find_all(['div'], class_=lambda x: x and ('container' in x or 'max-w-' in ' '.join(x)))
            if not inner_containers:
                container_issues.append(f"Section missing inner container for content width control")
    
    # 4. Check for text wrapping and overflow issues
    text_overflow_issues = []
    long_text_elements = soup.find_all(string=lambda text: text and len(text.strip()) > 100)
    
    for text_elem in long_text_elements[:10]:  # Check first 10 long text elements
        parent = text_elem.parent
        if parent:
            classes = parent.get('class', [])
            class_str = ' '.join(classes)
            
            # Check for text overflow prevention
            has_overflow_protection = any(cls in class_str for cls in ['break-words', 'overflow-hidden', 'truncate', 'text-ellipsis'])
            if not has_overflow_protection:
                text_overflow_issues.append(f"Long text without overflow protection: '{str(text_elem)[:60]}...'")
    
    # 5. Check for mobile-first responsive design
    mobile_responsive_issues = []
    all_elements = soup.find_all(True)
    mobile_first_count = 0
    desktop_first_count = 0
    
    for elem in all_elements:
        classes = elem.get('class', [])
        class_str = ' '.join(classes)
        
        # Check for mobile-first vs desktop-first patterns
        if re.search(r'\b(sm:|md:|lg:)', class_str):
            mobile_first_count += 1
        elif re.search(r'\b(text-\w+|p-\d+|m-\d+)\b(?!\s*sm:|md:|lg:)', class_str):
            desktop_first_count += 1
    
    # Generate issues and recommendations
    if left_aligned_count > center_aligned_count * 2:
        issues.append(f"Excessive left alignment: {left_aligned_count} left vs {center_aligned_count} center aligned elements")
        recommendations.append("Consider center-aligning headers and key content for better visual hierarchy")
    
    if responsive_text_count == 0:
        issues.append("No responsive text alignment classes found")
        recommendations.append("Add responsive text alignment (sm:text-center, md:text-left, etc.)")
    
    if len(container_issues) > 0:
        issues.extend(container_issues)
        recommendations.append("Add proper container classes (container, max-w-4xl, etc.) for content width control")
    
    if len(text_overflow_issues) > 3:
        issues.append(f"Multiple text overflow risks: {len(text_overflow_issues)} elements")
        recommendations.append("Add text overflow protection classes (break-words, overflow-hidden)")
    
    if no_alignment_count > (left_aligned_count + center_aligned_count):
        issues.append(f"Many elements missing explicit text alignment: {no_alignment_count}")
        recommendations.append("Add explicit text alignment classes to improve consistency")
    
    return {
        'total_text_elements': len(text_elements),
        'alignment_stats': {
            'left_aligned': left_aligned_count,
            'center_aligned': center_aligned_count,
            'justified': justified_count,
            'no_alignment': no_alignment_count
        },
        'responsive_text_elements': responsive_text_count,
        'container_stats': {
            'total_containers': len(containers),
            'proper_containers': proper_containers
        },
        'text_overflow_risks': len(text_overflow_issues),
        'responsive_design': {
            'mobile_first_elements': mobile_first_count,
            'desktop_first_elements': desktop_first_count
        },
        'issues': issues,
        'recommendations': recommendations
    }

def main():
    """Main execution function."""
    
    print("🔍 Analyzing Text Alignment and Layout Issues...")
    print("=" * 60)
    
    # Read the generated website HTML
    html_file = project_root / "debug_output" / "debug_generated_website.html"
    
    if not html_file.exists():
        print(f"❌ HTML file not found: {html_file}")
        return
    
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        print(f"📄 Analyzing HTML file: {html_file}")
        print(f"📊 File size: {len(html_content):,} characters")
        print()
        
        # Analyze text alignment issues
        analysis = analyze_text_alignment_issues(html_content)
        
        # Print results
        print("📈 TEXT ALIGNMENT & LAYOUT ANALYSIS")
        print("-" * 40)
        print(f"Total text elements analyzed: {analysis['total_text_elements']}")
        print(f"Responsive text elements: {analysis['responsive_text_elements']}")
        print(f"Text overflow risks: {analysis['text_overflow_risks']}")
        print()
        
        print("📊 ALIGNMENT STATISTICS")
        stats = analysis['alignment_stats']
        print(f"  • Left aligned: {stats['left_aligned']}")
        print(f"  • Center aligned: {stats['center_aligned']}")
        print(f"  • Justified: {stats['justified']}")
        print(f"  • No explicit alignment: {stats['no_alignment']}")
        print()
        
        print("📦 CONTAINER STATISTICS")
        container_stats = analysis['container_stats']
        print(f"  • Total containers: {container_stats['total_containers']}")
        print(f"  • Proper containers: {container_stats['proper_containers']}")
        print()
        
        print("📱 RESPONSIVE DESIGN")
        responsive = analysis['responsive_design']
        print(f"  • Mobile-first elements: {responsive['mobile_first_elements']}")
        print(f"  • Desktop-first elements: {responsive['desktop_first_elements']}")
        print()
        
        # Print issues
        if analysis['issues']:
            print(f"⚠️  ISSUES FOUND ({len(analysis['issues'])})")
            for i, issue in enumerate(analysis['issues'], 1):
                print(f"{i:2d}. {issue}")
            print()
        
        # Print recommendations
        if analysis['recommendations']:
            print(f"💡 RECOMMENDATIONS ({len(analysis['recommendations'])})")
            for i, rec in enumerate(analysis['recommendations'], 1):
                print(f"{i:2d}. {rec}")
            print()
        
        # Save detailed report
        report_file = project_root / "debug_output" / "text_alignment_analysis_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Text Alignment & Layout Analysis Report\n\n")
            f.write(f"Generated from: {html_file}\n\n")
            
            f.write("## Statistics\n\n")
            f.write(f"- Total text elements: {analysis['total_text_elements']}\n")
            f.write(f"- Responsive text elements: {analysis['responsive_text_elements']}\n")
            f.write(f"- Text overflow risks: {analysis['text_overflow_risks']}\n\n")
            
            f.write("### Alignment Distribution\n\n")
            f.write(f"- Left aligned: {stats['left_aligned']}\n")
            f.write(f"- Center aligned: {stats['center_aligned']}\n") 
            f.write(f"- Justified: {stats['justified']}\n")
            f.write(f"- No explicit alignment: {stats['no_alignment']}\n\n")
            
            if analysis['issues']:
                f.write(f"## Issues Found ({len(analysis['issues'])})\n\n")
                for i, issue in enumerate(analysis['issues'], 1):
                    f.write(f"{i}. {issue}\n")
                f.write("\n")
            
            if analysis['recommendations']:
                f.write(f"## Recommendations ({len(analysis['recommendations'])})\n\n")
                for i, rec in enumerate(analysis['recommendations'], 1):
                    f.write(f"{i}. {rec}\n")
                f.write("\n")
        
        print(f"📄 Detailed report saved: {report_file}")
        print("✅ Text alignment analysis complete!")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()