# -*- coding: utf-8 -*-
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Database URL
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite+aiosqlite:///worldskills.db')

# Async engine
engine = create_async_engine(DATABASE_URL, echo=False, future=True)

# Base class for models
Base = declarative_base()

# Async session
async_session = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    future=True
)

# Database initialization
async def init_db():
    """Create all tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Test connection
async def test_connection():
    """Test database connection"""
    try:
        async with async_session() as session:
            await session.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False
