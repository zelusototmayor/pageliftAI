from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.models import Project, Job, JobStatus
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
            "download_url": job.output_zip_url if job.status == JobStatus.complete else None,
            "error": job.error,
            "original_url": project.url if project else None,
        }

@router.get("/projects")
async def get_projects():
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        # Get all projects with their most recent job
        result = await db.execute(
            select(Project, Job)
            .outerjoin(Job, Project.id == Job.project_id)
            .order_by(Project.id.desc(), Job.id.desc())
        )
        
        projects_data = []
        seen_projects = set()
        
        for project, job in result:
            if project.id not in seen_projects:
                seen_projects.add(project.id)
                project_data = {
                    "id": project.id,
                    "name": project.name,
                    "url": project.url,
                }
                
                # Add job info if exists
                if job:
                    project_data.update({
                        "job_id": job.id,
                        "status": job.status,
                        "download_url": job.output_zip_url if job.status == JobStatus.complete else None,
                        "error": job.error,
                    })
                else:
                    project_data.update({
                        "job_id": None,
                        "status": "no_job",
                        "download_url": None,
                        "error": None,
                    })
                
                projects_data.append(project_data)
        
        return projects_data

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
        if job.status != JobStatus.complete or not job.output_zip_url:
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
        if job.status != JobStatus.complete or not job.output_zip_url:
            raise HTTPException(status_code=400, detail="Job not complete or no output available")
    
    extract_dir = await download_and_extract_zip(job_id)
    asset_path = os.path.join(extract_dir, file_path)
    
    if not os.path.exists(asset_path) or not os.path.commonpath([extract_dir, asset_path]) == extract_dir:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    return FileResponse(asset_path)

