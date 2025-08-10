import pytest
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import inspect
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/pagelift")

@pytest.mark.asyncio
async def test_tables_exist():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        def get_tables(sync_conn):
            inspector = inspect(sync_conn)
            return inspector.get_table_names()
        tables = await conn.run_sync(get_tables)
        assert "users" in tables
        assert "projects" in tables
        assert "jobs" in tables 