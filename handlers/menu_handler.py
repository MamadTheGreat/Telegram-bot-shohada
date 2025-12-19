from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from keyboards import get_education_menu_keyboard, get_symptoms_menu_keyboard

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

لطفاً علامتی که می‌خواهید ثبت کنید را انتخاب کنید:
    """
    await update.message.reply_text(
        message,
        reply_markup=get_symptoms_menu_keyboard()
    )

async def show_contact_expert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش اطلاعات تماس"""
    from keyboards import get_main_menu_keyboard
    
    message = """
📞 اطلاعات تماس

برای دریافت مشاوره تخصصی با ما در ارتباط باشید:

☎️ تلفن: 021-12345678
📱 موبایل: 0912-345-6789
📧 ایمیل: info@hospital.com

🕐 ساعات پاسخگویی: 
   شنبه تا چهارشنبه: 8 صبح تا 8 شب
   پنج‌شنبه: 8 صبح تا 2 بعدازظهر

⚠️ در مواقع اورژانسی با 115 تماس بگیرید.
    """
    
    await update.message.reply_text(
        message,
        reply_markup=get_main_menu_keyboard()
    )
