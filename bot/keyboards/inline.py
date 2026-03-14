# -*- coding: utf-8 -*-
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ✅ VERCEL URL
WEBAPP_URL = "https://worldskills-webapp.vercel.app"


def get_start_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    texts = {
        "uz": {"start": "🚀 Boshlash", "about": "ℹ️ Bot haqida"},
        "ru": {"start": "🚀 Начать", "about": "ℹ️ О боте"},
        "en": {"start": "🚀 Start", "about": "ℹ️ About bot"},
    }
    
    t = texts.get(lang, texts["uz"])
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=t["start"], callback_data="start_registration"))
    builder.row(InlineKeyboardButton(text=t["about"], callback_data="about_bot"))
    return builder.as_markup()


def get_main_menu_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    texts = {
        "uz": {
            "lang": "🌍 O'zbek",
            "webapp": "📱 Mini App",
            "register": "📋 Ro'yxatdan o'tish",
            "schedule": "📅 Jadval",
            "competition": "🎯 Yo'nalishim",
            "ai": "🤖 AI Yordamchi",
            "rating": "🏆 Reyting",
            "stats": "📊 Statistikam",
        },
        "ru": {
            "lang": "🌍 Русский",
            "webapp": "📱 Mini App",
            "register": "📋 Регистрация",
            "schedule": "📅 Расписание",
            "competition": "🎯 Моя компетенция",
            "ai": "🤖 AI помощник",
            "rating": "🏆 Рейтинг",
            "stats": "📊 Моя статистика",
        },
        "en": {
            "lang": "🌍 English",
            "webapp": "📱 Mini App",
            "register": "📋 Registration",
            "schedule": "📅 Schedule",
            "competition": "🎯 My competition",
            "ai": "🤖 AI assistant",
            "rating": "🏆 Rating",
            "stats": "📊 My stats",
        },
    }
    
    t = texts.get(lang, texts["uz"])
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=t["webapp"], web_app=WebAppInfo(url=WEBAPP_URL)))
    builder.row(InlineKeyboardButton(text=t["lang"], callback_data="lang"))
    builder.row(InlineKeyboardButton(text=t["register"], callback_data="register"))
    builder.row(InlineKeyboardButton(text=t["schedule"], callback_data="schedule"))
    builder.row(
        InlineKeyboardButton(text=t["competition"], callback_data="my_competition"),
        InlineKeyboardButton(text=t["ai"], callback_data="ai_help")
    )
    builder.row(
        InlineKeyboardButton(text=t["rating"], callback_data="rating"),
        InlineKeyboardButton(text=t["stats"], callback_data="stats")
    )
    return builder.as_markup()


def get_competition_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    competitions = {
        "uz": [
            ("💻 IT dasturiy ta'minot", "comp_it_software"),
            ("🎨 Grafik dizayn", "comp_graphic_design"),
            ("🔧 Mexanika", "comp_mechanics"),
            ("👨‍ Oshpazlik", "comp_culinary"),
            ("⚡ Elektronika", "comp_electronics"),
            ("🏗️ Qurilish", "comp_construction"),
        ],
        "ru": [
            ("💻 IT программное обеспечение", "comp_it_software"),
            ("🎨 Графический дизайн", "comp_graphic_design"),
            ("🔧 Механика", "comp_mechanics"),
            ("👨‍ Кулинария", "comp_culinary"),
            ("⚡ Электроника", "comp_electronics"),
            ("🏗️ Строительство", "comp_construction"),
        ],
        "en": [
            ("💻 IT Software", "comp_it_software"),
            ("🎨 Graphic Design", "comp_graphic_design"),
            ("🔧 Mechanics", "comp_mechanics"),
            ("👨‍🍳 Culinary", "comp_culinary"),
            ("⚡ Electronics", "comp_electronics"),
            ("🏗️ Construction", "comp_construction"),
        ],
    }
    
    builder = InlineKeyboardBuilder()
    for text, callback in competitions.get(lang, competitions["uz"]):
        builder.row(InlineKeyboardButton(text=text, callback_data=callback))
    
    return builder.as_markup()


def get_language_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang_uz"))
    builder.row(InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"))
    builder.row(InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"))
    return builder.as_markup()


def get_back_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    texts = {"uz": "🔙 Ortga", "ru": "🔙 Назад", "en": "🔙 Back"}
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=texts.get(lang, "🔙 Back"), callback_data="back_to_menu"))
    return builder.as_markup()
