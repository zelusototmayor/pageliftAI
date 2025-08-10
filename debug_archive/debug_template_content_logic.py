#!/usr/bin/env python3
"""
Debug Template Content Logic
Analyzes why templates generate infinite placeholders instead of using original content.
"""

import os
import sys
import re
from pathlib import Path
from bs4 import BeautifulSoup

# Add project root to Python path  
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def analyze_template_logic_issues():
    """Analyze templates to find why they generate placeholders instead of real content."""
    
    print("🔍 Analyzing Template Content Logic Issues...")
    print("=" * 60)
    
    template_dir = project_root / "app" / "templates" / "blocks"
    issues_found = []
    
    # Key templates that likely cause infinite content
    problematic_templates = [
        "services_modern.html",
        "gallery_responsive.html", 
        "about_responsive.html"
    ]
    
    for template_name in problematic_templates:
        template_file = template_dir / template_name
        if not template_file.exists():
            continue
            
        print(f"\n📄 Analyzing {template_name}...")
        
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 1. Check for loops that generate multiple placeholder items
        loop_patterns = [
            (r'{% for \w+ in [\w\.\[\]:]+\s*%}', 'Jinja for loop'),
            (r'{% for \w+ in range\(\d+\)', 'Range-based loop generating fixed items'),
            (r'{{ loop\.index }}', 'Loop index usage (may generate numbered items)'),
        ]
        
        template_issues = []
        
        for pattern, description in loop_patterns:
            matches = re.findall(pattern, content)
            if matches:
                template_issues.append(f"  ⚠️  {description}: {len(matches)} instances")
                
        # 2. Check for hardcoded service/item generation
        hardcoded_patterns = [
            (r'rich_services\s*=\s*\[', 'Hardcoded service list generation'),
            (r'standard_services\s*=\s*\[', 'Hardcoded standard services'),
            (r'{% set [\w_]+ = \[.*?\]', 'Hardcoded item arrays'),
        ]
        
        for pattern, description in hardcoded_patterns:
            if re.search(pattern, content, re.DOTALL):
                template_issues.append(f"  🔴 {description}")
        
        # 3. Check for image loops without proper bounds
        image_loop_patterns = [
            (r'{% for image in image_set\.all_images.*?%}', 'Image set iteration'),
            (r'{% for image in [\w\.\[\]]+\[:\d+\]', 'Limited image iteration (good)'),
            (r'{% for image in [\w\.\[\]]+\s*%}(?!\s*.*\[:\d+\])', 'Unbounded image iteration'),
        ]
        
        for pattern, description in image_loop_patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            if matches:
                template_issues.append(f"  🖼️  {description}: {len(matches)} instances")
        
        # 4. Check for conditional logic that defaults to placeholder generation
        placeholder_patterns = [
            (r'{% else %}.*?<!-- .*(Placeholder|placeholder).*? -->', 'Placeholder fallbacks'),
            (r'Professional Service \d+', 'Generic numbered services'),
            (r'Service \d+', 'Generic numbered service items'),
        ]
        
        for pattern, description in placeholder_patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            if matches:
                template_issues.append(f"  📝 {description}: {len(matches)} instances")
        
        if template_issues:
            print(f"  Found {len(template_issues)} issues:")
            for issue in template_issues:
                print(issue)
            issues_found.extend([(template_name, issue) for issue in template_issues])
        else:
            print(f"  ✅ No obvious content generation issues")
    
    return issues_found

