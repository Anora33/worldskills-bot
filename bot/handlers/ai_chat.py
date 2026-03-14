# -*- coding: utf-8 -*-
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.states.states import AIChatStates
from bot.database.database import async_session
from bot.database.queries import get_user_by_telegram_id, add_points
from bot.keyboards.inline import get_main_menu_keyboard
import os
import httpx

router = Router()

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# Til bo'yicha system promptlar
SYSTEM_PROMPTS = {
    "uz": """Siz WorldSkills musobaqasi uchun maxsus AI yordamchisiz.
TIL: O'zbek tilida javob bering.
Vazifalaringiz: musobaqa haqida ma'lumot berish, tayyorgarlik bo'yicha maslahatlar, motivatsiya.
Muhim: Do'stona va professional muloqot qiling, qisqa va aniq bo'ling.
Musobaqa: Vaqt 09:00-17:00, Joy: Toshkent, Ballar: faollik uchun 1-10 ball.""",

    "ru": """Вы специальный AI помощник для соревнований WorldSkills.
ЯЗЫК: Отвечайте на русском языке.
Ваши задачи: информация о соревновании, советы по подготовке, мотивация.
Важно: Дружелюбное и профессиональное общение, краткие и четкие ответы.
Соревнование: Время 09:00-17:00, Место: Ташкент, Баллы: 1-10 за активность.""",

    "en": """You are a special AI assistant for WorldSkills competition.
LANGUAGE: Respond in English.
Your tasks: provide competition info, preparation tips, motivation.
Important: Friendly and professional communication, short and clear answers.
Competition: Time 09:00-17:00, Location: Tashkent, Points: 1-10 for activity."""
}


