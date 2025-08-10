#!/usr/bin/env python3
"""
Comprehensive PageLift AI Pipeline Debugging Script

This script exercises the complete pipeline end-to-end to identify why generated websites
have poor quality (major icons, long pages, left-aligned text, no UI styling).

Focus areas:
1. Template context preparation and data flow
2. Image/icon sizing and processing
3. Brand identity extraction and color handling
4. Template selection and rendering logic
5. CSS generation and styling application
"""

import os
import sys
import json
import tempfile
import zipfile
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.scrape import scrape_site
from app.services.parse import parse_html_sections
from app.services.analyze import analyze_sections
from app.services.brand_extraction import extract_brand_identity
from app.services.render import render_site_with_brand, prepare_section_for_rendering
from app.services.image_processing import process_section_images
from app.services.proportional_sizing import apply_proportional_sizing_to_sections
from app.services.css_generator import generate_brand_css
from app.services.typography import create_typography_system


def print_section_divider(title: str):
    """Print a formatted section divider"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}")


def print_subsection(title: str):
    """Print a formatted subsection header"""
    print(f"\n{'-'*60}")
    print(f"  {title}")
    print(f"{'-'*60}")


def analyze_template_context_issues(sections_data, brand_identity):
    """Analyze template context preparation for issues"""
    print_subsection("TEMPLATE CONTEXT ANALYSIS")
    
    issues_found = []
    
    for i, section in enumerate(sections_data):
        print(f"\n📊 Section {i} Context Analysis:")
        print(f"   • Category: {section.get('category', 'MISSING')}")
        print(f"   • Has heading: {bool(section.get('heading'))}")
        print(f"   • Content length: {len(section.get('short_copy', ''))}")
        print(f"   • Image count: {len(section.get('img_urls', []))}")
        print(f"   • Has business data: {bool(section.get('business_data'))}")
        
        # Check for template context preparation
        try:
            prepared = prepare_section_for_rendering(section)
            print(f"   • Template context keys: {list(prepared.keys())}")
            
            # Check for missing critical data
            if 'sizing' not in prepared:
                issues_found.append(f"Section {i}: Missing sizing data")
            if 'image_set' not in prepared:
                issues_found.append(f"Section {i}: Missing image_set data")
            if 'typography' not in prepared:
                issues_found.append(f"Section {i}: Missing typography data")
                
        except Exception as e:
            issues_found.append(f"Section {i}: Context preparation failed - {e}")
            print(f"   ❌ Context preparation failed: {e}")
    
    # Check brand identity structure
    print(f"\n🎨 Brand Identity Structure:")
    if isinstance(brand_identity, dict):
        print(f"   • Colors: {brand_identity.get('colors', {}).keys() if brand_identity.get('colors') else 'MISSING'}")
        print(f"   • Typography: {brand_identity.get('typography', {}).keys() if brand_identity.get('typography') else 'MISSING'}")
        print(f"   • Style: {brand_identity.get('style', {}).keys() if brand_identity.get('style') else 'MISSING'}")
        
        # Check for problematic colors
        colors = brand_identity.get('colors', {})
        primary = colors.get('primary', '').lower()
        if primary in ['#ffffff', '#fff', 'white', '']:
            issues_found.append("Primary color is white/missing - will cause invisible text")
        
        background = colors.get('background', '').lower() 
        if background in ['#ffffff', '#fff', 'white'] and primary in ['#ffffff', '#fff', 'white']:
            issues_found.append("White text on white background - visibility issue")
    else:
        issues_found.append("Brand identity is not a dictionary")
    
    return issues_found


def analyze_image_sizing_issues(sections_with_sizing, brand_identity):
    """Analyze image processing and sizing for issues"""
    print_subsection("IMAGE & SIZING ANALYSIS")
    
    issues_found = []
    
    for i, section in enumerate(sections_with_sizing):
        print(f"\n🖼️  Section {i} Image Analysis:")
        
        # Test image processing
        try:
            image_set = process_section_images(section, brand_identity)
            print(f"   • Primary image: {bool(image_set.primary_image)}")
            print(f"   • Total images: {len(image_set.images)}")
            print(f"   • Hero images: {len(image_set.hero_images)}")
            print(f"   • Gallery images: {len(image_set.gallery_images)}")
            
            # Check for oversized images
            if len(image_set.images) > 10:
                issues_found.append(f"Section {i}: Too many images ({len(image_set.images)}) - may cause layout issues")
                
        except Exception as e:
            issues_found.append(f"Section {i}: Image processing failed - {e}")
            print(f"   ❌ Image processing failed: {e}")
        
        # Check sizing data
        sizing = section.get('sizing', {})
        print(f"   • Sizing data: {list(sizing.keys()) if sizing else 'MISSING'}")
        
        if sizing:
            section_padding = sizing.get('section_padding')
            height_class = sizing.get('height_class')
            if not section_padding or not height_class:
                issues_found.append(f"Section {i}: Incomplete sizing data")
        else:
            issues_found.append(f"Section {i}: No proportional sizing applied")
    
    return issues_found


def analyze_css_generation_issues(brand_identity, typography):
    """Analyze CSS generation for styling issues"""
    print_subsection("CSS GENERATION ANALYSIS")
    
    issues_found = []
    
    try:
        # Test brand CSS generation
        brand_css = generate_brand_css(brand_identity, typography)
        print(f"   • Brand CSS length: {len(brand_css)} characters")
        print(f"   • CSS preview: {brand_css[:200]}..." if brand_css else "   ❌ No CSS generated")
        
        if len(brand_css) < 500:
            issues_found.append("Generated CSS is suspiciously short - may be incomplete")
        
        # Check for critical CSS rules
        if '--brand-primary' not in brand_css:
            issues_found.append("Missing primary brand color variable in CSS")
        if 'font-family' not in brand_css:
            issues_found.append("Missing font-family rules in CSS")
            
    except Exception as e:
        issues_found.append(f"CSS generation failed: {e}")
        print(f"   ❌ CSS generation failed: {e}")
    
    # Test typography system
    try:
        print(f"   • Typography CSS length: {len(typography.get_typography_css()) if hasattr(typography, 'get_typography_css') else 0}")
        print(f"   • Font imports: {typography.get_font_imports() if hasattr(typography, 'get_font_imports') else 'MISSING'}")
    except Exception as e:
        issues_found.append(f"Typography CSS generation failed: {e}")
    
    return issues_found


def test_template_rendering(sections_with_context, brand_identity, title="Test Site"):
    """Test template rendering and identify issues"""
    print_subsection("TEMPLATE RENDERING TEST")
    
    issues_found = []
    
    try:
        # Test the full rendering process
        zip_path = render_site_with_brand(sections_with_context, brand_identity, title)
        print(f"   ✅ Site rendered successfully to: {zip_path}")
        
        # Extract and analyze the generated HTML
        with tempfile.TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
                
            # Read the generated HTML
            html_path = os.path.join(temp_dir, 'index.html')
            if os.path.exists(html_path):
                with open(html_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                print(f"   • Generated HTML length: {len(html_content):,} characters")
                
                # Analyze HTML for issues
                if len(html_content) < 5000:
                    issues_found.append("Generated HTML is very short - may be missing content")
                elif len(html_content) > 100000:
                    issues_found.append("Generated HTML is extremely long - may have duplication issues")
                
                # Check for styling issues
                if 'class="loading"' in html_content:
                    loading_count = html_content.count('class="loading"')
                    print(f"   • Found {loading_count} sections with loading animation")
                
                if '--brand-primary' not in html_content:
                    issues_found.append("Brand CSS variables missing from generated HTML")
                
                # Check for layout issues  
                if 'text-left' in html_content and 'text-center' not in html_content:
                    issues_found.append("All text may be left-aligned - check responsive design")
                
                # Check for icon/image issues
                svg_count = html_content.count('<svg')
                img_count = html_content.count('<img')
                print(f"   • SVG icons: {svg_count}, Images: {img_count}")
                
                if svg_count > 50:
                    issues_found.append(f"Excessive SVG icons ({svg_count}) - may cause visual overload")
                
                # Check for section duplication
                section_count = html_content.count('data-section-id=')
                if section_count != len(sections_with_context):
                    issues_found.append(f"Section count mismatch: expected {len(sections_with_context)}, found {section_count}")
                
                # Save HTML for manual inspection
                debug_html_path = "/Users/zelu/Desktop/code/PageLift AI/debug_output/debug_generated_site.html"
                with open(debug_html_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print(f"   📁 HTML saved for inspection: {debug_html_path}")
                
            else:
                issues_found.append("Generated ZIP does not contain index.html")
        
    except Exception as e:
        issues_found.append(f"Template rendering failed: {e}")
        print(f"   ❌ Rendering failed: {e}")
    
    return issues_found


def debug_pipeline_comprehensive(url="https://desentopecanalizacoes.pt/"):
    """Run comprehensive pipeline debugging"""
    print_section_divider("COMPREHENSIVE PAGELIFT PIPELINE DEBUGGING")
    print(f"🔍 Testing URL: {url}")
    
    all_issues = []
    
    # Phase 1: Data Extraction
    print_section_divider("PHASE 1: DATA EXTRACTION")
    
    try:
        # Scraping
        print("1️⃣ Scraping website...")
        scrape_result = scrape_site(url)
        html = scrape_result.pages[0].html
        print(f"   ✅ Scraped {len(html):,} characters")
        
        # Parsing
        print("2️⃣ Parsing HTML sections...")
        sections = parse_html_sections(html)
        section_dicts = [s.__dict__ for s in sections]
        print(f"   ✅ Extracted {len(sections)} sections")
        
        # Analysis
        print("3️⃣ Analyzing sections with AI...")
        analyses = analyze_sections(section_dicts)
        print(f"   ✅ Analyzed {len(analyses)} sections")
        
        # Print analysis summary
        categories = {}
        for analysis in analyses:
            cat = analysis.category
            categories[cat] = categories.get(cat, 0) + 1
        print(f"   📊 Categories: {categories}")
        
    except Exception as e:
        print(f"   ❌ Data extraction failed: {e}")
        return [f"Pipeline failed at data extraction: {e}"]
    
    # Phase 2: Brand & Enhancement Processing
    print_section_divider("PHASE 2: BRAND & ENHANCEMENT PROCESSING")
    
    try:
        # Brand extraction
        print("4️⃣ Extracting brand identity...")
        brand_identity_obj = extract_brand_identity(url, html)
        print(f"   ✅ Brand identity extracted")
        print(f"   🎨 Colors: {brand_identity_obj.colors.primary} / {brand_identity_obj.colors.secondary}")
        print(f"   📝 Typography: {brand_identity_obj.typography.primary_font}")
        
        # Convert to expected format
        brand_identity = {
            'brand': {
                'industry': brand_identity_obj.industry,
                'tone': brand_identity_obj.tone,
                'layout_preference': brand_identity_obj.layout_preference,
                'image_style': brand_identity_obj.image_style,
                'name': 'Test Site',
                'description': f'Professional {brand_identity_obj.industry} services'
            },
            'colors': {
                'primary': brand_identity_obj.colors.primary,
                'secondary': brand_identity_obj.colors.secondary,
                'accent': brand_identity_obj.colors.accent,
                'background': brand_identity_obj.colors.background,
                'text_primary': brand_identity_obj.colors.text_primary,
                'text_secondary': brand_identity_obj.colors.text_secondary,
                'success': brand_identity_obj.colors.success,
                'error': brand_identity_obj.colors.error
            },
            'typography': {
                'primary_font': brand_identity_obj.typography.primary_font,
                'secondary_font': brand_identity_obj.typography.secondary_font,
                'heading_font': brand_identity_obj.typography.heading_font,
                'font_sizes': brand_identity_obj.typography.font_sizes,
                'font_weights': brand_identity_obj.typography.font_weights,
                'line_heights': brand_identity_obj.typography.line_heights
            },
            'style': {
                'border_radius': brand_identity_obj.style.border_radius,
                'shadow_style': brand_identity_obj.style.shadow_style,
                'spacing_scale': brand_identity_obj.style.spacing_scale,
                'button_styles': brand_identity_obj.style.button_styles,
                'card_styles': brand_identity_obj.style.card_styles,
                'layout_patterns': brand_identity_obj.style.layout_patterns
            }
        }
        
        # Typography system
        print("5️⃣ Creating typography system...")
        typography = create_typography_system(brand_identity)
        print(f"   ✅ Typography system created")
        
        # Proportional sizing
        print("6️⃣ Applying proportional sizing...")
        sections_with_sizing = apply_proportional_sizing_to_sections([a.__dict__ for a in analyses])
        print(f"   ✅ Sizing applied to {len(sections_with_sizing)} sections")
        
    except Exception as e:
        print(f"   ❌ Brand processing failed: {e}")
        all_issues.append(f"Brand processing failed: {e}")
        # Use fallback values
        sections_with_sizing = [a.__dict__ for a in analyses]
        brand_identity = {'colors': {'primary': '#3B82F6'}, 'typography': {}, 'brand': {}, 'style': {}}
        typography = None
    
    # Phase 3: Issue Analysis
    print_section_divider("PHASE 3: DETAILED ISSUE ANALYSIS")
    
    # Analyze template context issues
    context_issues = analyze_template_context_issues(sections_with_sizing, brand_identity)
    all_issues.extend(context_issues)
    
    # Analyze image and sizing issues
    sizing_issues = analyze_image_sizing_issues(sections_with_sizing, brand_identity)
    all_issues.extend(sizing_issues)
    
    # Analyze CSS generation issues
    if typography:
        css_issues = analyze_css_generation_issues(brand_identity, typography)
        all_issues.extend(css_issues)
    
    # Test template rendering
    rendering_issues = test_template_rendering(sections_with_sizing, brand_identity)
    all_issues.extend(rendering_issues)
    
    # Phase 4: Results Summary
    print_section_divider("PHASE 4: RESULTS SUMMARY")
    
    if all_issues:
        print("❌ ISSUES FOUND:")
        for i, issue in enumerate(all_issues, 1):
            print(f"   {i}. {issue}")
    else:
        print("✅ No major issues detected")
    
    print(f"\n📊 Total Issues Found: {len(all_issues)}")
    print(f"🔍 Generated HTML saved for manual inspection")
    
    return all_issues


if __name__ == "__main__":
    issues = debug_pipeline_comprehensive()
    print(f"\nDebugging complete. Found {len(issues)} issues.")