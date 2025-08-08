#!/usr/bin/env python3
"""
Test script to validate enhanced scraping functionality
"""
import sys
import os
sys.path.insert(0, '/app')

from app.services.scrape import extract_sections
import requests

def test_scraping(url):
    print(f"Testing enhanced scraping on: {url}")
    
    try:
        # Fetch the webpage
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        print(f"✅ Successfully fetched HTML ({len(response.text)} characters)")
        
        # Extract sections using enhanced logic
        sections = extract_sections(response.text, url)
        
        print(f"\n📊 EXTRACTION RESULTS:")
        print(f"Total sections extracted: {len(sections)}")
        
        total_words = 0
        total_images = 0
        
        for i, section in enumerate(sections):
            word_count = len(section.text.split()) if section.text else 0
            img_count = len(section.img_urls) if section.img_urls else 0
            total_words += word_count
            total_images += img_count
            
            print(f"\nSection {i}:")
            print(f"  Strategy: {section.strategy}")
            print(f"  Tag: {section.tag}")
            print(f"  Classes: {section.classes}")
            print(f"  Heading: {section.heading[:100]}..." if section.heading else "  Heading: None")
            print(f"  Word count: {word_count}")
            print(f"  Images: {img_count}")
            
            # Business data
            if section.business_data:
                phones = section.business_data.get('phones', [])
                emails = section.business_data.get('emails', [])
                ctas = section.business_data.get('ctas', [])
                forms = section.business_data.get('forms', [])
                print(f"  Business data: {len(phones)} phones, {len(emails)} emails, {len(ctas)} CTAs, {len(forms)} forms")
                
                if phones:
                    print(f"    Phones: {phones}")
                if emails:
                    print(f"    Emails: {emails}")
            
            if section.text:
                print(f"  Text preview: {section.text[:200]}...")
        
        print(f"\n📈 SUMMARY:")
        print(f"Total words extracted: {total_words}")
        print(f"Total images found: {total_images}")
        print(f"Average words per section: {total_words / len(sections) if sections else 0:.1f}")
        
        # Business data summary
        all_phones = set()
        all_emails = set()
        all_ctas = []
        all_forms = []
        
        for section in sections:
            if section.business_data:
                all_phones.update(section.business_data.get('phones', []))
                all_emails.update(section.business_data.get('emails', []))
                all_ctas.extend(section.business_data.get('ctas', []))
                all_forms.extend(section.business_data.get('forms', []))
        
        print(f"\n📞 BUSINESS DATA SUMMARY:")
        print(f"Total unique phones: {len(all_phones)}")
        print(f"Total unique emails: {len(all_emails)}")
        print(f"Total CTAs: {len(all_ctas)}")
        print(f"Total forms: {len(all_forms)}")
        
        if all_phones:
            print(f"Phone numbers found: {list(all_phones)}")
        if all_emails:
            print(f"Email addresses found: {list(all_emails)}")
        
        # Success criteria: content AND business data
        has_content = len(sections) > 0 and total_words > 0
        has_business_data = len(all_phones) > 0 or len(all_emails) > 0 or len(all_ctas) > 0
        
        return has_content and has_business_data
        
    except Exception as e:
        print(f"❌ Error testing scraping: {e}")
        return False

if __name__ == "__main__":
    # Test on the problematic site
    success = test_scraping("https://desentopecanalizacoes.pt/")
    
    if success:
        print("\n✅ Enhanced scraping test PASSED")
    else:
        print("\n❌ Enhanced scraping test FAILED")
        sys.exit(1)