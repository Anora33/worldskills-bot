# -*- coding: utf-8 -*-
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging
import sqlite3
import os

logger = logging.getLogger(__name__)
router = Router()

# Database path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "worldskills.db")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

# Database helpers
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_user(tid):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE telegram_id=?", (str(tid),))
        r = c.fetchone()
        conn.close()
        return dict(r) if r else None
    except: return None

# Admin ID tekshiruvi
def is_admin(user_id):
    admin_id = int(os.getenv("ADMIN_ID", 0))
    return user_id == admin_id

# ============= ADMIN START =============
@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Admin panel - bosh menyu"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Bu command faqat admin uchun!")
        return
    
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Umumiy statistika", callback_data="admin_stats")
    builder.button(text="📄 Portfoliolarni ko'rish", callback_data="admin_portfolios")
    builder.button(text="📋 Hujjatlarni ko'rish", callback_data="admin_documents")
    builder.button(text="👥 Ishtirokchilar ro'yxati", callback_data="admin_users")
    builder.adjust(1)
    
    await message.answer(
        "👨‍💼 <b>Admin Panel</b>\n\n"
        "Bo'limni tanlang:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

# ============= STATISTIKA =============
@router.callback_query(F.data == "admin_stats")
async def callback_admin_stats(callback: types.CallbackQuery):
    """Umumiy statistika"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) FROM users")
        total_users = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM portfolio")
        total_portfolio = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM portfolio WHERE status='pending'")
        pending_portfolio = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM portfolio WHERE status='approved'")
        approved_portfolio = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM documents")
        total_docs = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM documents WHERE status='pending'")
        pending_docs = c.fetchone()[0]
        
        conn.close()
        
        await callback.message.answer(
            f"📊 <b>Umumiy Statistika</b>\n\n"
            f"👥 <b>Ishtirokchilar:</b> {total_users}\n\n"
            f"💼 <b>Portfolio:</b>\n"
            f"• Jami: {total_portfolio}\n"
            f"• ⏳ Kutishda: {pending_portfolio}\n"
            f"• ✅ Tasdiqlandi: {approved_portfolio}\n\n"
            f"📄 <b>Hujjatlar:</b>\n"
            f"• Jami: {total_docs}\n"
            f"• ⏳ Kutishda: {pending_docs}",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Stats error: {e}")
    await callback.answer()

# ============= PORTFOLIO KO'RISH =============
@router.callback_query(F.data == "admin_portfolios")
async def callback_admin_portfolios(callback: types.CallbackQuery):
    """Portfoliolarni ko'rish"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("""
            SELECT p.*, u.fullname, u.phone, u.profession_uz 
            FROM portfolio p 
            LEFT JOIN users u ON p.telegram_id = u.telegram_id 
            WHERE p.status = 'pending' 
            ORDER BY p.uploaded_at DESC 
            LIMIT 10
        """)
        portfolios = c.fetchall()
        conn.close()
        
        if not portfolios:
            await callback.answer("⏳ Hozir ko'rib chiqiladigan portfolio yo'q", show_alert=True)
            return
        
        for portfolio in portfolios:
            user_name = portfolio['fullname'] or "N/A"
            profession = portfolio['profession_uz'] or "N/A"
            filename = portfolio['filename']
            p_id = portfolio['id']
            tid = portfolio['telegram_id']
            
            # Fayl yo'li
            file_path = os.path.join(UPLOAD_DIR, "portfolio", tid, portfolio['profession_id'], filename)
            
            # Tugmalar
            builder = InlineKeyboardBuilder()
            builder.button(text="✅ Qabul qilish", callback_data=f"approve_{p_id}")
            builder.button(text="❌ Rad etish", callback_data=f"reject_{p_id}")
            builder.adjust(2)
            
            await callback.bot.send_document(
                chat_id=callback.from_user.id,
                document=FSInputFile(file_path),
                caption=f"💼 <b>Portfolio Ish</b>\n\n"
                       f"👤 <b>Ism:</b> {user_name}\n"
                       f"🔧 <b>Kasb:</b> {profession}\n"
                       f"📎 <b>Fayl:</b> {filename}\n\n"
                       f"<i>Baholang:</i>",
                reply_markup=builder.as_markup(),
                parse_mode="HTML"
            )
        
        await callback.answer()
    except Exception as e:
        logger.error(f"Portfolio view error: {e}")
        await callback.answer("❌ Xatolik yuz berdi", show_alert=True)

# ============= APPROVE PORTFOLIO =============
@router.callback_query(F.data.startswith("approve_"))
async def callback_approve_portfolio(callback: types.CallbackQuery):
    """Portfolioni qabul qilish"""
    try:
        p_id = int(callback.data.replace("approve_", ""))
        
        # Bahoni so'rash
        await callback.message.answer(
            "⭐ <b>Baho kiriting (0-100):</b>\n\n"
            "<i>Raqam yuboring:</i>",
            parse_mode="HTML"
        )
        
        # State o'rnatish (keyingi xabar uchun)
        await callback.state.set_state("waiting_score")
        await callback.state.update_data(approve_id=p_id)
        
    except Exception as e:
        logger.error(f"Approve error: {e}")
    await callback.answer()

# ============= REJECT PORTFOLIO =============
@router.callback_query(F.data.startswith("reject_"))
async def callback_reject_portfolio(callback: types.CallbackQuery):
    """Portfolioni rad etish"""
    try:
        p_id = int(callback.data.replace("reject_", ""))
        
        await callback.message.answer(
            "💬 <b>Rad etish sababini yozing:</b>\n\n"
            "<i>Masalan: Fayl ochilmadi, sifat past...</i>",
            parse_mode="HTML"
        )
        
        await callback.state.set_state("waiting_reject_reason")
        await callback.state.update_data(reject_id=p_id)
        
    except Exception as e:
        logger.error(f"Reject error: {e}")
    await callback.answer()

# ============= SCORE HANDLER =============
@router.message(F.text)
async def handle_score(message: Message, state):
    """Baho qo'shish"""
    try:
        current_state = await state.get_state()
        
        if current_state == "waiting_score":
            data = await state.get_data()
            p_id = data.get("approve_id")
            
            try:
                score = int(message.text)
                if score < 0 or score > 100:
                    await message.answer("❌ Baho 0-100 oralig'ida bo'lishi kerak!")
                    return
                
                # Database'ga yangilash
                conn = get_db_connection()
                c = conn.cursor()
                c.execute("UPDATE portfolio SET status='approved', score=? WHERE id=?", (score, p_id))
                
                # User ID olish
                c.execute("SELECT telegram_id FROM portfolio WHERE id=?", (p_id,))
                tid = c.fetchone()[0]
                conn.commit()
                conn.close()
                
                # User'ga xabar
                await message.bot.send_message(
                    tid,
                    f"✅ <b>Tabriklaymiz!</b>\n\n"
                    f"Portfolio ishingiz qabul qilindi!\n"
                    f"⭐ <b>Baho:</b> {score}/100\n\n"
                    f"Yaxshi natija! 🎉",
                    parse_mode="HTML"
                )
                
                await message.answer(f"✅ Portfolio {score} ball bilan qabul qilindi!")
                await state.clear()
                
            except ValueError:
                await message.answer("❌ Iltimos, raqam kiriting!")
        
        elif current_state == "waiting_reject_reason":
            data = await state.get_data()
            p_id = data.get("reject_id")
            reason = message.text
            
            # Database'ga yangilash
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("UPDATE portfolio SET status='rejected', comment=? WHERE id=?", (reason, p_id))
            
            # User ID olish
            c.execute("SELECT telegram_id FROM portfolio WHERE id=?", (p_id,))
            tid = c.fetchone()[0]
            conn.commit()
            conn.close()
            
            # User'ga xabar
            await message.bot.send_message(
                tid,
                f"❌ <b>Portfolio ishingiz rad etildi</b>\n\n"
                f"💬 <b>Sabab:</b> {reason}\n\n"
                f"Iltimos, qayta yuklang!",
                parse_mode="HTML"
            )
            
            await message.answer(f"❌ Portfolio rad etildi. Sabab: {reason}")
            await state.clear()
    
    except Exception as e:
        logger.error(f"Score handler error: {e}")

# ============= Hujjatlar uchun ham xuddi shunday...
# (Xuddi shu mantik hujjatlar uchun ham qo'llaniladi)
