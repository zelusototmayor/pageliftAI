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

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), '../templates')

CATEGORY_BLOCKS = {
    'hero': 'blocks/hero.html',
    'about': 'blocks/about.html',
    'services': 'blocks/services.html',
    'gallery': 'blocks/gallery.html',
    'contact': 'blocks/contact.html',
    'other': 'blocks/other.html',
}

def render_site(sections: List[Dict[str, Any]], title: str = None) -> str:
    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('index.html')
    html = template.render(sections=sections, title=title)
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