import os
from celery import Celery
from app.services.scrape import scrape_site
from app.services.parse import parse_html_sections
from app.services.analyze import analyze_sections, persist_analysis_output
from app.services.render import render_site_with_brand, upload_and_set_output
from app.services.brand_extraction import extract_brand_identity
from app.models import Project, Job
from app.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json

CELERY_BROKER_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
CELERY_BACKEND_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery(
    "pagelift",
    broker=CELERY_BROKER_URL,
    backend=CELERY_BACKEND_URL,
)

# SQLAlchemy sync session factory
engine = create_engine(settings.DATABASE_URL.replace("+asyncpg", ""))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@celery_app.task(autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def pipeline_task(job_id: int, url: str):
    with SessionLocal() as session:
        job = session.get(Job, job_id)
        try:
            job.status = "scraping"
            session.commit()
            
            # Synchronous scrape
            scrape_result = scrape_site(url)
            html = scrape_result.pages[0].html
            
            job.status = "analyzing"
            session.commit()
            
            # Synchronous parse
            sections = parse_html_sections(html)
            section_dicts = [s.__dict__ for s in sections]
            
            # Synchronous analyze
            analyses = analyze_sections(section_dicts)
            
            # Persist analysis output (needs to be made sync)
            job.analysis_output = json.dumps([a.__dict__ for a in analyses])
            session.commit()
            
            job.status = "rendering"
            session.commit()
            
            # Extract brand identity from original site
            brand_identity_obj = extract_brand_identity(url, html)
            
            # Convert BrandIdentity dataclass to the expected format
            brand_identity = {
                'brand': {
                    'industry': brand_identity_obj.industry,
                    'tone': brand_identity_obj.tone,
                    'layout_preference': brand_identity_obj.layout_preference,
                    'image_style': brand_identity_obj.image_style,
                    'name': job.project.name,
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
            
            # Synchronous render with brand
            zip_path = render_site_with_brand([a.__dict__ for a in analyses], brand_identity, title=job.project.name)
            
            # Upload to MinIO (needs to be made sync)
            minio_endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
            minio_access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
            minio_secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin")
            minio_bucket = os.getenv("MINIO_BUCKET", "pagelift-assets")
            
            import boto3
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
            
            job.output_zip_url = key
            job.status = "complete"
            session.commit()
            
        except Exception as e:
            job.status = "failed"
            job.error = str(e)
            session.commit()
            raise 