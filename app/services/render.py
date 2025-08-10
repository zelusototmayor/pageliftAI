import os
import shutil
import tempfile
import zipfile
from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import List, Dict, Any
import boto3
from app.models import Job
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from .typography import create_typography_system
from .image_processing import process_section_images
from .css_generator import generate_brand_css
from .proportional_sizing import apply_proportional_sizing_to_sections

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), '../templates')

CATEGORY_BLOCKS = {
    'hero': 'blocks/hero_modern.html',
    'about': 'blocks/about_responsive.html', 
    'services': 'blocks/services_modern.html',
    'gallery': 'blocks/gallery_responsive.html',
    'contact': 'blocks/contact_modern.html',
    'other': 'blocks/other.html',
    # Handle mixed/hybrid categories from Phase 2
    'hero_mixed': 'blocks/mixed_responsive.html',
    'about_mixed': 'blocks/mixed_responsive.html',
    'services_mixed': 'blocks/mixed_responsive.html',
    'contact_mixed': 'blocks/mixed_responsive.html',
}

def prepare_section_for_rendering(section: Dict[str, Any], brand_identity: Dict[str, Any] = None, typography = None) -> Dict[str, Any]:
    """Prepare section data for template rendering with enhanced context"""
    
    # Extract business data for template context
    business_data = section.get('business_data', {})
    phones = business_data.get('phones', [])
    emails = business_data.get('emails', [])
    
    # Extract sizing data from proportional sizing system
    sizing_data = section.get('sizing', {})
    
    # Create enhanced template context
    template_context = {
        'section_id': section.get('section_id', 0),
        'category': section.get('category', 'other'),
        'heading': section.get('heading', ''),
        'short_copy': section.get('short_copy', ''),
        'original_text': section.get('original_text', ''),
        'img_urls': section.get('img_urls', []),
        'classes': section.get('classes', []),
        'id': section.get('id', ''),
        
        # Business data for templates
        'phone_number': phones[0] if phones else '#',
        'email': emails[0] if emails else '#',
        'business_data': business_data,
        
        # Proportional sizing data for templates - CRITICAL FIX
        'sizing': sizing_data,
        
        # Enhanced analysis data
        'confidence': section.get('confidence', 0.5),
        'reasoning': section.get('reasoning', ''),
        'is_hybrid': section.get('is_hybrid', False),
        'hybrid_categories': section.get('hybrid_categories', []),
    }
    
    # Add image_set with safe defaults if not provided via brand_identity
    if brand_identity:
        try:
            from .image_processing import process_section_images
            image_set = process_section_images(section, brand_identity)
            template_context['image_set'] = {
                'primary_image': image_set.primary_image,
                'all_images': image_set.images,
                'hero_images': image_set.hero_images,
                'gallery_images': image_set.gallery_images,
                'icon_images': image_set.icon_images,
            }
        except Exception as e:
            # Fallback to safe defaults if image processing fails
            template_context['image_set'] = create_default_image_set()
    else:
        # Provide safe defaults when brand_identity not available
        template_context['image_set'] = create_default_image_set()
    
    # Add typography with safe defaults if not provided
    if typography:
        try:
            template_context['typography'] = {
                'primary_font': typography.primary_font,
                'heading_font': typography.heading_font,
                'semantic_styles': typography.get_semantic_text_styles() if hasattr(typography, 'get_semantic_text_styles') else {},
            }
        except Exception as e:
            # Fallback to safe defaults if typography fails
            template_context['typography'] = create_default_typography()
    else:
        # Provide safe defaults when typography not available
        template_context['typography'] = create_default_typography()
    
    return template_context


def create_default_image_set() -> Dict[str, Any]:
    """Create safe default image_set to prevent template errors"""
    return {
        'primary_image': None,
        'all_images': [],
        'hero_images': [],
        'gallery_images': [],
        'icon_images': [],
    }


def create_default_typography() -> Dict[str, Any]:
    """Create safe default typography to prevent template errors"""
    return {
        'primary_font': 'Inter, system-ui, sans-serif',
        'heading_font': 'Inter, system-ui, sans-serif',
        'semantic_styles': {},
    }

