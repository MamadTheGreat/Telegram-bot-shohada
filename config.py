import os

# توکن ربات تلگرام (از BotFather دریافت کنید)
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# مسیر فایل credentials گوگل (JSON)
GOOGLE_CREDENTIALS_FILE = "credentials.json"

# ID فولدر اصلی در Google Drive که فولدرهای بیماری‌ها در آن هستند
MAIN_FOLDER_ID = "YOUR_MAIN_FOLDER_ID"

# ID گوگل شیت برای ذخیره اطلاعات کاربران
GOOGLE_SHEET_ID = "YOUR_GOOGLE_SHEET_ID"

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
    "دیابت نوع ۲": "دیابت نوع ۲",
    "فشار خون": "فشار خون",
    "بیماری قلبی عروقی": "بیماری قلبی عروقی"
}
