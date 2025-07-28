"""initial

Revision ID: 0001_initial
Revises: 
Create Date: 2024-06-07

"""
from alembic import op
import sqlalchemy as sa
import enum

revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None

class JobStatus(enum.Enum):
    queued = "queued"
    scraping = "scraping"
    analyzing = "analyzing"
    rendering = "rendering"
    complete = "complete"
    failed = "failed"

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(), unique=True, nullable=True),
    )
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
    )
    op.create_table(
        'jobs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('status', sa.Enum(JobStatus), nullable=False, default=JobStatus.queued),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('output_zip_url', sa.String(), nullable=True),
    )

def downgrade():
    op.drop_table('jobs')
    op.drop_table('projects')
    op.drop_table('users') 