# -*- coding: utf-8 -*-
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import Message
import logging
import os

logger = logging.getLogger(__name__)
router = Router()

# Groq API sozlamalari
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

@router.message(Command("ai"))
async def cmd_ai(message: Message):
    """AI yordamchini ishga tushirish"""
    await message.answer(
        "🤖 <b>AI Yordamchi</b>\n\n"
        "Savolingizni yozing, men yordam beraman!\n\n"
        "<i>Masalan:</i>\n"
        "• WorldSkills qachon bo'ladi?\n"
        "• Qanday hujjatlar kerak?\n"
        "• Tayyorgarlik bo'yicha maslahat",
        parse_mode="HTML"
    )

@router.message(F.text)
async def handle_ai_message(message: Message):
    """AI ga savol yuborish"""
    # Faqat /ai dan keyin ishlaydi (oddiy xabarlarga javob bermaslik uchun)
    # Bu yerda oddiy javob qaytaramiz (Groq API ulanmagan bo'lsa)
    
    user_text = message.text.lower()
    
    # Oddiy keyword javoblari
    responses = {
        "worldskills": "🏆 WorldSkills Shanghai 2026 2026-yil sentabr oyida bo'lib o'tadi. 60+ mamlakat, 60+ kasb!",
        "hujjat": "📄 Kerakli hujjatlar:\n• Pasport nusxasi\n• Sudlanganlik haqida ma'lumot\n• Ta'lim haqida hujjat\n• 3 ta rasm\nBarchasi my.gov.uz orqali olinadi!",
        "tayyorgarlik": "💪 Tayyorgarlik bo'yicha:\n1. Kasbingiz bo'yicha amaliy mashqlar\n2. Nazariy bilimlarni mustahkamlash\n3. Vaqtni to'g'ri taqsimlash\n4. Stressga chidamlilik",
        "kontakt": "📞 Aloqa:\nTelegram: @worldskills_admin\nTelefon: +998 93 340 40 80\nEmail: dadaxon45@gmail.com"
    }
    
    # Keyword qidirish
    for key, response in responses.items():
        if key in user_text:
            await message.answer(response)
            return
    
    # Default javob
    await message.answer(
        "🤔 Men sizning savolingizni to'liq tushunmadim.\n\n"
        "Quyidagilardan birini so'rang:\n"
        "• WorldSkills qachon?\n"
        "• Qanday hujjatlar kerak?\n"
        "• Tayyorgarlik bo'yicha maslahat\n"
        "• Kontakt ma'lumotlari\n\n"
        "Yoki /admin orqali inson yordamiga murojaat qiling!"
    )
