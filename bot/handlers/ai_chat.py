# -*- coding: utf-8 -*-
from aiogram import Router, F
from aiogram.types import Message
from groq import Groq
import os

router = Router()

# GROQ API client
client = Groq(api_key=os.environ.get('GROQ_API_KEY'))

# AI assistant handler
@router.message(F.text == "🤖 AI assistant")
async def handle_ai_assistant(message: Message):
    await message.answer(
        "🤖 <b>AI Assistant</b>\n\n"
        "Salom! Men sizga yordam berishga tayyorman.\n\n"
        "Menga savol bering:\n"
        "- Musobaqa haqida\n"
        "- Topshiriqlar haqida\n"
        "- Texnik yordam\n"
        "- Boshqa savollar\n\n"
        "<i>Savolingizni yozing, men javob beraman!</i>"
    )

# AI chat messages
@router.message(F.regexp(r"^(?!/).+$"))  # Har qanday matnli xabar (command emas)
async def ai_chat(message: Message):
    """AI bilan suhbat"""
    try:
        # Typing holatini ko'rsatish
        await message.chat.action("typing")
        
        # GROQ API ga so'rov yuborish
        completion = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "Siz WorldSkills musobaqasi bo'yicha professional yordamchisiz. Foydalanuvchilarga musobaqa, topshiriqlar va texnik savollar bo'yicha yordam berasiz. Qisqa va aniq javob bering."
                },
                {
                    "role": "user",
                    "content": message.text
                }
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        ai_response = completion.choices[0].message.content
        
        # Javob yuborish
        await message.answer(ai_response)
        
    except Exception as e:
        await message.answer(
            f"❌ <b>Xato yuz berdi</b>\n\n"
            f"Tafsilotlar: {str(e)}\n\n"
            "<i>Keyinroq qayta urinib ko'ring</i>"
        )
