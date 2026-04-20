# -*- coding: utf-8 -*-
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.config import ADMIN_ID
import logging
import os
import sqlite3

logger = logging.getLogger(__name__)
router = Router()

# Database helper
def get_db_connection():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(BASE_DIR, "worldskills.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# ============= ADMIN PANEL COMMAND =============
@router.message(Command("admin"))
async def admin_panel(message: Message):
    """Admin panel - faqat ADMIN_ID uchun"""
    user_id = message.from_user.id
    
    if user_id != ADMIN_ID:
        await message.answer(
            f"❌ <b>Ruxsat yo'q!</b>\n\n"
            f"Sizning ID: <code>{user_id}</code>\n"
            f"Bu command faqat admin uchun!",
            parse_mode="HTML"
        )
        logger.warning(f"🚨 Unauthorized admin access from {user_id}")
        return
    
    # Statistika olish
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM documents WHERE status='pending'")
        pending_docs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM documents WHERE status='approved'")
        approved_docs = cursor.fetchone()[0]
        
        conn.close()
    except:
        total_users = 0
        pending_docs = 0
        approved_docs = 0
    
    # Inline keyboard
    builder = InlineKeyboardBuilder()
    builder.button(text="📄 Hujjatlar", callback_data="admin_docs")
    builder.button(text="💼 Portfolio", callback_data="admin_portfolio")
    builder.button(text="👥 Ishtirokchilar", callback_data="admin_users")
    builder.button(text="📊 Statistika", callback_data="admin_stats")
    builder.button(text="🔗 Web Panel", url="https://worldskills-bot.onrender.com/admin-panel")
    builder.adjust(2)
    
    await message.answer(
        f"🔧 <b>Admin Panel</b>\n\n"
        f"📊 <b>Tezkor statistika:</b>\n"
        f"• 👥 Ishtirokchilar: <b>{total_users} ta</b>\n"
        f"• 📄 Kutishda: <b>{pending_docs} ta</b>\n"
        f"• ✅ Tasdiqlandi: <b>{approved_docs} ta</b>\n\n"
        f"Bo'limni tanlang:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    logger.info(f"✅ Admin panel opened by {user_id}")

# ============= DOCUMENTS =============
@router.callback_query(F.data == "admin_docs")
async def admin_docs(callback: CallbackQuery):
    """Ko'rib chiqiladigan hujjatlar"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT d.*, u.fullname, u.telegram_id 
            FROM documents d 
            LEFT JOIN users u ON d.telegram_id = u.telegram_id 
            WHERE d.status = 'pending' 
            ORDER BY d.uploaded_at DESC 
            LIMIT 10
        """)
        docs = cursor.fetchall()
        conn.close()
        
        if not docs:
            await callback.answer("Hozir ko'rib chiqiladigan hujjatlar yo'q", show_alert=True)
            return
        
        text = "📄 <b>Ko'rib chiqiladigan hujjatlar:</b>\n\n"
        for doc in docs:
            text += f"• {doc['fullname'] or 'N/A'} - Hujjat {doc['doc_id']}\n"
            text += f"  📎 <code>{doc['filename']}</code>\n\n"
        
        builder = InlineKeyboardBuilder()
        builder.button(text="🔄 Yangilash", callback_data="admin_docs")
        builder.button(text="🔙 Orqaga", callback_data="admin_back")
        builder.adjust(1)
        
        await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    except Exception as e:
        logger.error(f"admin_docs error: {e}")
        await callback.answer("Xatolik yuz berdi", show_alert=True)
    await callback.answer()

# ============= PORTFOLIO =============
@router.callback_query(F.data == "admin_portfolio")
async def admin_portfolio(callback: CallbackQuery):
    """Portfolio ishlar"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.*, u.fullname, u.telegram_id 
            FROM portfolio p 
            LEFT JOIN users u ON p.telegram_id = u.telegram_id 
            WHERE p.score IS NULL 
            ORDER BY p.uploaded_at DESC 
            LIMIT 10
        """)
        items = cursor.fetchall()
        conn.close()
        
        if not items:
            await callback.answer("Hozir baholanmagan ishlar yo'q", show_alert=True)
            return
        
        text = "💼 <b>Baholanmagan portfolio ishlar:</b>\n\n"
        for item in items:
            text += f"• {item['fullname'] or 'N/A'}\n"
            text += f"  📎 <code>{item['filename']}</code>\n\n"
        
        builder = InlineKeyboardBuilder()
        builder.button(text="🔄 Yangilash", callback_data="admin_portfolio")
        builder.button(text="🔙 Orqaga", callback_data="admin_back")
        builder.adjust(1)
        
        await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    except Exception as e:
        logger.error(f"admin_portfolio error: {e}")
        await callback.answer("Xatolik yuz berdi", show_alert=True)
    await callback.answer()

