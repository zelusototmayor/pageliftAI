"""add analysis_output to jobs

Revision ID: 0003_add_analysis_output_to_job
Revises: 0002_add_analysis_input_to_job
Create Date: 2024-06-07
"""
from alembic import op
import sqlalchemy as sa

revision = '0003_add_analysis_output_to_job'
down_revision = '0002_add_analysis_input_to_job'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('jobs', sa.Column('analysis_output', sa.Text(), nullable=True))

def downgrade():
    op.drop_column('jobs', 'analysis_output') 