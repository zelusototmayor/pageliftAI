from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.models import Project, Job
from app.config import settings
from app.services.tasks import celery_app, pipeline_task
import os
import asyncio
import tempfile
import zipfile
import boto3

router = APIRouter()

DATABASE_URL = settings.DATABASE_URL
engine = create_async_engine(DATABASE_URL, future=True)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class ProjectCreate(BaseModel):
    url: str
    project_name: str

@router.post("/projects")
async def create_project(data: ProjectCreate):
    async with AsyncSessionLocal() as db:
        # Create Project
        project = Project(name=data.project_name, url=data.url)
        db.add(project)
        await db.flush()
        # Create Job
        job = Job(project_id=project.id, status="queued")
        db.add(job)
        await db.commit()
        # Enqueue Celery pipeline
        celery_app.send_task("app.services.tasks.pipeline_task", args=[job.id, data.url])
        return {"project_id": project.id, "job_id": job.id}

@router.get("/jobs/{job_id}")
async def get_job(job_id: int):
    async with AsyncSessionLocal() as db:
        job = await db.get(Job, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Get project to include original URL
        project = await db.get(Project, job.project_id)
        
        return {
            "job_id": job.id,
            "status": job.status,
            "download_url": job.output_zip_url if job.status == "complete" else None,
            "error": job.error,
            "original_url": project.url if project else None,
        }

@router.post("/test/set_job_status")
async def set_job_status(job_id: int, status: str, output_zip_url: str = None, error: str = None, env: str = Depends(lambda: settings.ENV)):
    if env != "development":
        raise HTTPException(status_code=403, detail="Not allowed in production")
    async with AsyncSessionLocal() as db:
        job = await db.get(Job, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        job.status = status
        job.output_zip_url = output_zip_url
        job.error = error
        await db.commit()
    return {"ok": True}

async def download_and_extract_zip(job_id: int) -> str:
    """Download ZIP from MinIO and extract to temp directory"""
    minio_endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    minio_access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    minio_secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    minio_bucket = os.getenv("MINIO_BUCKET", "pagelift-assets")
    
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
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "site.zip")
    
    try:
        s3.download_file(minio_bucket, key, zip_path)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Site file not found")
    
    extract_dir = os.path.join(temp_dir, "extracted")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    
    return extract_dir

@router.get("/jobs/{job_id}/preview", response_class=HTMLResponse)
async def preview_site(job_id: int):
    async with AsyncSessionLocal() as db:
        job = await db.get(Job, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        if job.status != "complete" or not job.output_zip_url:
            raise HTTPException(status_code=400, detail="Job not complete or no output available")
    
    extract_dir = await download_and_extract_zip(job_id)
    index_path = os.path.join(extract_dir, "index.html")
    
    if not os.path.exists(index_path):
        raise HTTPException(status_code=404, detail="Site index.html not found")
    
    with open(index_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    return HTMLResponse(content=html_content)

@router.get("/jobs/{job_id}/preview/assets/{file_path:path}")
async def preview_assets(job_id: int, file_path: str):
    async with AsyncSessionLocal() as db:
        job = await db.get(Job, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        if job.status != "complete" or not job.output_zip_url:
            raise HTTPException(status_code=400, detail="Job not complete or no output available")
    
    extract_dir = await download_and_extract_zip(job_id)
    asset_path = os.path.join(extract_dir, file_path)
    
    if not os.path.exists(asset_path) or not os.path.commonpath([extract_dir, asset_path]) == extract_dir:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    return FileResponse(asset_path) 