import asyncio
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import pool
from alembic import context
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.models import Base

config = context.config
fileConfig(config.config_file_name)

def get_url():
    return os.getenv("DATABASE_URL")

target_metadata = Base.metadata

def run_migrations_online():
    connectable = create_async_engine(get_url(), poolclass=pool.NullPool)
    async def run_migrations():
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)
    def do_run_migrations(connection):
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
    asyncio.run(run_migrations())

run_migrations_online() 