def render_site(sections: List[Dict[str, Any]], title: str = None) -> str:
    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(['html', 'xml'])
    )
    
    # Prepare sections for rendering with enhanced context
    enhanced_sections = []
    for section in sections:
        enhanced_section = prepare_section_for_rendering(section)
        enhanced_sections.append(enhanced_section)
    
    template = env.get_template('index.html')
    html = template.render(sections=enhanced_sections, title=title)
    # Create temp dir for site bundle
    temp_dir = tempfile.mkdtemp()
    # Write index.html
    index_path = os.path.join(temp_dir, 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)
    # Copy referenced assets (img_urls)
    asset_paths = set()
    for section in sections:
        for img in section.get('img_urls', []):
            if img and not img.startswith('http'):
                asset_paths.add(img)
    for asset in asset_paths:
        asset_src = os.path.join(TEMPLATES_DIR, asset.lstrip('/'))
        asset_dst = os.path.join(temp_dir, asset.lstrip('/'))
        os.makedirs(os.path.dirname(asset_dst), exist_ok=True)
        if os.path.exists(asset_src):
            shutil.copy(asset_src, asset_dst)
    # Zip the site
    zip_path = os.path.join(temp_dir, 'site.zip')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(temp_dir):
            for file in files:
                if file == 'site.zip':
                    continue
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, temp_dir)
                zipf.write(abs_path, rel_path)
    return zip_path


def render_site_with_brand(sections: List[Dict[str, Any]], brand_identity: Dict[str, Any], title: str = None) -> str:
    """Enhanced render function with brand identity, typography, and image processing"""
    
    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(['html', 'xml'])
    )
    
    # Create typography system from brand identity
    typography = create_typography_system(brand_identity)
    
    # Generate dynamic CSS based on brand identity
    brand_css = generate_brand_css(brand_identity, typography)
    
    # Apply proportional sizing to all sections
    sections_with_sizing = apply_proportional_sizing_to_sections(sections)
    
    # Process sections with enhanced context including images and typography
    enhanced_sections = []
    for section in sections_with_sizing:
        # Prepare section with all enhancements including image_set and typography
        enhanced_section = prepare_section_for_rendering(section, brand_identity, typography)
        enhanced_sections.append(enhanced_section)
    
    # Aggregate business data from all sections for global template context
    all_phones = []
    all_emails = []
    for section in sections:
        business_data = section.get('business_data', {})
        phones = business_data.get('phones', [])
        emails = business_data.get('emails', [])
        all_phones.extend(phones)
        all_emails.extend(emails)
    
    # Remove duplicates while preserving order
    all_phones = list(dict.fromkeys(all_phones))
    all_emails = list(dict.fromkeys(all_emails))
    
    aggregated_business_data = {
        'phones': all_phones,
        'emails': all_emails
    }
    
    # Create template context with brand identity and CSS
    template_context = {
        'sections': enhanced_sections,
        'title': title or 'Modern Professional Website',
        'brand_identity': brand_identity,
        'business_data': aggregated_business_data,  # Add aggregated business data
        'typography': {
            'css': typography.get_typography_css(),
            'responsive_css': typography.apply_responsive_scaling(),
            'font_imports': typography.get_font_imports(),
            'primary_font': typography.primary_font,
            'heading_font': typography.heading_font,
        },
        'brand_css': brand_css,  # Dynamic CSS system
    }
    
    # Render with modern enhanced template
    template = env.get_template('index_modern.html')
    html = template.render(**template_context)
    
    # Create temp dir for site bundle
    temp_dir = tempfile.mkdtemp()
    
    # Write index.html
    index_path = os.path.join(temp_dir, 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    # Copy referenced assets (keeping existing logic)
    asset_paths = set()
    for section in sections:
        for img in section.get('img_urls', []):
            if img and not img.startswith('http'):
                asset_paths.add(img)
    
    for asset in asset_paths:
        asset_src = os.path.join(TEMPLATES_DIR, asset.lstrip('/'))
        asset_dst = os.path.join(temp_dir, asset.lstrip('/'))
        os.makedirs(os.path.dirname(asset_dst), exist_ok=True)
        if os.path.exists(asset_src):
            shutil.copy(asset_src, asset_dst)
    
    # Zip the site
    zip_path = os.path.join(temp_dir, 'site.zip')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(temp_dir):
            for file in files:
                if file == 'site.zip':
                    continue
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, temp_dir)
                zipf.write(abs_path, rel_path)
    
    return zip_path


async def upload_and_set_output(job_id: int, zip_path: str, db: AsyncSession):
    minio_endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    minio_access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    minio_secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    minio_bucket = os.getenv("MINIO_BUCKET", "pagelift-assets")
    
    # Fix endpoint URL construction - don't add http:// if already present
    if not minio_endpoint.startswith(('http://', 'https://')):
        minio_endpoint = f"http://{minio_endpoint}"
    
    s3 = boto3.client(
        "s3",
        endpoint_url=minio_endpoint,
        aws_access_key_id=minio_access_key,
        aws_secret_access_key=minio_secret_key,
        region_name="us-east-1",
    )
    key = f"S3_GENERATED/site_{job_id}.zip"
    with open(zip_path, 'rb') as f:
        s3.put_object(Bucket=minio_bucket, Key=key, Body=f)
    # Set Job.output_zip_url
    job = await db.get(Job, job_id)
    job.output_zip_url = key
    await db.commit() 