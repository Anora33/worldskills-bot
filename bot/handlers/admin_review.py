# -*- coding: utf-8 -*-
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging
import sqlite3
import os

logger = logging.getLogger(__name__)
router = Router()

# Database path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "worldskills.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@router.message(Command("review"))
async def cmd_review(message: Message):
    """Admin uchun ko'rib chiqish menyusi"""
    user_id = message.from_user.id
    admin_id = int(os.getenv("ADMIN_ID", 0))
    
    if user_id != admin_id:
        await message.answer("❌ Bu command faqat admin uchun!")
        return
    
    builder = InlineKeyboardBuilder()
    builder.button(text="📄 Hujjatlar", callback_data="admin_review_docs")
    builder.button(text="💼 Portfolio", callback_data="admin_review_portfolio")
    builder.button(text="📊 Statistika", callback_data="admin_review_stats")
    builder.adjust(2)
    
    await message.answer(
        " <b>Ko'rib Chiqish Paneli</b>\n\n"
        "Qaysi bo'limni ko'rmoqchisiz?",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "admin_review_docs")
async def callback_review_docs(callback: CallbackQuery):
    """Ko'rib chiqiladigan hujjatlar"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("""
            SELECT d.*, u.fullname, u.telegram_id 
            FROM documents d 
            LEFT JOIN users u ON d.telegram_id = u.telegram_id 
            WHERE d.status = 'pending' 
            ORDER BY d.uploaded_at DESC 
            LIMIT 10
        """)
        docs = c.fetchall()
        conn.close()
        
        if not docs:
            await callback.answer("Hozir ko'rib chiqiladigan hujjatlar yo'q", show_alert=True)
            return
        
        text = "📄 <b>Ko'rib chiqiladigan hujjatlar:</b>\n\n"
        for doc in docs:
            text += f"• {doc['fullname'] or 'N/A'}\n"
            text += f"  📋 Hujjat: {doc['doc_id']}\n"
            text += f"  📎 Fayl: {doc['filename']}\n"
            text += f"  🆔 ID: <code>{doc['telegram_id']}</code>\n\n"
        
        builder = InlineKeyboardBuilder()
        builder.button(text="🔄 Yangilash", callback_data="admin_review_docs")
        builder.button(text="🔙 Orqaga", callback_data="admin_review_back")
        builder.adjust(1)
        
        await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    except Exception as e:
        logger.error(f"Review docs error: {e}")
        await callback.answer("Xatolik yuz berdi", show_alert=True)
    await callback.answer()

@router.callback_query(F.data == "admin_review_portfolio")
async def callback_review_portfolio(callback: CallbackQuery):
    """Ko'rib chiqiladigan portfolio"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("""
            SELECT p.*, u.fullname, u.telegram_id 
            FROM portfolio p 
            LEFT JOIN users u ON p.telegram_id = u.telegram_id 
            WHERE p.score IS NULL 
            ORDER BY p.uploaded_at DESC 
            LIMIT 10
        """)
        items = c.fetchall()
        conn.close()
        
        if not items:
            await callback.answer("Hozir baholanmagan ishlar yo'q", show_alert=True)
            return
        
        text = "💼 <b>Baholanmagan portfolio ishlar:</b>\n\n"
        for item in items:
            text += f"• {item['fullname'] or 'N/A'}\n"
            text += f"  📎 Fayl: {item['filename']}\n"
            text += f"  🆔 ID: <code>{item['telegram_id']}</code>\n\n"
        
        builder = InlineKeyboardBuilder()
        builder.button(text="🔄 Yangilash", callback_data="admin_review_portfolio")
        builder.button(text="🔙 Orqaga", callback_data="admin_review_back")
        builder.adjust(1)
        
        await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    except Exception as e:
        logger.error(f"Review portfolio error: {e}")
        await callback.answer("Xatolik yuz berdi", show_alert=True)
    await callback.answer()

@router.callback_query(F.data == "admin_review_stats")
async def callback_review_stats(callback: CallbackQuery):
    """Statistika"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) FROM documents WHERE status='pending'")
        pending_docs = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM documents WHERE status='approved'")
        approved_docs = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM portfolio WHERE score IS NULL")
        pending_portfolio = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM portfolio WHERE score IS NOT NULL")
        scored_portfolio = c.fetchone()[0]
        
        conn.close()
        
        text = (
            f"📊 <b>Statistika</b>\n\n"
            f"📄 <b>Hujjatlar:</b>\n"
            f"• ⏳ Kutishda: {pending_docs}\n"
            f"• ✅ Tasdiqlandi: {approved_docs}\n\n"
            f"💼 <b>Portfolio:</b>\n"
            f"• ⏳ Baholanmagan: {pending_portfolio}\n"
            f"• ✅ Baholangan: {scored_portfolio}"
        )
        
        builder = InlineKeyboardBuilder()
        builder.button(text="🔄 Yangilash", callback_data="admin_review_stats")
        builder.button(text="🔙 Orqaga", callback_data="admin_review_back")
        builder.adjust(1)
        
        await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    except Exception as e:
        logger.error(f"Review stats error: {e}")
        await callback.answer("Xatolik yuz berdi", show_alert=True)
    await callback.answer()

@router.callback_query(F.data == "admin_review_back")
async def callback_review_back(callback: CallbackQuery):
    """Orqaga"""
    await callback.message.delete()
    await cmd_review(callback.message)