def analyze_website_data_usage():
    """Analyze how templates use actual website data vs placeholders."""
    
    print(f"\n🔍 Analyzing Website Data Usage...")
    print("-" * 40)
    
    # Read the generated website to see what data was actually used
    html_file = project_root / "debug_output" / "debug_generated_website.html"
    
    if not html_file.exists():
        print("❌ No generated website found. Run pipeline first.")
        return {}
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Look for evidence of placeholder vs real content
    analysis = {
        'placeholder_services': 0,
        'real_content_sections': 0,
        'generic_titles': 0,
        'repeated_content': 0
    }
    
    # Count generic/placeholder service titles
    service_titles = soup.find_all(['h3', 'h4'])
    for title in service_titles:
        text = title.get_text().strip()
        if re.match(r'(Professional )?Service \d+', text):
            analysis['placeholder_services'] += 1
        elif 'Professional Service' in text and text == 'Professional Service':
            analysis['placeholder_services'] += 1
    
    # Count generic titles/headings
    all_headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
    for heading in all_headings:
        text = heading.get_text().strip()
        if text in ['Professional Service', 'Expert Service', 'Our Services', 'About Our Company']:
            analysis['generic_titles'] += 1
    
    # Look for repeated identical content
    paragraphs = soup.find_all('p')
    paragraph_texts = [p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 20]
    
    # Count duplicates
    from collections import Counter
    text_counts = Counter(paragraph_texts)
    analysis['repeated_content'] = sum(count - 1 for count in text_counts.values() if count > 1)
    
    print(f"Placeholder services found: {analysis['placeholder_services']}")
    print(f"Generic titles found: {analysis['generic_titles']}")
    print(f"Repeated content instances: {analysis['repeated_content']}")
    
    return analysis

def find_root_cause():
    """Identify the root cause of placeholder generation."""
    
    print(f"\n🎯 ROOT CAUSE ANALYSIS")
    print("-" * 30)
    
    # The key issue is likely in services_modern.html where it generates hardcoded services
    services_template = project_root / "app" / "templates" / "blocks" / "services_modern.html"
    
    if services_template.exists():
        with open(services_template, 'r') as f:
            content = f.read()
        
        # Look for the problematic sections
        issues = []
        
        # Check for hardcoded service arrays
        if 'rich_services = [' in content:
            issues.append("❗ CRITICAL: Hardcoded 'rich_services' array generates up to 4 placeholder services")
        
        if 'standard_services = [' in content:
            issues.append("❗ CRITICAL: Hardcoded 'standard_services' array generates up to 6 placeholder services")
        
        # Check for image loops
        if 'for image in image_set.all_images' in content:
            if '[:9]' in content:
                issues.append("❗ CRITICAL: Loop generates up to 9 service cards from images")
            if '[:6]' in content:
                issues.append("❗ CRITICAL: Loop generates up to 6 service cards from images")
        
        # Check for industry-specific content generation
        if 'if industry ==' in content and 'plumbing' in content:
            issues.append("❗ CRITICAL: Industry-specific hardcoded content generates multiple services")
        
        if issues:
            print("ROOT CAUSES IDENTIFIED:")
            for issue in issues:
                print(f"  {issue}")
        else:
            print("No obvious root causes found in services template")
    
    # Check other problematic areas
    print(f"\nKEY PROBLEMS:")
    print("1. Templates have hardcoded service arrays instead of using parsed website data")
    print("2. Image loops create placeholder services when no real services exist") 
    print("3. Industry-specific logic generates content rather than using original site structure")
    print("4. Fallback logic creates placeholders instead of using minimal real content")

def main():
    """Main analysis function."""
    
    print("🚨 DEBUGGING: Why Templates Generate Infinite Placeholders")
    print("=" * 70)
    
    # Analyze template logic issues
    template_issues = analyze_template_logic_issues()
    
    # Analyze actual data usage
    data_usage = analyze_website_data_usage()
    
    # Find root cause
    find_root_cause()
    
    # Provide solution recommendations
    print(f"\n💡 SOLUTION RECOMMENDATIONS")
    print("-" * 35)
    print("1. REMOVE hardcoded service arrays from templates")
    print("2. LIMIT image-to-service generation (max 3 services)")
    print("3. USE original website's actual service text/structure") 
    print("4. FALLBACK to minimal content, not placeholder generation")
    print("5. PREVENT infinite loops in service/content generation")
    
    return len(template_issues)

if __name__ == "__main__":
    issues_count = main()
    exit(0 if issues_count == 0 else 1)