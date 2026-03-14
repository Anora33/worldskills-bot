# -*- coding: utf-8 -*-
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import os
import httpx

router = Router()

GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
GROQ_MODEL = "llama3-70b-8192"

# System prompts for different languages
SYSTEM_PROMPTS = {
    "uz": "Siz WorldSkills professional yordamchisisiz. Foydalanuvchilarga musobaqa, topshiriqlar va texnik savollar bo'yicha yordam berasiz. Javoblaringiz qisqa (max 300 belgi), aniq va foydali bo'lsin. Faqat o'zbek tilida javob bering.",
    "ru": "Вы профессиональный помощник WorldSkills. Помогаете пользователям по вопросам соревнований, заданий и технической поддержки. Ответы должны быть краткими (макс. 300 символов), точными и полезными. Отвечайте только на русском языке.",
    "en": "You are a professional WorldSkills assistant. Help users with competition, tasks, and technical questions. Keep answers short (max 300 chars), precise and helpful. Respond only in English."
}

@router.message(F.state == "ai_mode")
async def ai_chat_active(message: Message, state: FSMContext):
    """AI bilan suhbat - faqat AI mode'da ishlaydi"""
    if not GROQ_API_KEY:
        await message.answer("❌ GROQ_API_KEY sozlanmagan!")
        await state.clear()
        return
    
    user_data = await state.get_data()
    lang = user_data.get("language", "uz")
    
    try:
        await message.chat.action("typing")
        
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": GROQ_MODEL,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPTS.get(lang, SYSTEM_PROMPTS["uz"])},
                        {"role": "user", "content": message.text}
                    ],
                    "max_tokens": 300,
                    "temperature": 0.7
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data["choices"][0]["message"]["content"]
                await message.answer(ai_response)
            else:
                await message.answer("❌ " + {"uz": "AI vaqtincha ishlamayapti", "ru": "AI временно не работает", "en": "AI is temporarily unavailable"}.get(lang, "AI error"))
                
    except Exception as e:
        await message.answer("❌ " + {"uz": "Xato yuz berdi", "ru": "Произошла ошибка", "en": "An error occurred"}.get(lang, "Error"))
