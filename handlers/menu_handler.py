from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from keyboards import get_education_menu_keyboard, get_back_keyboard, get_main_menu_keyboard

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
    # پاک کردن flag ثبت علائم
    context.user_data['in_symptoms_menu'] = False
    
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
    # این تابع فقط برای compatibility هست
    # ConversationHandler خودش handle میکنه
    pass

async def show_contact_expert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش منوی ارتباط با کارشناس"""
    keyboard = [
        ["🩺 مشاوره پرستاری"],
        ["📞 اطلاعات تماس"],
        ["🔙 بازگشت"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    message = """
👨‍⚕️ ارتباط با کارشناس

لطفاً یکی از گزینه‌ها را انتخاب کنید:

🩺 مشاوره پرستاری: پرسش و پاسخ با کارشناس پرستاری

📞 اطلاعات تماس: دریافت شماره تماس و ایمیل
    """
    await update.message.reply_text(
        message,
        reply_markup=reply_markup
    )