@router.get("/jobs/{job_id}/download")
async def download_site(job_id: int):
    async with AsyncSessionLocal() as db:
        job = await db.get(Job, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        if job.status != JobStatus.complete or not job.output_zip_url:
            raise HTTPException(status_code=400, detail="Job not complete or no output available")
    
    # Download from MinIO and serve as file
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
    zip_path = os.path.join(temp_dir, f"site_{job_id}.zip")
    
    try:
        s3.download_file(minio_bucket, key, zip_path)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Site file not found")
    
    return FileResponse(
        path=zip_path,
        filename=f"pagelift_site_{job_id}.zip",
        media_type="application/zip"
    )

@router.get("/debug/job/{job_id}/extraction")
async def debug_job_extraction(job_id: int):
    """Debug endpoint to show detailed extraction results for a job"""
    async with AsyncSessionLocal() as db:
        job = await db.get(Job, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if not job.analysis_input:
            return {"error": "No extraction data available for this job"}
        
        try:
            import json
            extraction_data = json.loads(job.analysis_input)
            
            # Calculate extraction metrics
            total_sections = len(extraction_data)
            total_words = sum(len(section.get('text', '').split()) for section in extraction_data)
            total_images = sum(len(section.get('img_urls', [])) for section in extraction_data)
            
            # Business data analysis
            total_phones = set()
            total_emails = set()
            total_ctas = 0
            total_forms = 0
            
            for section in extraction_data:
                business_data = section.get('business_data', {})
                if business_data:
                    total_phones.update(business_data.get('phones', []))
                    total_emails.update(business_data.get('emails', []))
                    total_ctas += len(business_data.get('ctas', []))
                    total_forms += len(business_data.get('forms', []))
            
            # Strategy breakdown
            strategy_counts = {}
            for section in extraction_data:
                strategy = section.get('strategy', 'unknown')
                strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
            
            return {
                "job_id": job_id,
                "extraction_summary": {
                    "total_sections": total_sections,
                    "total_words": total_words,
                    "total_images": total_images,
                    "average_words_per_section": total_words / total_sections if total_sections > 0 else 0
                },
                "business_data_summary": {
                    "unique_phones": len(total_phones),
                    "unique_emails": len(total_emails),
                    "total_ctas": total_ctas,
                    "total_forms": total_forms,
                    "phones": list(total_phones),
                    "emails": list(total_emails)
                },
                "strategy_breakdown": strategy_counts,
                "sections": extraction_data
            }
            
        except json.JSONDecodeError:
            return {"error": "Invalid extraction data format"}

@router.get("/debug/job/{job_id}/comparison")
async def debug_job_comparison(job_id: int):
    """Compare original URL content with extracted content"""
    async with AsyncSessionLocal() as db:
        job = await db.get(Job, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        project = await db.get(Project, job.project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get extraction data
        if not job.analysis_input:
            return {"error": "No extraction data available"}
        
        try:
            import json
            import requests
            from bs4 import BeautifulSoup
            
            extraction_data = json.loads(job.analysis_input)
            
            # Fetch original page
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            
            try:
                response = requests.get(project.url, headers=headers, timeout=30)
                response.raise_for_status()
                original_html = response.text
            except Exception as e:
                return {"error": f"Could not fetch original page: {str(e)}"}
            
            # Analyze original content
            soup = BeautifulSoup(original_html, 'html.parser')
            original_text = soup.get_text()
            original_words = len(original_text.split())
            original_images = len(soup.find_all('img'))
            
            # Calculate extraction metrics
            extracted_words = sum(len(section.get('text', '').split()) for section in extraction_data)
            extracted_images = sum(len(section.get('img_urls', [])) for section in extraction_data)
            
            # Content preservation rates
            word_preservation_rate = (extracted_words / original_words * 100) if original_words > 0 else 0
            image_preservation_rate = (extracted_images / original_images * 100) if original_images > 0 else 0
            
            return {
                "job_id": job_id,
                "original_url": project.url,
                "original_content": {
                    "total_words": original_words,
                    "total_images": original_images,
                },
                "extracted_content": {
                    "total_words": extracted_words,
                    "total_images": extracted_images,
                    "total_sections": len(extraction_data)
                },
                "preservation_rates": {
                    "words": round(word_preservation_rate, 2),
                    "images": round(image_preservation_rate, 2)
                },
                "quality_score": round((word_preservation_rate + image_preservation_rate) / 2, 2)
            }
            
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}

@router.get("/debug/extraction-quality")
async def debug_extraction_quality():
    """Get overall extraction quality metrics across all jobs"""
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select, func
        
        # Get all completed jobs with extraction data
        result = await db.execute(
            select(Job, Project)
            .join(Project, Job.project_id == Project.id)
            .where(Job.status == JobStatus.complete)
            .where(Job.analysis_input.isnot(None))
            .order_by(Job.id.desc())
            .limit(20)  # Last 20 jobs
        )
        
        jobs_data = []
        total_word_preservation = 0
        total_image_preservation = 0
        valid_jobs = 0
        
        for job, project in result:
            try:
                import json
                extraction_data = json.loads(job.analysis_input)
                
                # Calculate basic metrics
                extracted_words = sum(len(section.get('text', '').split()) for section in extraction_data)
                extracted_images = sum(len(section.get('img_urls', [])) for section in extraction_data)
                
                # Business data metrics
                business_phones = set()
                business_emails = set()
                business_ctas = 0
                
                for section in extraction_data:
                    business_data = section.get('business_data', {})
                    if business_data:
                        business_phones.update(business_data.get('phones', []))
                        business_emails.update(business_data.get('emails', []))
                        business_ctas += len(business_data.get('ctas', []))
                
                job_info = {
                    "job_id": job.id,
                    "project_name": project.name,
                    "url": project.url,
                    "sections": len(extraction_data),
                    "words": extracted_words,
                    "images": extracted_images,
                    "phones": len(business_phones),
                    "emails": len(business_emails),
                    "ctas": business_ctas,
                    "has_business_data": len(business_phones) > 0 or len(business_emails) > 0 or business_ctas > 0
                }
                
                jobs_data.append(job_info)
                valid_jobs += 1
                
            except Exception as e:
                continue
        
        # Calculate averages
        if valid_jobs > 0:
            avg_sections = sum(job['sections'] for job in jobs_data) / valid_jobs
            avg_words = sum(job['words'] for job in jobs_data) / valid_jobs
            avg_images = sum(job['images'] for job in jobs_data) / valid_jobs
            business_data_rate = sum(1 for job in jobs_data if job['has_business_data']) / valid_jobs * 100
        else:
            avg_sections = avg_words = avg_images = business_data_rate = 0
        
        return {
            "total_jobs_analyzed": valid_jobs,
            "averages": {
                "sections_per_job": round(avg_sections, 1),
                "words_per_job": round(avg_words, 1),
                "images_per_job": round(avg_images, 1)
            },
            "business_data_success_rate": round(business_data_rate, 1),
            "recent_jobs": jobs_data
        }

@router.get("/debug/job/{job_id}/quality-report")
async def debug_job_quality_report(job_id: int):
    """Generate detailed quality report for a specific job"""
    async with AsyncSessionLocal() as db:
        job = await db.get(Job, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        project = await db.get(Project, job.project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        if not job.analysis_input:
            return {"error": "No extraction data available for quality analysis"}
        
        try:
            import json
            from app.services.validation import generate_content_quality_report
            
            extraction_data = json.loads(job.analysis_input)
            
            # Generate quality report
            report = generate_content_quality_report(
                job_id=job_id,
                url=project.url,
                extraction_data=extraction_data
            )
            
            # Convert dataclass to dict for JSON response
            return {
                "job_id": report.job_id,
                "url": report.url,
                "metrics": {
                    "total_sections": report.total_sections,
                    "total_words": report.total_words,
                    "total_images": report.total_images,
                    "average_words_per_section": round(report.average_words_per_section, 1)
                },
                "business_data": {
                    "phones_found": report.phones_found,
                    "emails_found": report.emails_found,
                    "ctas_found": report.ctas_found,
                    "forms_found": report.forms_found,
                    "business_data_score": round(report.business_data_score, 1)
                },
                "quality_scores": {
                    "content_density_score": round(report.content_density_score, 1),
                    "business_completeness_score": round(report.business_completeness_score, 1),
                    "overall_quality_score": round(report.overall_quality_score, 1)
                },
                "issues": report.issues,
                "recommendations": report.recommendations,
                "quality_grade": (
                    "A" if report.overall_quality_score >= 90 else
                    "B" if report.overall_quality_score >= 80 else
                    "C" if report.overall_quality_score >= 70 else
                    "D" if report.overall_quality_score >= 60 else "F"
                )
            }
            
        except Exception as e:
            return {"error": f"Quality analysis failed: {str(e)}"}

@router.post("/debug/validate-url")
async def debug_validate_url(data: dict):
    """Validate extraction quality for any URL (development only)"""
    if not data.get('url'):
        raise HTTPException(status_code=400, detail="URL is required")
    
    url = data['url']
    
    try:
        import requests
        from app.services.scrape import extract_sections
        from app.services.validation import validate_extraction_pipeline, generate_content_quality_report
        
        # Fetch the page
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        original_html = response.text
        
        # Extract sections using our enhanced logic
        sections = extract_sections(original_html, url)
        
        # Convert Section objects to dictionaries
        sections_data = []
        for section in sections:
            section_dict = {
                'section_id': section.section_id,
                'text': section.text,
                'heading': section.heading,
                'img_urls': section.img_urls,
                'strategy': section.strategy,
                'priority': section.priority,
                'business_data': section.business_data,
                'ctas': section.ctas,
                'forms': section.forms,
                'tag': section.tag,
                'classes': section.classes,
                'id': section.id
            }
            sections_data.append(section_dict)
        
        # Validate extraction pipeline
        pipeline_validation = validate_extraction_pipeline(original_html, sections_data)
        
        # Generate quality report
        quality_report = generate_content_quality_report(
            job_id=0,  # No real job ID for this test
            url=url,
            extraction_data=sections_data
        )
        
        return {
            "url": url,
            "extraction_results": {
                "sections_found": len(sections_data),
                "total_words": sum(len(s.get('text', '').split()) for s in sections_data),
                "total_images": sum(len(s.get('img_urls', [])) for s in sections_data),
                "business_phones": len(set().union(*(s.get('business_data', {}).get('phones', []) for s in sections_data))),
                "business_emails": len(set().union(*(s.get('business_data', {}).get('emails', []) for s in sections_data))),
                "total_ctas": sum(len(s.get('business_data', {}).get('ctas', [])) for s in sections_data)
            },
            "pipeline_validation": pipeline_validation,
            "quality_score": round(quality_report.overall_quality_score, 1),
            "quality_grade": (
                "A" if quality_report.overall_quality_score >= 90 else
                "B" if quality_report.overall_quality_score >= 80 else
                "C" if quality_report.overall_quality_score >= 70 else
                "D" if quality_report.overall_quality_score >= 60 else "F"
            ),
            "recommendations": quality_report.recommendations,
            "issues": quality_report.issues[:5]  # Limit to top 5 issues
        }
        
    except Exception as e:
        return {"error": f"Validation failed: {str(e)}"}
