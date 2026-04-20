# -*- coding: utf-8 -*-
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.config import ADMIN_ID
from bot.database.db import get_all_users, get_user_documents, get_user_portfolio
import logging

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("admin"))
async def admin_panel(message: Message):
    """Admin panel - faqat ADMIN_ID uchun"""
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Bu command faqat admin uchun!")
        return
    
    builder = InlineKeyboardBuilder()
    builder.button(text="👥 Ishtirokchilar", callback_data="admin_users")
    builder.button(text="📄 Hujjatlar", callback_data="admin_docs")
    builder.button(text="💼 Portfolio", callback_data="admin_portfolio")
    builder.button(text="🏆 Sertifikatlar", callback_data="admin_certs")
    builder.adjust(2)
    
    await message.answer(
        "🔧 <b>Admin Panel</b>\n\n"
        "Kerakli bo'limni tanlang:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "admin_users")
async def admin_users_list(cb: types.CallbackQuery):
    """Barcha ishtirokchilar ro'yxati"""
    users = get_all_users()
    
    if not users:
        await cb.answer("Hali ishtirokchilar yo'q", show_alert=True)
        return
    
    text = "👥 <b>Ishtirokchilar Ro'yxati</b>\n\n"
    for user in users[:10]:  # Birinchi 10 ta
        text += f"• {user.get('fullname')} | {user.get('profession')}\n"
        text += f"  📱 {user.get('phone')} | ID: <code>{user.get('telegram_id')}</code>\n\n"
    
    if len(users) > 10:
        text += f"\n... va yana {len(users) - 10} ta ishtirokchi"
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Orqaga", callback_data="admin_back")
    
    await cb.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await cb.answer()

@router.callback_query(F.data == "admin_docs")
async def admin_docs_pending(cb: types.CallbackQuery):
    """Ko'rib chiqilishi kerak bo'lgan hujjatlar"""
    # Placeholder: Database'dan pending hujjatlarni olish
    pending_docs = []  # db.get_pending_documents()
    
    if not pending_docs:
        await cb.answer("Hozir ko'rib chiqiladigan hujjatlar yo'q", show_alert=True)
        return
    
    # Har bir hujjat uchun inline keyboard
    for doc in pending_docs[:5]:  # Birinchi 5 ta
        builder = InlineKeyboardBuilder()
        builder.button(text="✅ Tasdiqlash", callback_data=f"approve_doc_{doc['tid']}_{doc['doc_id']}")
        builder.button(text="❌ Rad etish", callback_data=f"reject_doc_{doc['tid']}_{doc['doc_id']}")
        builder.adjust(2)
        
        await cb.message.answer(
            f"📄 <b>{doc['doc_title']}</b>\n"
            f"👤 {doc['fullname']}\n"
            f"📎 {doc['filename']}\n\n"
            f"<i>Izoh qo'shing yoki tasdiqlang/rad eting:</i>",
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
    
    await cb.answer()

@router.callback_query(F.data.startswith("approve_doc_") | F.data.startswith("reject_doc_"))
async def admin_review_action(cb: types.CallbackQuery):
    """Admin tasdiqlash yoki rad etish"""
    action, tid, doc_id = cb.data.split("_")[0], cb.data.split("_")[2], cb.data.split("_")[3]
    
    # Database'ni yangilash (placeholder)
    # db.update_document_status(tid, doc_id, action)
    
    # Foydalanuvchiga xabar yuborish (backend orqali)
    # Bu yerda requests.post() orqali /api/admin/review/document ga yuborish mumkin
    
    status_text = "✅ tasdiqlandi" if action == "approve" else "❌ rad etildi"
    await cb.answer(f"Hujjat {status_text}!", show_alert=True)
    
    # Refresh list
    await admin_docs_pending(cb)

@router.callback_query(F.data == "admin_back")
async def admin_back(cb: types.CallbackQuery):
    """Admin panelga qaytish"""
    builder = InlineKeyboardBuilder()
    builder.button(text="👥 Ishtirokchilar", callback_data="admin_users")
    builder.button(text="📄 Hujjatlar", callback_data="admin_docs")
    builder.button(text="💼 Portfolio", callback_data="admin_portfolio")
    builder.button(text="🏆 Sertifikatlar", callback_data="admin_certs")
    builder.adjust(2)
    
    await cb.message.edit_text(
        "🔧 <b>Admin Panel</b>\n\nKerakli bo'limni tanlang:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await cb.answer()
