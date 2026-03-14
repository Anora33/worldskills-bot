# -*- coding: utf-8 -*-
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import select
from bot.database.models import User
from bot.database.database import DATABASE_URL
import logging

app = FastAPI()

# Database setup
engine = create_async_engine(DATABASE_URL, echo=True)

# Pydantic models
class UserRegister(BaseModel):
    telegram_id: int
    first_name: str
    last_name: str
    phone: str
    competition: str
    language: str = "uz"

class WorkSubmit(BaseModel):
    telegram_id: int
    title: str
    description: str
    file_url: str = None

class GradeWork(BaseModel):
    telegram_id: int
    work_id: int
    grade: int


@app.get("/")
async def root():
    return {"status": "API is running", "bot": "WorldSkills Professional"}


@app.post("/api/register")
async def register_user(user: UserRegister):
    """Yangi foydalanuvchini ro'yxatdan o'tkazish"""
    async with AsyncSession(engine) as db:
        # Borligini tekshirish
        existing = await db.execute(
            select(User).where(User.telegram_id == user.telegram_id)
        )
        if existing.scalar_one_or_none():
            return {"status": "already_registered"}
        
        # Yangi user yaratish
        new_user = User(
            telegram_id=user.telegram_id,
            full_name=f"{user.first_name} {user.last_name}",
            phone=user.phone,
            competition=user.competition,
            language=user.language,
            points=10
        )
        db.add(new_user)
        await db.commit()
        
        return {"status": "success", "user_id": new_user.id}


@app.get("/api/user/{telegram_id}")
async def get_user(telegram_id: int):
    """Foydalanuvchi ma'lumotlarini olish"""
    async with AsyncSession(engine) as db:
        user = await db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "id": user.id,
            "full_name": user.full_name,
            "competition": user.competition,
            "points": user.points,
            "language": user.language,
            "is_registered": True
        }


@app.post("/api/work")
async def submit_work(work: WorkSubmit):
    """Ish yuborish (Admin ko'radi)"""
    # Bu funksiya keyinroq to'liq amalga oshiriladi
    # Hozircha dummy response
    return {
        "status": "success",
        "message": "Ish admin tekshiruvi uchun yuborildi",
        "work_id": work.telegram_id
    }


@app.get("/api/admin/works")
async def get_all_works(admin_token: str):
    """Barcha ishlar (faqat admin)"""
    if admin_token != "admin_secret_token_123":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    # Keyinroq database'dan olish implement qilinadi
    return {
        "works": [
            {"user": "Anor Karimova", "title": "Veb-sayt", "status": "pending"},
            {"user": "Ivan Petrov", "title": "Mexanizm", "status": "graded", "grade": 4}
        ]
    }


@app.post("/api/admin/grade")
async def grade_work(grade: GradeWork, admin_token: str):
    """Ishni baholash (faqat admin)"""
    if admin_token != "admin_secret_token_123":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    # Keyinroq database'ga yozish implement qilinadi
    return {
        "status": "success",
        "message": f"Ish {grade.grade}/5 ga baholandi",
        "points_added": grade.grade * 5
    }
