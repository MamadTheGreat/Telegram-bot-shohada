import os
import json

# توکن ربات تلگرام (از متغیر محیطی یا مستقیم)
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Google Gemini API Key (رایگان)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")

# ID فولدر اصلی در Google Drive
MAIN_FOLDER_ID = os.getenv("MAIN_FOLDER_ID", "YOUR_MAIN_FOLDER_ID")

# ID گوگل شیت برای ذخیره اطلاعات کاربران
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "YOUR_GOOGLE_SHEET_ID")

# مسیر فایل credentials گوگل (JSON)
# در Render از متغیر محیطی استفاده می‌کنیم
GOOGLE_CREDENTIALS_FILE = "credentials.json"

# اگر در Render هستیم، credentials را از متغیر محیطی بخوانیم
if os.getenv("GOOGLE_CREDENTIALS_JSON"):
    credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    with open(GOOGLE_CREDENTIALS_FILE, "w") as f:
        f.write(credentials_json)

# نام شیت‌ها در گوگل شیت
USER_DATA_SHEET = "کاربران"
SYMPTOMS_SHEET = "علائم"

# متن پیام خوش‌آمد
WELCOME_MESSAGE = """
🌟 به ربات مشاوره سلامت خوش آمدید! 🌟

من در خدمت شما هستم برای:
✅ دریافت آموزش‌های تخصصی
✅ ثبت و پیگیری علائم
✅ ارتباط با کارشناس

لطفا از منوی زیر یکی را انتخاب کنید:
"""

# نقشه نام بیماری‌ها به نام فولدرها در Google Drive
DISEASE_FOLDERS = {
    "دیابت نوع ۲": "Diabetes Mellitus",
    "فشار خون": "Hypertension",
    "بیماری قلبی عروقی": "Heart disease"
}

# تنظیمات Gemini AI
GEMINI_SYSTEM_PROMPT = """
شما یک دستیار پرستاری هوشمند هستید که به فارسی پاسخ می‌دهید.

وظایف شما:
- راهنمایی کلی در زمینه بیماری‌های مزمن (دیابت، فشار خون، قلبی)
- پاسخ به سوالات درباره مراقبت از بیمار در منزل
- توصیه‌های تغذیه‌ای و سبک زندگی سالم
- توضیح درباره داروها و نحوه مصرف (بدون تجویز)

⚠️ محدودیت‌های شما:
- هرگز تشخیص قطعی نمی‌دهید
- هرگز دارو تجویز نمی‌کنید
- در موارد اورژانسی، حتماً تأکید کنید که باید به پزشک یا اورژانس مراجعه کنند
- همیشه یادآوری کنید که باید با پزشک معالج مشورت شود

سبک پاسخ:
- محترمانه و دلسوزانه
- ساده و قابل فهم
- با ذکر منابع معتبر در صورت امکان
- همراه با هشدارهای لازم

در پایان هر پاسخ، این جمله را اضافه کنید:
"⚠️ این راهنمایی کلی است و جایگزین مشاوره پزشک نمی‌شود. لطفاً با پزشک معالج خود مشورت کنید."
"""
