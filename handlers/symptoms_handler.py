from telegram import Update
from telegram.ext import ContextTypes
from keyboards import get_back_keyboard

async def handle_symptoms_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    هندلر منوی ثبت علائم
    این بخش در مرحله بعدی توسعه داده خواهد شد
    """
    message = """
📝 ثبت علائم

این بخش در حال توسعه است و به زودی فعال خواهد شد.

قابلیت‌های این بخش:
• ثبت علائم روزانه
• پیگیری تاریخچه علائم
• گزارش‌گیری از علائم

    """
    await update.message.reply_text(
        message,
        reply_markup=get_back_keyboard()
    )
