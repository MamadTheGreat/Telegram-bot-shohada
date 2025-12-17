from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from keyboards import get_main_menu_keyboard

# States
SELECTING_DISEASE, ANSWERING_QUESTIONS = range(2)

# فلوهای پرستاری با سؤالات هوشمندتر
NURSING_FLOWS = {
    "diabetes": {
        "name": "دیابت نوع ۲",
        "questions": [
            {
                "q": "چند وقته که دیابت دارید؟",
                "tips": ["کمتر از یک سال", "۱ تا ۵ سال", "بیشتر از ۵ سال"]
            },
            {
                "q": "قند خون رو در منزل چک می‌کنید؟ اگه بله، آخرین عدد چقدر بود؟",
                "tips": []
            },
            {
                "q": "این علائم رو داشتید؟\n• تشنگی زیاد\n• تکرر ادرار\n• خستگی شدید\n• تاری دید",
                "tips": ["بله", "خیر", "بعضی از اینها"]
            },
            {
                "q": "دارو یا انسولین مصرف می‌کنید؟ آیا مصرف منظمه؟",
                "tips": ["بله، منظم", "بله، گاهی فراموش میشه", "خیر"]
            },
            {
                "q": "آیا زخم پا یا بی‌حسی در پاها دارید؟",
                "tips": ["بله", "خیر"]
            }
        ],
        "education": """
📚 آموزش‌های کلیدی:

✅ پایش قند خون:
• ناشتا و ۲ ساعت بعد غذا چک کنید
• دفترچه ثبت قند تهیه کنید

✅ تغذیه:
• غذا در ساعات منظم
• کاهش قند و نشاسته ساده
• افزایش سبزیجات

✅ فعالیت:
• روزی ۳۰ دقیقه پیاده‌روی
• قبل از ورزش قند چک شود

✅ مراقبت از پا:
• روزانه پاها بررسی شود
• کفش مناسب استفاده کنید
        """,
        "warning": """
⚠️ هشدارهای مهم:

🚨 مراجعه فوری در صورت:
• قند خون بالاتر از ۳۰۰
• قند خون پایین‌تر از ۷۰ با علائم
• تهوع و استفراغ مکرر
• زخم پا که بهبود نمی‌یابد
• تاری دید ناگهانی

این گفتگو جایگزین ویزیت پزشک نیست.
        """
    },
    "hypertension": {
        "name": "فشار خون بالا",
        "questions": [
            {
                "q": "فشار خون بالا چند وقته تشخیص داده شده؟",
                "tips": ["جدید", "چند ماه", "چند سال"]
            },
            {
                "q": "فشار خون رو در منزل اندازه می‌گیرید؟ آخرین عدد چقدر بود؟",
                "tips": []
            },
            {
                "q": "این علائم رو تجربه کردید؟\n• سردرد شدید\n• سرگیجه\n• درد قفسه سینه\n• تاری دید",
                "tips": ["بله", "خیر", "بعضی از اینها"]
            },
            {
                "q": "داروی فشار خون مصرف می‌کنید؟ مصرف منظمه؟",
                "tips": ["بله، منظم", "بله، گاهی فراموش میشه", "خیر"]
            },
            {
                "q": "سابقه بیماری قلبی یا کلیوی دارید؟",
                "tips": ["بله", "خیر"]
            }
        ],
        "education": """
📚 آموزش‌های کلیدی:

✅ کنترل فشار:
• صبح و عصر فشار چک کنید
• دفترچه ثبت فشار داشته باشید

✅ تغذیه:
• کاهش نمک (کمتر از یک قاشق چایخوری)
• افزایش میوه و سبزیجات
• پرهیز از غذاهای چرب

✅ سبک زندگی:
• کاهش وزن در صورت اضافه‌وزن
• ترک سیگار
• کنترل استرس

✅ فعالیت:
• روزی ۳۰ دقیقه پیاده‌روی
        """,
        "warning": """
⚠️ هشدارهای مهم:

🚨 مراجعه فوری در صورت:
• فشار بالاتر از ۱۸۰/۱۲۰
• سردرد شدید ناگهانی
• درد قفسه سینه
• تنگی نفس
• ضعف یکطرفه بدن

این گفتگو جایگزین ویزیت پزشک نیست.
        """
    },
    "cardiac": {
        "name": "بیماری قلبی عروقی",
        "questions": [
            {
                "q": "علائم فعلی شما چیست؟\n• درد قفسه سینه\n• تنگی نفس\n• تپش قلب\n• ضعف",
                "tips": ["درد قفسه سینه", "تنگی نفس", "تپش قلب", "چیز دیگر"]
            },
            {
                "q": "اگه درد قفسه سینه دارید، به بازو، گردن یا فک منتشر میشه؟",
                "tips": ["بله", "خیر", "درد ندارم"]
            },
            {
                "q": "این علائم در چه شرایطی تشدید میشه؟\n• هنگام فعالیت\n• استراحت\n• هر دو",
                "tips": ["فعالیت", "استراحت", "هر دو"]
            },
            {
                "q": "سابقه حمله قلبی یا بستری قبلی دارید؟",
                "tips": ["بله", "خیر"]
            },
            {
                "q": "داروی قلب مصرف می‌کنید؟ (مثل آسپرین، بتابلوکر) مصرف منظمه؟",
                "tips": ["بله، منظم", "بله، گاهی فراموش میشه", "خیر"]
            }
        ],
        "education": """
📚 آموزش‌های کلیدی:

✅ مصرف دارو:
• دقیقاً طبق تجویز پزشک
• داشتن لیست داروها همراه

✅ تغذیه:
• کاهش چربی و نمک
• افزایش فیبر و میوه
• پرهیز از سرخ‌کردنی

✅ فعالیت:
• فعالیت متناسب با توان
• شروع آرام و تدریجی
• توقف در صورت درد یا تنگی نفس

✅ سبک زندگی:
• ترک سیگار قطعی
• کنترل استرس
• خواب کافی
        """,
        "warning": """
⚠️ هشدارهای مهم:

🚨 مراجعه فوری (۱۱۵) در صورت:
• درد قفسه سینه بیش از ۵ دقیقه
• تنگی نفس شدید ناگهانی
• عرق سرد و حالت تهوع
• درد انتشاری به بازو/فک
• از دست دادن هوشیاری

این گفتگو جایگزین ویزیت پزشک نیست.
        """
    }
}

