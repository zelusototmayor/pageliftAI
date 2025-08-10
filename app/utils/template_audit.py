#!/usr/bin/env python3
"""
Template Design Audit
Analyzes template quality and suggests improvements
"""

import os
import re
from typing import Dict, List, Any

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), '../templates/blocks')

def analyze_template_file(template_path: str) -> Dict[str, Any]:
    """Analyze a single template file for design quality"""
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    analysis = {
        'file': os.path.basename(template_path),
        'size': len(content),
        'issues': [],
        'strengths': [],
        'modernization_score': 0
    }
    
    # Check for modern CSS features
    modern_css_features = {
        'CSS Variables': r'var\(--',
        'CSS Grid': r'grid-',
        'Flexbox': r'flex',
        'Color Mix': r'color-mix',
        'Clamp': r'clamp\(',
        'CSS Custom Properties': r'--[\w-]+:',
        'Modern Gradients': r'linear-gradient|radial-gradient'
    }
    
    for feature, pattern in modern_css_features.items():
        if re.search(pattern, content):
            analysis['strengths'].append(f"Uses {feature}")
            analysis['modernization_score'] += 10
    
    # Check for responsive design
    responsive_patterns = {
        'Mobile-first breakpoints': r'sm:|md:|lg:|xl:',
        'Responsive spacing': r'p-\d|m-\d|py-|px-|my-|mx-',
        'Responsive text': r'text-\w+\s+(sm|md|lg|xl):text-',
        'Responsive layout': r'grid-cols-\d+\s+(md|lg):grid-cols-'
    }
    
    for feature, pattern in responsive_patterns.items():
        if re.search(pattern, content):
            analysis['strengths'].append(f"Has {feature}")
            analysis['modernization_score'] += 8
    
    # Check for accessibility features
    accessibility_features = {
        'Alt text': r'alt="[^"]*"',
        'ARIA labels': r'aria-\w+="',
        'Focus states': r':focus',
        'Semantic markup': r'<(header|main|section|article|aside|nav|footer)',
        'Skip links': r'sr-only'
    }
    
    for feature, pattern in accessibility_features.items():
        if re.search(pattern, content):
            analysis['strengths'].append(f"Includes {feature}")
            analysis['modernization_score'] += 5
    
    # Check for performance considerations
    performance_features = {
        'Lazy loading': r'loading="lazy"',
        'Preload hints': r'fetchpriority="high"',
        'Optimized images': r'object-cover|object-fit'
    }
    
    for feature, pattern in performance_features.items():
        if re.search(pattern, content):
            analysis['strengths'].append(f"Has {feature}")
            analysis['modernization_score'] += 5
    
    # Identify potential issues
    potential_issues = {
        'Hardcoded colors': r'#[0-9a-fA-F]{6}(?!\s*\})',  # Colors not in CSS vars
        'Fixed sizes': r'\d+px(?![^{]*\})',  # Pixel values not in responsive units
        'Missing fallbacks': r'var\(--[^)]*\)(?!\s*,)',  # CSS vars without fallbacks
        'Inline styles': r'style="',
        'Non-semantic classes': r'class="[^"]*\b(div|span|p)\d',
        'Long lines': None  # Will check separately
    }
    
    for issue, pattern in potential_issues.items():
        if issue == 'Long lines':
            long_lines = [i+1 for i, line in enumerate(content.split('\n')) if len(line) > 120]
            if long_lines:
                analysis['issues'].append(f"Long lines: {len(long_lines)} lines exceed 120 chars")
        elif pattern and re.search(pattern, content):
            matches = len(re.findall(pattern, content))
            analysis['issues'].append(f"{issue}: {matches} instances found")
    
    # Calculate overall grade
    if analysis['modernization_score'] >= 80:
        analysis['grade'] = 'A'
        analysis['quality'] = 'Excellent'
    elif analysis['modernization_score'] >= 60:
        analysis['grade'] = 'B'
        analysis['quality'] = 'Good'
    elif analysis['modernization_score'] >= 40:
        analysis['grade'] = 'C'
        analysis['quality'] = 'Average'
    else:
        analysis['grade'] = 'D'
        analysis['quality'] = 'Needs Improvement'
    
    return analysis

