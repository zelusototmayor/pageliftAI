import pytest
from unittest.mock import patch, MagicMock
from app.services.tasks import pipeline_task
from app.models import Job, Project
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile
import os

# Test database setup
test_engine = create_engine("sqlite:///:memory:")
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture
def setup_test_db():
    from app.models import Base
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def test_session():
    with TestSessionLocal() as session:
        yield session

def test_pipeline_task_success(setup_test_db, test_session):
    # Create test project and job
    project = Project(name="TestProject", url="http://example.com")
    test_session.add(project)
    test_session.flush()
    
    job = Job(project_id=project.id, status="queued")
    test_session.add(job)
    test_session.commit()
    
    # Mock external dependencies
    mock_scrape_result = MagicMock()
    mock_scrape_result.pages = [MagicMock(html="<html><body><section>Test</section></body></html>")]
    
    mock_sections = [MagicMock(__dict__={"section_id": 1, "heading": "Test", "text": "Test content"})]
    
    mock_analyses = [MagicMock(__dict__={"section_id": 1, "category": "hero", "short_copy": "Test"})]
    
    # Create a temporary file for the zip
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_file:
        tmp_file.write(b"fake zip content")
        tmp_zip_path = tmp_file.name
    
    try:
        with patch("app.services.tasks.scrape_site", return_value=mock_scrape_result), \
             patch("app.services.tasks.parse_html_sections", return_value=mock_sections), \
             patch("app.services.tasks.analyze_sections", return_value=mock_analyses), \
             patch("app.services.tasks.render_site", return_value=tmp_zip_path), \
             patch("app.services.tasks.boto3.client") as mock_boto3, \
             patch("app.services.tasks.SessionLocal", TestSessionLocal):
            
            # Run the pipeline task
            result = pipeline_task(job.id, "http://example.com")
            
            # Verify the job was updated correctly
            test_session.refresh(job)
            assert job.status == "complete"
            assert job.output_zip_url == f"S3_GENERATED/site_{job.id}.zip"
            assert job.error is None
            
            # Verify MinIO upload was called
            mock_boto3.assert_called_once()
            
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_zip_path):
            os.unlink(tmp_zip_path)

def test_pipeline_task_failure(setup_test_db, test_session):
    # Create test project and job
    project = Project(name="TestProject", url="http://example.com")
    test_session.add(project)
    test_session.flush()
    
    job = Job(project_id=project.id, status="queued")
    test_session.add(job)
    test_session.commit()
    
    with patch("app.services.tasks.scrape_site", side_effect=Exception("Scraping failed")), \
         patch("app.services.tasks.SessionLocal", TestSessionLocal):
        
        # Run the pipeline task (should fail)
        with pytest.raises(Exception):
            pipeline_task(job.id, "http://example.com")
        
        # Verify the job was marked as failed
        test_session.refresh(job)
        assert job.status == "failed"
        assert "Scraping failed" in job.error 