def get_disease_selection_keyboard():
    """کیبورد انتخاب بیماری"""
    keyboard = [
        ["دیابت نوع ۲"],
        ["فشار خون بالا"],
        ["بیماری قلبی عروقی"],
        ["🔙 بازگشت به منوی اصلی"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_question_keyboard(tips):
    """کیبورد پاسخ‌های پیشنهادی"""
    if not tips:
        keyboard = [["🔙 بازگشت"]]
    else:
        keyboard = [[tip] for tip in tips]
        keyboard.append(["🔙 بازگشت"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start_consultation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع مشاوره پرستاری"""
    await update.message.reply_text(
        "🩺 مشاوره پرستاری\n\n"
        "سلام! من کارشناس پرستاری هستم.\n"
        "می‌تونم در مورد این بیماری‌ها راهنماییتون کنم:\n\n"
        "⚠️ توجه: این گفتگو جایگزین ویزیت پزشک نیست.\n\n"
        "لطفاً موضوع مورد نظرتون رو انتخاب کنید:",
        reply_markup=get_disease_selection_keyboard()
    )
    return SELECTING_DISEASE

async def select_disease(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """انتخاب بیماری"""
    text = update.message.text
    
    # بازگشت به منوی اصلی
    if text == "🔙 بازگشت به منوی اصلی":
        await update.message.reply_text(
            "مشاوره لغو شد.",
            reply_markup=get_main_menu_keyboard()
        )
        return ConversationHandler.END
    
    # نقشه متن به کلید
    disease_map = {
        "دیابت نوع ۲": "diabetes",
        "فشار خون بالا": "hypertension",
        "بیماری قلبی عروقی": "cardiac"
    }
    
    disease_key = disease_map.get(text)
    
    if disease_key:
        context.user_data['nursing'] = {
            'disease': disease_key,
            'step': 0,
            'answers': []
        }
        
        # ارسال اولین سؤال
        flow = NURSING_FLOWS[disease_key]
        first_q = flow['questions'][0]
        
        await update.message.reply_text(
            f"✅ موضوع انتخابی: {flow['name']}\n\n"
            f"چند سؤال ازتون می‌پرسم تا بتونم راهنمایی بهتری بکنم.\n\n"
            f"❓ {first_q['q']}",
            reply_markup=get_question_keyboard(first_q['tips'])
        )
        return ANSWERING_QUESTIONS
    
    await update.message.reply_text(
        "لطفاً از گزینه‌های موجود انتخاب کنید:",
        reply_markup=get_disease_selection_keyboard()
    )
    return SELECTING_DISEASE

async def answer_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دریافت پاسخ و پرسیدن سؤال بعدی"""
    text = update.message.text
    
    # بازگشت
    if text == "🔙 بازگشت":
        await update.message.reply_text(
            "مشاوره لغو شد.",
            reply_markup=get_main_menu_keyboard()
        )
        context.user_data.pop('nursing', None)
        return ConversationHandler.END
    
    nursing_data = context.user_data.get('nursing', {})
    disease = nursing_data.get('disease')
    step = nursing_data.get('step', 0)
    
    if not disease:
        return ConversationHandler.END
    
    # ذخیره پاسخ
    nursing_data['answers'].append(text)
    nursing_data['step'] = step + 1
    
    flow = NURSING_FLOWS[disease]
    questions = flow['questions']
    
    # اگه سؤال بعدی داریم
    if nursing_data['step'] < len(questions):
        next_q = questions[nursing_data['step']]
        await update.message.reply_text(
            f"✅ پاسخ شما ثبت شد.\n\n"
            f"❓ {next_q['q']}",
            reply_markup=get_question_keyboard(next_q['tips'])
        )
        return ANSWERING_QUESTIONS
    
    # پایان سؤالات - ارسال آموزش و هشدار
    await update.message.reply_text(
        "✅ ممنون از پاسخ‌هاتون.\n\n"
        "حالا آموزش‌ها و نکات مهم رو براتون ارسال می‌کنم...",
        reply_markup=get_main_menu_keyboard()
    )
    
    # ارسال آموزش
    await update.message.reply_text(flow['education'])
    
    # ارسال هشدارها
    await update.message.reply_text(flow['warning'])
    
    # پیام پایانی
    await update.message.reply_text(
        "✅ مشاوره به پایان رسید.\n\n"
        "💡 نکته: لطفاً این اطلاعات رو با پزشک معالج خود در میان بگذارید.\n\n"
        "برای مشاوره جدید، از منو گزینه 'ارتباط با کارشناس' رو انتخاب کنید.",
        reply_markup=get_main_menu_keyboard()
    )
    
    # پاک کردن داده
    context.user_data.pop('nursing', None)
    return ConversationHandler.END

async def cancel_consultation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """لغو مشاوره"""
    await update.message.reply_text(
        "مشاوره لغو شد.",
        reply_markup=get_main_menu_keyboard()
    )
    context.user_data.pop('nursing', None)
    return ConversationHandler.END
