import pytest
import asyncio
from httpx import AsyncClient
from app.main import app
from unittest.mock import patch, MagicMock
from app.models import Job
from app.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(settings.DATABASE_URL, future=True)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

@pytest.mark.asyncio
async def test_create_project_and_job_happy():
    async with AsyncClient(app=app, base_url="http://test") as client:
        with patch("app.api.routes.celery_app.send_task") as mock_send_task:
            mock_send_task.return_value = MagicMock()
            resp = await client.post("/projects", json={"url": "http://example.com", "project_name": "TestProj"})
            assert resp.status_code == 200
            data = resp.json()
            assert "project_id" in data and "job_id" in data
            job_id = data["job_id"]
            # Set job status via test endpoint
            resp_set = await client.post("/test/set_job_status", params={"job_id": job_id, "status": "complete", "output_zip_url": f"S3_GENERATED/site_{job_id}.zip"})
            assert resp_set.status_code == 200
            resp2 = await client.get(f"/jobs/{job_id}")
            assert resp2.status_code == 200
            job_data = resp2.json()
            assert job_data["status"] == "complete"
            assert job_data["download_url"] is not None

@pytest.mark.asyncio
async def test_job_failure():
    async with AsyncClient(app=app, base_url="http://test") as client:
        with patch("app.api.routes.celery_app.send_task") as mock_send_task:
            mock_send_task.return_value = MagicMock()
            resp = await client.post("/projects", json={"url": "http://fail.com", "project_name": "FailProj"})
            assert resp.status_code == 200
            data = resp.json()
            job_id = data["job_id"]
            # Set job status via test endpoint
            resp_set = await client.post("/test/set_job_status", params={"job_id": job_id, "status": "failed", "error": "Something went wrong"})
            assert resp_set.status_code == 200
            resp2 = await client.get(f"/jobs/{job_id}")
            assert resp2.status_code == 200
            job_data = resp2.json()
            assert job_data["status"] == "failed"
            assert job_data["download_url"] is None
            assert job_data["error"] == "Something went wrong" 