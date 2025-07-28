import os
from celery import Celery
from app.services.scrape import scrape_site
from app.services.parse import parse_html_sections
from app.services.analyze import analyze_sections, persist_analysis_output
from app.services.render import render_site, upload_and_set_output
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
            
            # Synchronous render
            zip_path = render_site([a.__dict__ for a in analyses], title=job.project.name)
            
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