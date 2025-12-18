from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from keyboards import get_main_menu_keyboard
from services.gemini_service import ask_gemini, ask_gemini_with_context

# States
SELECTING_TOPIC, ASKING_QUESTION = range(2)

async def start_ai_consultation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع مشاوره هوشمند با AI"""
    
    keyboard = [
        ["دیابت نوع ۲"],
        ["فشار خون بالا"],
        ["بیماری قلبی عروقی"],
        ["سوال عمومی"],
        ["🔙 بازگشت به منوی اصلی"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    message = """
🤖 مشاوره هوشمند با کمک هوش مصنوعی

⚠️ توجه مهم:
• این سیستم توسط هوش مصنوعی Google Gemini پشتیبانی می‌شود
• پاسخ‌ها راهنمایی کلی هستند و جایگزین مشاوره پزشک نیستند
• در مواقع اورژانسی حتماً با 115 تماس بگیرید

لطفاً موضوع مورد نظر خود را انتخاب کنید:
    """
    
    await update.message.reply_text(message, reply_markup=reply_markup)
    return SELECTING_TOPIC

async def select_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """انتخاب موضوع و شروع پرسش"""
    text = update.message.text
    
    # بازگشت به منوی اصلی
    if text == "🔙 بازگشت به منوی اصلی":
        await update.message.reply_text(
            "مشاوره لغو شد.",
            reply_markup=get_main_menu_keyboard()
        )
        context.user_data.pop('ai_consultation', None)
        return ConversationHandler.END
    
    # ذخیره موضوع انتخابی
    context.user_data['ai_consultation'] = {
        'topic': text
    }
    
    # نقشه موضوعات
    topic_map = {
        "دیابت نوع ۲": "دیابت نوع 2",
        "فشار خون بالا": "فشار خون بالا (هیپرتانسیون)",
        "بیماری قلبی عروقی": "بیماری‌های قلبی و عروقی",
        "سوال عمومی": None
    }
    
    selected_topic = topic_map.get(text)
    
    if selected_topic is not None or text == "سوال عمومی":
        keyboard = [["🔙 بازگشت به منوی اصلی"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        topic_display = selected_topic if selected_topic else "سوالات عمومی"
        
        await update.message.reply_text(
            f"✅ موضوع انتخابی: {topic_display}\n\n"
            f"🤖 حالا سوال خود را بپرسید:\n\n"
            f"مثال:\n"
            f"• چطور قند خونم رو کنترل کنم؟\n"
            f"• چه غذاهایی برای فشار خون مفیده؟\n"
            f"• علائم هشدار دهنده قلبی چیه؟",
            reply_markup=reply_markup
        )
        return ASKING_QUESTION
    
    # موضوع نامعتبر
    await update.message.reply_text(
        "لطفاً از گزینه‌های موجود انتخاب کنید:"
    )
    return SELECTING_TOPIC

async def answer_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت سوال و ارسال پاسخ از AI"""
    
    # بازگشت به منوی اصلی
    if update.message.text == "🔙 بازگشت به منوی اصلی":
        await update.message.reply_text(
            "مشاوره لغو شد.",
            reply_markup=get_main_menu_keyboard()
        )
        context.user_data.pop('ai_consultation', None)
        return ConversationHandler.END
    
    question = update.message.text
    consultation_data = context.user_data.get('ai_consultation', {})
    topic = consultation_data.get('topic')
    
    # نمایش پیام در حال پردازش
    processing_msg = await update.message.reply_text(
        "🤖 در حال پردازش سوال شما...\n"
        "⏳ لطفاً چند لحظه صبر کنید..."
    )
    
    try:
        # نقشه موضوعات
        topic_map = {
            "دیابت نوع ۲": "دیابت نوع 2",
            "فشار خون بالا": "فشار خون بالا (هیپرتانسیون)",
            "بیماری قلبی عروقی": "بیماری‌های قلبی و عروقی",
            "سوال عمومی": None
        }
        
        disease_context = topic_map.get(topic)
        
        # دریافت پاسخ از Gemini
        answer = await ask_gemini_with_context(question, disease_context)
        
        # حذف پیام پردازش
        await processing_msg.delete()
        
        # ارسال پاسخ
        await update.message.reply_text(
            f"🤖 پاسخ هوش مصنوعی:\n\n{answer}\n\n"
            f"━━━━━━━━━━━━━━━\n"
            f"💬 سوال دیگری دارید؟ بپرسید یا به منوی اصلی برگردید."
        )
        
        # ادامه گفتگو
        return ASKING_QUESTION
        
    except Exception as e:
        print(f"خطا در پاسخگویی: {e}")
        await processing_msg.delete()
        await update.message.reply_text(
            "❌ متأسفانه خطایی رخ داد.\n\n"
            "لطفاً دوباره تلاش کنید یا با شماره 021-12345678 تماس بگیرید."
        )
        return ASKING_QUESTION

async def cancel_ai_consultation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """لغو مشاوره"""
    await update.message.reply_text(
        "مشاوره لغو شد.",
        reply_markup=get_main_menu_keyboard()
    )
    context.user_data.pop('ai_consultation', None)
    return ConversationHandler.END
