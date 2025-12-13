from telegram import Update
from telegram.ext import ContextTypes
from keyboards import get_education_menu_keyboard, get_back_keyboard

async def handle_menu_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    هندلر انتخاب از منوی اصلی
    """
    text = update.message.text
    
    if text == "آموزش":
        await show_education_menu(update, context)
    
    elif text == "ثبت علائم":
        await show_symptoms_menu(update, context)
    
    elif text == "ارتباط با کارشناس":
        await show_contact_expert(update, context)

async def show_education_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش منوی آموزش"""
    message = """
📚 منوی آموزش

لطفا موضوع مورد نظر خود را انتخاب کنید:
    """
    await update.message.reply_text(
        message,
        reply_markup=get_education_menu_keyboard()
    )

async def show_symptoms_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش منوی ثبت علائم"""
    message = """
📝 ثبت علائم

این بخش در مرحله بعدی توسعه داده خواهد شد.
    """
    await update.message.reply_text(
        message,
        reply_markup=get_back_keyboard()
    )

async def show_contact_expert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش اطلاعات تماس با کارشناس"""
    message = """
👨‍⚕️ ارتباط با کارشناس

این بخش در مرحله بعدی توسعه داده خواهد شد.
    """
    await update.message.reply_text(
        message,
        reply_markup=get_back_keyboard()
    )
