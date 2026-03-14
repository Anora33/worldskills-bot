# -*- coding: utf-8 -*-
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

# Database URL - to'g'ridan-to'g'ri os.environ dan
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite+aiosqlite:///worldskills.db')

# Async engine yaratish
engine = create_async_engine(DATABASE_URL, echo=False, future=True)

# Async session factory
async_session = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    future=True
)

# Database'ni tekshirish funksiyasi
async def test_connection():
    """Database ulanishini tekshirish"""
    try:
        async with async_session() as session:
            await session.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False
