"""
Content validation and quality scoring utilities
"""
import json
import logging
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ContentQualityReport:
    """Report containing content quality metrics"""
    job_id: int
    url: str
    
    # Content metrics
    total_sections: int
    total_words: int
    total_images: int
    average_words_per_section: float
    
    # Business data metrics
    phones_found: int
    emails_found: int
    ctas_found: int
    forms_found: int
    business_data_score: float
    
    # Quality scores
    content_density_score: float
    business_completeness_score: float
    overall_quality_score: float
    
    # Issues and recommendations
    issues: List[str]
    recommendations: List[str]

def validate_section_content(section: Dict[str, Any]) -> Tuple[float, List[str]]:
    """Validate content quality for a single section"""
    issues = []
    score = 100.0
    
    text = section.get('text', '')
    heading = section.get('heading', '')
    images = section.get('img_urls', [])
    
    # Check for empty content
    if not text or len(text.strip()) < 10:
        issues.append("Section has minimal or no text content")
        score -= 30
    
    # Check word count
    word_count = len(text.split())
    if word_count < 5:
        issues.append(f"Very low word count: {word_count}")
        score -= 20
    elif word_count < 15:
        issues.append(f"Low word count: {word_count}")
        score -= 10
    
    # Check for heading
    if not heading or len(heading.strip()) < 3:
        issues.append("Section missing meaningful heading")
        score -= 15
    
    # Check for very long sections (might indicate poor extraction)
    if word_count > 500:
        issues.append(f"Unusually long section: {word_count} words (might need splitting)")
        score -= 10
    
    # Check for duplicate or repetitive content
    sentences = text.split('.')
    if len(sentences) > 3:
        unique_sentences = set(s.strip().lower() for s in sentences if len(s.strip()) > 10)
        if len(unique_sentences) < len(sentences) * 0.7:
            issues.append("High repetitive content detected")
            score -= 15
    
    return max(score, 0), issues

def validate_business_data(business_data: Dict[str, Any]) -> Tuple[float, List[str]]:
    """Validate business-critical data completeness"""
    issues = []
    score = 0
    max_score = 100
    
    phones = business_data.get('phones', [])
    emails = business_data.get('emails', [])
    addresses = business_data.get('addresses', [])
    business_hours = business_data.get('business_hours', [])
    ctas = business_data.get('ctas', [])
    forms = business_data.get('forms', [])
    social_media = business_data.get('social_media', {})
    
    # Phone numbers (25 points)
    if phones:
        score += 25
        if len(phones) > 1:
            score += 5  # Bonus for multiple contact methods
    else:
        issues.append("No phone numbers found")
    
    # Email addresses (20 points)
    if emails:
        score += 20
    else:
        issues.append("No email addresses found")
    
    # Physical address (15 points)
    if addresses:
        score += 15
    else:
        issues.append("No physical address found")
    
    # Business hours (10 points)
    if business_hours:
        score += 10
    else:
        issues.append("No business hours found")
    
    # Call-to-actions (15 points)
    if ctas:
        score += 15
        if len(ctas) >= 3:
            score += 5  # Bonus for multiple CTAs
    else:
        issues.append("No call-to-action buttons found")
    
    # Contact forms (10 points)
    if forms:
        score += 10
    else:
        issues.append("No contact forms found")
    
    # Social media (5 points)
    if social_media:
        score += 5
    
    return min(score, max_score), issues

def calculate_content_density_score(total_words: int, total_sections: int) -> float:
    """Calculate content density score based on word distribution"""
    if total_sections == 0:
        return 0
    
    avg_words = total_words / total_sections
    
    # Optimal range is 30-150 words per section
    if 30 <= avg_words <= 150:
        return 100
    elif avg_words < 30:
        return max(0, avg_words / 30 * 100)
    else:
        # Penalize very long sections
        return max(50, 100 - (avg_words - 150) / 10)

