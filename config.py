import os
import json

# توکن ربات تلگرام (از متغیر محیطی یا مستقیم)
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

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
    "دیابت نوع ۲": "دیابت نوع ۲",
    "فشار خون": "فشار خون",
    "بیماری قلبی عروقی": "بیماری قلبی عروقی"
}
