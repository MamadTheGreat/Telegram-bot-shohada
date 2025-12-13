import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import BOT_TOKEN
from handlers.start_handler import start_command
from handlers.menu_handler import handle_menu_selection
from handlers.education_handler import handle_education_menu, handle_disease_selection
from handlers.symptoms_handler import handle_symptoms_menu

def main():
    """راه‌اندازی ربات تلگرام"""
    
    # ساخت Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # اضافه کردن هندلرها
    application.add_handler(CommandHandler("start", start_command))
    
    # هندلر برای منوی اصلی
    application.add_handler(MessageHandler(
        filters.Regex('^(آموزش|ثبت علائم|ارتباط با کارشناس)$'), 
        handle_menu_selection
    ))
    
    # هندلر برای منوی آموزش
    application.add_handler(MessageHandler(
        filters.Regex('^(دیابت نوع ۲|فشار خون|بیماری قلبی عروقی)$'),
        handle_disease_selection
    ))
    
    # هندلر برای بازگشت به منوی اصلی
    application.add_handler(MessageHandler(
        filters.Regex('^(بازگشت به منوی اصلی|🔙 بازگشت)$'),
        start_command
    ))
    
    # شروع ربات
    print("ربات در حال اجرا است...")
    application.run_polling(allowed_updates=["message"])

if __name__ == '__main__':
    main()