def generate_content_quality_report(
    job_id: int, 
    url: str, 
    extraction_data: List[Dict[str, Any]]
) -> ContentQualityReport:
    """Generate comprehensive content quality report"""
    
    logger.info(f"Generating quality report for job {job_id}")
    
    # Basic metrics
    total_sections = len(extraction_data)
    total_words = sum(len(section.get('text', '').split()) for section in extraction_data)
    total_images = sum(len(section.get('img_urls', [])) for section in extraction_data)
    avg_words = total_words / total_sections if total_sections > 0 else 0
    
    # Aggregate business data
    all_phones = set()
    all_emails = set()
    all_ctas = []
    all_forms = []
    
    for section in extraction_data:
        business_data = section.get('business_data', {})
        if business_data:
            all_phones.update(business_data.get('phones', []))
            all_emails.update(business_data.get('emails', []))
            all_ctas.extend(business_data.get('ctas', []))
            all_forms.extend(business_data.get('forms', []))
    
    # Validate business data
    combined_business_data = {
        'phones': list(all_phones),
        'emails': list(all_emails),
        'ctas': all_ctas,
        'forms': all_forms,
        'addresses': [],  # TODO: Aggregate from sections
        'business_hours': [],  # TODO: Aggregate from sections
        'social_media': {}  # TODO: Aggregate from sections
    }
    
    business_score, business_issues = validate_business_data(combined_business_data)
    
    # Validate content quality
    content_issues = []
    section_scores = []
    
    for i, section in enumerate(extraction_data):
        section_score, section_issues = validate_section_content(section)
        section_scores.append(section_score)
        
        # Add section-specific issues
        for issue in section_issues:
            content_issues.append(f"Section {i}: {issue}")
    
    # Calculate scores
    content_density_score = calculate_content_density_score(total_words, total_sections)
    avg_section_score = sum(section_scores) / len(section_scores) if section_scores else 0
    
    # Overall quality score (weighted average)
    overall_score = (
        avg_section_score * 0.4 +  # Section quality: 40%
        business_score * 0.35 +    # Business data: 35%
        content_density_score * 0.25  # Content density: 25%
    )
    
    # Generate recommendations
    recommendations = []
    
    if total_words < 100:
        recommendations.append("Increase content extraction - very low word count")
    
    if len(all_phones) == 0:
        recommendations.append("Improve phone number detection patterns")
    
    if len(all_emails) == 0:
        recommendations.append("Enhance email address extraction")
    
    if len(all_ctas) < 2:
        recommendations.append("Better CTA detection needed")
    
    if total_sections < 3:
        recommendations.append("Increase section detection sensitivity")
    
    if avg_words > 200:
        recommendations.append("Consider splitting large sections for better categorization")
    
    # Combine all issues
    all_issues = content_issues + business_issues
    
    return ContentQualityReport(
        job_id=job_id,
        url=url,
        total_sections=total_sections,
        total_words=total_words,
        total_images=total_images,
        average_words_per_section=avg_words,
        phones_found=len(all_phones),
        emails_found=len(all_emails),
        ctas_found=len(all_ctas),
        forms_found=len(all_forms),
        business_data_score=business_score,
        content_density_score=content_density_score,
        business_completeness_score=business_score,
        overall_quality_score=overall_score,
        issues=all_issues,
        recommendations=recommendations
    )

def validate_extraction_pipeline(
    original_html: str, 
    extraction_data: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Validate the entire extraction pipeline by comparing with original"""
    from bs4 import BeautifulSoup
    
    # Analyze original content
    soup = BeautifulSoup(original_html, 'html.parser')
    
    # Remove noise
    for noise in soup(['script', 'style', 'meta', 'link', 'noscript']):
        noise.decompose()
    
    original_text = soup.get_text()
    original_words = len(original_text.split())
    original_images = len(soup.find_all('img'))
    original_links = len(soup.find_all('a', href=True))
    
    # Analyze extracted content
    extracted_words = sum(len(section.get('text', '').split()) for section in extraction_data)
    extracted_images = sum(len(section.get('img_urls', [])) for section in extraction_data)
    
    # Calculate preservation rates
    word_preservation = (extracted_words / original_words * 100) if original_words > 0 else 0
    image_preservation = (extracted_images / original_images * 100) if original_images > 0 else 0
    
    # Determine quality level
    if word_preservation >= 80 and image_preservation >= 70:
        quality_level = "Excellent"
    elif word_preservation >= 60 and image_preservation >= 50:
        quality_level = "Good"
    elif word_preservation >= 40:
        quality_level = "Fair"
    else:
        quality_level = "Poor"
    
    return {
        "original_stats": {
            "words": original_words,
            "images": original_images,
            "links": original_links
        },
        "extracted_stats": {
            "words": extracted_words,
            "images": extracted_images,
            "sections": len(extraction_data)
        },
        "preservation_rates": {
            "words": round(word_preservation, 2),
            "images": round(image_preservation, 2)
        },
        "quality_level": quality_level,
        "meets_standards": word_preservation >= 60 and image_preservation >= 40
    }