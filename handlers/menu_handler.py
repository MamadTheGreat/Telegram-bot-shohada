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
    """نمایش منوی ارتباط با کارشناس"""
    keyboard = [
        ["🤖 مشاوره هوشمند (AI)"],
        ["💬 مشاوره پرستاری (فلو سوالات)"],
        ["📞 اطلاعات تماس"],
        ["🔙 بازگشت"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    message = """
👨‍⚕️ ارتباط با کارشناس

لطفاً یکی از گزینه‌ها را انتخاب کنید:

🤖 مشاوره هوشمند (AI): پرسش و پاسخ آزاد با هوش مصنوعی
   • پاسخ سریع و فوری
   • امکان پرسیدن هر سوالی
   ⚠️ پاسخ‌ها توسط AI تولید می‌شوند

💬 مشاوره پرستاری (فلو سوالات): پاسخ به سوالات استاندارد
   • فلوی مشخص سوال و جواب
   • آموزش‌های تایید شده

📞 اطلاعات تماس: دریافت شماره تماس و ایمیل
    """
    await update.message.reply_text(
        message,
        reply_markup=reply_markup
    )