async def get_groq_response(user_message: str, user_context: str = "", lang: str = "uz") -> str:
    """Groq AI dan javob olish"""
    
    if not config.OPENAI_API_KEY or config.OPENAI_API_KEY == "":
        return get_fallback_response(user_message, lang)
    
    # Tilga mos system prompt
    system_prompt = SYSTEM_PROMPTS.get(lang, SYSTEM_PROMPTS["uz"])
    
    headers = {
        "Authorization": f"Bearer {config.OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"User info: {user_context}\n\nQuestion: {user_message}"}
        ],
        "max_tokens": 500,
        "temperature": 0.7
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(GROQ_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if data.get("choices") and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
            else:
                return get_fallback_response(user_message, lang)
                
    except Exception as e:
        print(f"Groq API error: {e}")
        return get_fallback_response(user_message, lang)


def get_fallback_response(user_message: str, lang: str = "uz") -> str:
    """Agar Groq ishlamasa, oddiy javoblar"""
    
    responses = {
        "uz": {
            "salom": "Assalomu alaykum! Sizga qanday yordam bera olaman?",
            "yaxshimisiz": "Yaxshiman, rahmat! Sizchi?",
            "raqobat": "WorldSkills musobaqasi - professional mahorat tanlovi.",
            "vaqt": "Musobaqa 9:00 dan 17:00 gacha davom etadi.",
            "joy": "Musobaqa Toshkent shahrida bo'lib o'tadi.",
            "ball": "Ballaringizni ko'rish uchun /stats buyrug'ini bosing.",
            "yordam": "Men sizga musobaqa, jadval, ballar haqida yordam bera olaman.",
            "default": "Kechirasiz, bu savolga hozircha javob bera olmayman. /menu buyrug'ini bosing."
        },
        "ru": {
            "salom": "Здравствуйте! Чем я могу вам помочь?",
            "yaxshimisiz": "Хорошо, спасибо! А вы?",
            "raqobat": "WorldSkills - соревнование профессионального мастерства.",
            "vaqt": "Соревнование проходит с 9:00 до 17:00.",
            "joy": "Соревнование проходит в городе Ташкент.",
            "ball": "Нажмите /stats чтобы увидеть ваши баллы.",
            "yordam": "Я могу помочь с информацией о соревновании, расписании, баллах.",
            "default": "Извините, я пока не могу ответить на этот вопрос. Нажмите /menu."
        },
        "en": {
            "salom": "Hello! How can I help you?",
            "yaxshimisiz": "I'm good, thank you! And you?",
            "raqobat": "WorldSkills is a professional skills competition.",
            "vaqt": "The competition runs from 9:00 to 17:00.",
            "joy": "The competition takes place in Tashkent.",
            "ball": "Press /stats to see your points.",
            "yordam": "I can help with competition info, schedule, points.",
            "default": "Sorry, I can't answer this question yet. Press /menu."
        }
    }
    
    user_text = user_message.lower()
    lang_responses = responses.get(lang, responses["uz"])
    
    for key, value in lang_responses.items():
        if key != "default" and key in user_text:
            return value
    
    return lang_responses.get("default", "Sorry, I can't help with that.")


@router.callback_query(F.data == "ai_help")
async def ai_help_callback(callback: CallbackQuery, state: FSMContext):
    """AI Yordamchi ni ochish"""
    await state.set_state(AIChatStates.asking)
    
    async with async_session() as db:
        user = await get_user_by_telegram_id(db, callback.from_user.id)
    
    lang = user.language if user else "uz"
    
    # Tilga mos xabar
    help_texts = {
        "uz": "🤖 AI Yordamchi\n\nAssalomu alaykum! Men sizga yordam berishga tayyorman.\n\nMenga har qanday savolingizni bering:\n- Musobaqa qachon boshlanadi?\n- Qanday yo'nalishlar bor?\n- Tayyorgarlik bo'yicha maslahat\n\nYoki /menu buyrug'ini bosing.",
        "ru": "🤖 AI помощник\n\nЗдравствуйте! Я готов вам помочь.\n\nЗадайте мне любой вопрос:\n- Когда начинается соревнование?\n- Какие направления есть?\n- Советы по подготовке\n\nИли нажмите /menu.",
        "en": "🤖 AI Assistant\n\nHello! I'm ready to help you.\n\nAsk me any question:\n- When does the competition start?\n- What competitions are available?\n- Preparation tips\n\nOr press /menu."
    }
    
    await callback.message.answer(
        help_texts.get(lang, help_texts["uz"]),
        reply_markup=None
    )
    await callback.answer()


@router.message(AIChatStates.asking)
async def process_ai_question(message: Message, state: FSMContext):
    """AI savolga javob berish"""
    user_text = message.text.strip()
    
    async with async_session() as db:
        user = await get_user_by_telegram_id(db, message.from_user.id)
    
    # Foydalanuvchi tilini olish
    lang = user.language if user else "uz"
    
    user_context = ""
    if user:
        user_context = f"Name: {user.full_name}, Competition: {user.competition}, Language: {lang}"
    
    # "Thinking" xabari (tilga mos)
    thinking_texts = {
        "uz": "🤔 Fikrlayapman...",
        "ru": "🤔 Думаю...",
        "en": "🤔 Thinking..."
    }
    
    thinking_msg = await message.answer(thinking_texts.get(lang, "🤔 Thinking..."))
    
    # Groq dan javob olish (til bilan)
    response = await get_groq_response(user_text, user_context, lang)
    
    await thinking_msg.delete()
    await message.answer(response)
    
    # Ball qo'shish
    async with async_session() as db:
        await add_points(db, message.from_user.id, 1)
    
    await state.clear()


@router.message(F.text == "/menu")
async def cmd_menu(message: Message, state: FSMContext):
    """Asosiy menyuga qaytish"""
    await state.clear()
    async with async_session() as db:
        user = await get_user_by_telegram_id(db, message.from_user.id)
    
    lang = user.language if user else "uz"
    await message.answer(
        "📱 Asosiy menyu",
        reply_markup=get_main_menu_keyboard(lang)
    )

