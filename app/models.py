import enum
from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Text
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class JobStatus(enum.Enum):
    queued = "queued"
    scraping = "scraping"
    analyzing = "analyzing"
    rendering = "rendering"
    complete = "complete"
    failed = "failed"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=True)
    # Add more fields as needed

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", backref="projects")
    jobs = relationship("Job", back_populates="project")

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    status = Column(Enum(JobStatus), nullable=False, default=JobStatus.queued)
    error = Column(Text, nullable=True)
    output_zip_url = Column(String, nullable=True)
    analysis_input = Column(Text, nullable=True)  # JSON of parsed sections
    analysis_output = Column(Text, nullable=True)  # JSON of AI-categorized sections
    project = relationship("Project", back_populates="jobs") 