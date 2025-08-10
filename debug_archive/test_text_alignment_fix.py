#!/usr/bin/env python3
"""
Test Text Alignment Fixes
Regenerates a test website and validates text alignment improvements.
"""

import os
import sys
import json
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_text_alignment_fixes():
    """Test the text alignment fixes by generating a new website."""
    
    print("🧪 Testing Text Alignment Fixes...")
    print("=" * 50)
    
    try:
        # Import after path setup
        from app.services.render import render_site_with_brand
        from app.services.brand_identity import BrandIdentity
        from app.services.typography import TypographySystem
        from app.data_models import WebsiteData, SectionData
        
        print("✅ Successfully imported required modules")
        
        # Create test data
        test_sections = [
            SectionData(
                section_type="hero",
                heading="Professional Drain Cleaning Services",
                original_text="Expert drain cleaning services available 24/7 for emergency repairs and maintenance.",
                template="hero_modern",
                order=1
            ),
            SectionData(
                section_type="about", 
                heading="About Our Company",
                original_text="We are professional plumbing experts with years of experience serving residential and commercial clients.",
                template="about_responsive",
                order=2
            ),
            SectionData(
                section_type="services",
                heading="Our Services", 
                original_text="Comprehensive plumbing solutions including drain cleaning, pipe repair, and emergency services.",
                template="services_modern",
                order=3
            ),
            SectionData(
                section_type="contact",
                heading="Contact Us",
                original_text="Get in touch for professional plumbing services.",
                template="contact_modern", 
                order=4
            )
        ]
        
        test_website = WebsiteData(
            url="https://test-site.com",
            title="Professional Plumbing Services",
            sections=test_sections,
            phone_number="(555) 123-4567",
            email="info@test-plumbing.com"
        )
        
        # Create brand identity
        brand_identity = BrandIdentity(
            brand={
                'name': 'Test Plumbing Co',
                'industry': 'plumbing',
                'tone': 'professional',
                'description': 'Professional plumbing services'
            },
            colors={
                'primary': '#1E40AF',
                'secondary': '#64748B', 
                'accent': '#F59E0B',
                'text_primary': '#111827',
                'background': '#FFFFFF'
            }
        )
        
        # Create typography system
        typography = TypographySystem(
            heading_font='Inter, system-ui, sans-serif',
            primary_font='Inter, system-ui, sans-serif',
            heading_sizes={
                'h1': 'text-4xl sm:text-5xl lg:text-6xl',
                'h2': 'text-3xl sm:text-4xl lg:text-5xl', 
                'h3': 'text-2xl sm:text-3xl lg:text-4xl'
            }
        )
        
        print("✅ Created test data structures")
        
        # Generate the website HTML
        result = render_site_with_brand(test_website, brand_identity, typography)
        
        if result['status'] != 'success':
            print(f"❌ Website generation failed: {result.get('message', 'Unknown error')}")
            return False
            
        html_content = result['html']
        print(f"✅ Generated website HTML ({len(html_content):,} characters)")
        
        # Save the generated HTML for analysis
        output_file = project_root / "debug_output" / "test_text_alignment_fixed.html"
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Saved test HTML to: {output_file}")
        
        # Analyze the fixed HTML for text alignment improvements
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Count headers with text alignment classes
        headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        aligned_headers = 0
        center_aligned_headers = 0
        responsive_aligned_headers = 0
        
        for header in headers:
            classes = header.get('class', [])
            class_str = ' '.join(classes)
            
            if any(cls in classes for cls in ['text-left', 'text-center', 'text-right', 'text-justify']):
                aligned_headers += 1
                if 'text-center' in classes:
                    center_aligned_headers += 1
                    
            # Check for responsive alignment
            if any('text-center' in cls or 'text-left' in cls for cls in class_str.split() if 'lg:' in cls or 'sm:' in cls or 'md:' in cls):
                responsive_aligned_headers += 1
        
        # Count paragraphs with overflow protection
        paragraphs = soup.find_all(['p'])
        protected_paragraphs = 0
        
        for p in paragraphs:
            classes = p.get('class', [])
            class_str = ' '.join(classes)
            if any(cls in class_str for cls in ['break-words', 'overflow-hidden', 'text-ellipsis']):
                protected_paragraphs += 1
        
        # Print analysis results
        print("\n📊 TEXT ALIGNMENT FIX RESULTS")
        print("-" * 40)
        print(f"Total headers found: {len(headers)}")
        print(f"Headers with alignment classes: {aligned_headers}")
        print(f"Headers with center alignment: {center_aligned_headers}")
        print(f"Headers with responsive alignment: {responsive_aligned_headers}")
        print(f"Total paragraphs: {len(paragraphs)}")
        print(f"Paragraphs with overflow protection: {protected_paragraphs}")
        
        # Check if improvements were made
        improvement_score = 0
        if aligned_headers >= len(headers) * 0.8:  # At least 80% of headers have alignment
            improvement_score += 1
            print("✅ Good header alignment coverage")
        else:
            print(f"⚠️  Only {aligned_headers}/{len(headers)} headers have alignment classes")
            
        if center_aligned_headers >= aligned_headers * 0.5:  # At least 50% are center-aligned
            improvement_score += 1 
            print("✅ Good use of center alignment for visual hierarchy")
        else:
            print("⚠️  Could use more center alignment for better visual hierarchy")
            
        if protected_paragraphs >= len(paragraphs) * 0.3:  # At least 30% have overflow protection
            improvement_score += 1
            print("✅ Good text overflow protection")
        else:
            print("⚠️  More text overflow protection recommended")
            
        print(f"\n📈 Overall improvement score: {improvement_score}/3")
        
        if improvement_score >= 2:
            print("🎉 Text alignment fixes are working well!")
            return True
        else:
            print("⚠️  Text alignment fixes need more work")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_text_alignment_fixes()
    exit(0 if success else 1)