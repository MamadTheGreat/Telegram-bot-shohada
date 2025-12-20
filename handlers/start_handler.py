from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from config import WELCOME_MESSAGE
from keyboards import get_main_menu_keyboard
from services.google_sheets_service import log_user_start

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    هندلر دستور /start
    نمایش پیام خوش‌آمد و منوی اصلی
    """
    user = update.effective_user
    user_id = user.id
    username = user.username or "بدون نام کاربری"
    full_name = user.full_name or "نامشخص"
    
    # ثبت ورود کاربر در گوگل شیت
    try:
        await log_user_start(user_id, username, full_name)
    except Exception as e:
        print(f"خطا در ثبت اطلاعات کاربر: {e}")
    
    # پاک کردن کیبورد قبلی (مهم!)
    await update.message.reply_text(
        "در حال راه‌اندازی...",
        reply_markup=ReplyKeyboardRemove()
    )
    
    # ارسال پیام خوش‌آمد با منوی اصلی جدید
    await update.message.reply_text(
        WELCOME_MESSAGE,
        reply_markup=get_main_menu_keyboard()
    )