# ============= USERS =============
@router.callback_query(F.data == "admin_users")
async def admin_users(callback: CallbackQuery):
    """Ishtirokchilar ro'yxati"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users ORDER BY registered_at DESC LIMIT 20")
        users = cursor.fetchall()
        conn.close()
        
        if not users:
            await callback.answer("Hali ishtirokchilar yo'q", show_alert=True)
            return
        
        text = "👥 <b>Ishtirokchilar ro'yxati:</b>\n\n"
        for user in users:
            text += f"• {user['fullname']}\n"
            text += f"  📱 {user['phone']}\n"
            text += f"  🎓 {user['profession'] or 'Tanlanmagan'}\n"
            text += f"  🆔 <code>{user['telegram_id']}</code>\n\n"
        
        builder = InlineKeyboardBuilder()
        builder.button(text="🔄 Yangilash", callback_data="admin_users")
        builder.button(text="🔙 Orqaga", callback_data="admin_back")
        builder.adjust(1)
        
        await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    except Exception as e:
        logger.error(f"admin_users error: {e}")
        await callback.answer("Xatolik yuz berdi", show_alert=True)
    await callback.answer()

# ============= STATS =============
@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    """To'liq statistika"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM documents")
        total_docs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM documents WHERE status='approved'")
        approved_docs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM documents WHERE status='pending'")
        pending_docs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM documents WHERE status='rejected'")
        rejected_docs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM portfolio")
        total_portfolio = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(score) FROM portfolio WHERE score IS NOT NULL")
        avg_score = cursor.fetchone()[0] or 0
        
        conn.close()
        
        text = (
            f"📊 <b>To'liq Statistika</b>\n\n"
            f"👥 <b>Ishtirokchilar:</b>\n"
            f"• Jami: {total_users} ta\n\n"
            f"📄 <b>Hujjatlar:</b>\n"
            f"• Jami: {total_docs} ta\n"
            f"• ✅ Tasdiqlandi: {approved_docs} ta\n"
            f"• ⏳ Kutishda: {pending_docs} ta\n"
            f"• ❌ Rad etildi: {rejected_docs} ta\n\n"
            f"💼 <b>Portfolio:</b>\n"
            f"• Jami ishlar: {total_portfolio} ta\n"
            f"• 🏆 O'rtacha ball: {round(avg_score, 1)}/100\n\n"
            f"🌐 <b>Web Panel:</b>\n"
            f"https://worldskills-bot.onrender.com/admin-panel"
        )
        
        builder = InlineKeyboardBuilder()
        builder.button(text="🔗 Web Panelni Ochish", url="https://worldskills-bot.onrender.com/admin-panel")
        builder.button(text="🔙 Orqaga", callback_data="admin_back")
        builder.adjust(1)
        
        await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    except Exception as e:
        logger.error(f"admin_stats error: {e}")
        await callback.answer("Xatolik yuz berdi", show_alert=True)
    await callback.answer()

# ============= BACK =============
@router.callback_query(F.data == "admin_back")
async def admin_back(callback: CallbackQuery):
    """Admin panelga qaytish"""
    await callback.message.delete()
    await admin_panel(callback.message)