def audit_all_templates() -> Dict[str, Any]:
    """Audit all template files"""
    
    template_files = [
        'hero_modern.html',
        'about_responsive.html',
        'services_modern.html',
        'contact_modern.html',
        'gallery_responsive.html',
        'other.html',
        'mixed_responsive.html'
    ]
    
    results = {}
    total_score = 0
    
    print("🔍 Template Design Audit")
    print("=" * 60)
    
    for template_file in template_files:
        template_path = os.path.join(TEMPLATES_DIR, template_file)
        
        if os.path.exists(template_path):
            analysis = analyze_template_file(template_path)
            results[template_file] = analysis
            total_score += analysis['modernization_score']
            
            print(f"\n📄 {template_file}")
            print(f"   Grade: {analysis['grade']} ({analysis['quality']})")
            print(f"   Score: {analysis['modernization_score']}/100")
            print(f"   Size: {analysis['size']} chars")
            
            if analysis['strengths']:
                print(f"   ✅ Strengths ({len(analysis['strengths'])}):")
                for strength in analysis['strengths'][:3]:  # Show top 3
                    print(f"      • {strength}")
                if len(analysis['strengths']) > 3:
                    print(f"      • ... and {len(analysis['strengths']) - 3} more")
            
            if analysis['issues']:
                print(f"   ⚠️  Issues ({len(analysis['issues'])}):")
                for issue in analysis['issues'][:3]:  # Show top 3
                    print(f"      • {issue}")
                if len(analysis['issues']) > 3:
                    print(f"      • ... and {len(analysis['issues']) - 3} more")
        else:
            print(f"\n❌ {template_file} - File not found")
    
    # Overall summary
    avg_score = total_score / len([r for r in results.values()]) if results else 0
    
    print("\n" + "=" * 60)
    print(f"📊 Overall Template Quality")
    print(f"   Average Score: {avg_score:.1f}/100")
    print(f"   Templates Audited: {len(results)}")
    
    if avg_score >= 80:
        print("   🎉 EXCELLENT: Templates are highly modern and professional")
    elif avg_score >= 60:
        print("   ✅ GOOD: Templates are solid with minor improvements needed")
    elif avg_score >= 40:
        print("   ⚠️  AVERAGE: Templates need modernization")
    else:
        print("   ❌ POOR: Templates require significant redesign")
    
    return results

def suggest_improvements(results: Dict[str, Any]) -> List[str]:
    """Generate improvement suggestions based on audit results"""
    
    suggestions = []
    
    # Analyze common issues across templates
    all_issues = []
    low_scoring_templates = []
    
    for template_name, analysis in results.items():
        all_issues.extend(analysis['issues'])
        if analysis['modernization_score'] < 60:
            low_scoring_templates.append(template_name)
    
    # Count issue frequencies
    issue_counts = {}
    for issue in all_issues:
        issue_type = issue.split(':')[0]
        issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
    
    # Generate suggestions based on most common issues
    if 'Hardcoded colors' in issue_counts:
        suggestions.append("Replace hardcoded colors with CSS custom properties for better theme consistency")
    
    if 'Fixed sizes' in issue_counts:
        suggestions.append("Use responsive units (rem, em, %, vw/vh) instead of fixed pixel values")
    
    if 'Long lines' in issue_counts:
        suggestions.append("Break long lines for better code readability and maintenance")
    
    if low_scoring_templates:
        suggestions.append(f"Focus improvement efforts on: {', '.join(low_scoring_templates)}")
    
    # Add general modern design suggestions
    suggestions.extend([
        "Consider adding more CSS animations and micro-interactions",
        "Implement dark mode support using CSS custom properties",
        "Add more sophisticated hover and focus states",
        "Include loading states and skeleton screens for better UX"
    ])
    
    return suggestions

if __name__ == "__main__":
    results = audit_all_templates()
    
    print("\n" + "=" * 60)
    print("💡 Improvement Recommendations")
    
    suggestions = suggest_improvements(results)
    for i, suggestion in enumerate(suggestions[:5], 1):
        print(f"   {i}. {suggestion}")
    
    print(f"\nTemplate audit complete! Review results above.")