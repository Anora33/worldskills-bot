# -*- coding: utf-8 -*-
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.config import ADMIN_ID
import logging
import os

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("admin"))
async def admin_panel(message: Message):
    """Admin panel - faqat ADMIN_ID uchun"""
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Bu command faqat admin uchun!")
        return
    
    # Upload papkalarini tekshirish
    upload_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
    
    documents_count = 0
    portfolio_count = 0
    
    if os.path.exists(upload_folder):
        # Hujjatlar soni
        docs_path = os.path.join(upload_folder, "documents")
        if os.path.exists(docs_path):
            for root, dirs, files in os.walk(docs_path):
                documents_count += len(files)
        
        # Portfolio soni
        portfolio_path = os.path.join(upload_folder, "portfolio")
        if os.path.exists(portfolio_path):
            for root, dirs, files in os.walk(portfolio_path):
                portfolio_count += len(files)
    
    builder = InlineKeyboardBuilder()
    builder.button(text="📄 Hujjatlar", callback_data="admin_view_docs")
    builder.button(text="💼 Portfolio", callback_data="admin_view_portfolio")
    builder.button(text="📊 Statistika", callback_data="admin_stats")
    builder.adjust(2)
    
    await message.answer(
        f"🔧 <b>Admin Panel</b>\n\n"
        f"📊 <b>Statistika:</b>\n"
        f"• 📄 Yuklangan hujjatlar: {documents_count} ta\n"
        f"• 💼 Yuklangan portfolio: {portfolio_count} ta\n\n"
        f"Bo'limni tanlang:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "admin_view_docs")
async def admin_view_docs(cb: types.CallbackQuery):
    """Yuklangan hujjatlar ro'yxati"""
    upload_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads", "documents")
    
    if not os.path.exists(upload_folder):
        await cb.answer("Hali hujjatlar yo'q", show_alert=True)
        return
    
    files_list = []
    for root, dirs, files in os.walk(upload_folder):
        for file in files:
            if file.endswith(".pdf"):
                files_list.append(file)
    
    if not files_list:
        await cb.answer("Hali hujjatlar yo'q", show_alert=True)
        return
    
    text = f"📄 <b>Yuklangan Hujjatlar</b>\n\n"
    for i, file in enumerate(files_list[-10:], 1):  # Oxirgi 10 ta
        text += f"{i}. {file}\n"
    
    text += f"\n<b>Jami:</b> {len(files_list)} ta hujjat"
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Orqaga", callback_data="admin_back")
    
    await cb.message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await cb.answer()

@router.callback_query(F.data == "admin_view_portfolio")
async def admin_view_portfolio(cb: types.CallbackQuery):
    """Yuklangan portfolio ro'yxati"""
    upload_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads", "portfolio")
    
    if not os.path.exists(upload_folder):
        await cb.answer("Hali portfolio yo'q", show_alert=True)
        return
    
    files_list = []
    for root, dirs, files in os.walk(upload_folder):
        for file in files:
            if file.endswith(".pdf"):
                files_list.append(file)
    
    if not files_list:
        await cb.answer("Hali portfolio yo'q", show_alert=True)
        return
    
    text = f"💼 <b>Yuklangan Portfolio Ishlar</b>\n\n"
    for i, file in enumerate(files_list[-10:], 1):
        text += f"{i}. {file}\n"
    
    text += f"\n<b>Jami:</b> {len(files_list)} ta ish"
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Orqaga", callback_data="admin_back")
    
    await cb.message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await cb.answer()

@router.callback_query(F.data == "admin_stats")
async def admin_stats(cb: types.CallbackQuery):
    """To'liq statistika"""
    upload_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
    
    docs_count = 0
    portfolio_count = 0
    total_size = 0
    
    if os.path.exists(upload_folder):
        for root, dirs, files in os.walk(upload_folder):
            for file in files:
                if file.endswith(".pdf"):
                    filepath = os.path.join(root, file)
                    total_size += os.path.getsize(filepath)
                    if "documents" in root:
                        docs_count += 1
                    elif "portfolio" in root:
                        portfolio_count += 1
    
    total_size_mb = round(total_size / (1024 * 1024), 2)
    
    text = (
        f"📊 <b>To'liq Statistika</b>\n\n"
        f"📄 Hujjatlar: {docs_count} ta\n"
        f"💼 Portfolio: {portfolio_count} ta\n"
        f"💾 Umumiy hajm: {total_size_mb} MB\n\n"
        f"✅ Barcha fayllar Render serverida saqlanmoqda"
    )
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Orqaga", callback_data="admin_back")
    
    await cb.message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await cb.answer()

@router.callback_query(F.data == "admin_back")
async def admin_back(cb: types.CallbackQuery):
    """Admin panelga qaytish"""
    # Trigger admin_panel command again
    await cb.message.delete()
    await admin_panel(cb.message)
