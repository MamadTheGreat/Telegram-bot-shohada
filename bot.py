import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from config import BOT_TOKEN
from handlers.start_handler import start_command
from handlers.menu_handler import handle_menu_selection
from handlers.education_handler import handle_education_menu, handle_disease_selection
from handlers.education_router import route_blood_pressure
from handlers.symptoms_handler import (
    handle_symptoms_menu, handle_blood_sugar_menu, handle_back_button,
    ask_fasting_blood_sugar, ask_after_meal_blood_sugar, save_blood_sugar,
    ask_blood_pressure_systolic, ask_blood_pressure_diastolic, save_blood_pressure,
    ask_weight, save_weight,
    show_history_menu, send_blood_sugar_chart, send_blood_pressure_chart, send_weight_chart,
    cancel,
    CHOOSING_SYMPTOM, ENTERING_BLOOD_SUGAR_FASTING, ENTERING_BLOOD_SUGAR_AFTER_MEAL,
    ENTERING_BLOOD_PRESSURE_SYSTOLIC, ENTERING_BLOOD_PRESSURE_DIASTOLIC,
    ENTERING_WEIGHT, VIEWING_HISTORY
)

class HealthCheckHandler(BaseHTTPRequestHandler):
    """یک HTTP handler ساده برای health check"""
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Bot is running!')
    
    def log_message(self, format, *args):
        """غیرفعال کردن لاگ‌های HTTP"""
        pass

def run_health_check_server():
    """اجرای یک HTTP server ساده برای Render"""
    port = int(os.getenv('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    print(f"Health check server running on port {port}")
    server.serve_forever()

def main():
    """راه‌اندازی ربات تلگرام"""
    
    # اجرای health check server در یک thread جداگانه
    health_thread = threading.Thread(target=run_health_check_server, daemon=True)
    health_thread.start()
    
    # ساخت Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Conversation Handler برای ثبت علائم
    symptoms_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex('^ثبت علائم$'), handle_symptoms_menu)
        ],
        states={
            CHOOSING_SYMPTOM: [
                MessageHandler(filters.Regex('^قند خون$'), handle_blood_sugar_menu),
                MessageHandler(filters.Regex('^قند خون ناشتا$'), ask_fasting_blood_sugar),
                MessageHandler(filters.Regex('^قند خون بعد از غذا$'), ask_after_meal_blood_sugar),
                MessageHandler(filters.Regex('^فشار خون$'), ask_blood_pressure_systolic),
                MessageHandler(filters.Regex('^وزن$'), ask_weight),
                MessageHandler(filters.Regex('^📊 تاریخچه علائم$'), show_history_menu),
                MessageHandler(filters.Regex('^🔙 بازگشت$'), handle_back_button),
            ],
            ENTERING_BLOOD_SUGAR_FASTING: [
                MessageHandler(filters.Regex('^(بازگشت به منوی اصلی)$'), start_command),
                MessageHandler(filters.Regex('^🔙 بازگشت$'), handle_back_button),
                MessageHandler(filters.TEXT & ~filters.COMMAND, save_blood_sugar)
            ],
            ENTERING_BLOOD_SUGAR_AFTER_MEAL: [
                MessageHandler(filters.Regex('^(بازگشت به منوی اصلی)$'), start_command),
                MessageHandler(filters.Regex('^🔙 بازگشت$'), handle_back_button),
                MessageHandler(filters.TEXT & ~filters.COMMAND, save_blood_sugar)
            ],
            ENTERING_BLOOD_PRESSURE_SYSTOLIC: [
                MessageHandler(filters.Regex('^(بازگشت به منوی اصلی)$'), start_command),
                MessageHandler(filters.Regex('^🔙 بازگشت$'), handle_back_button),
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_blood_pressure_diastolic)
            ],
            ENTERING_BLOOD_PRESSURE_DIASTOLIC: [
                MessageHandler(filters.Regex('^(بازگشت به منوی اصلی)$'), start_command),
                MessageHandler(filters.Regex('^🔙 بازگشت$'), handle_back_button),
                MessageHandler(filters.TEXT & ~filters.COMMAND, save_blood_pressure)
            ],
            ENTERING_WEIGHT: [
                MessageHandler(filters.Regex('^(بازگشت به منوی اصلی)$'), start_command),
                MessageHandler(filters.Regex('^🔙 بازگشت$'), handle_back_button),
                MessageHandler(filters.TEXT & ~filters.COMMAND, save_weight)
            ],
            VIEWING_HISTORY: [
                MessageHandler(filters.Regex('^📊 نمودار قند خون$'), send_blood_sugar_chart),
                MessageHandler(filters.Regex('^📊 نمودار فشار خون$'), send_blood_pressure_chart),
                MessageHandler(filters.Regex('^📊 نمودار وزن$'), send_weight_chart),
                MessageHandler(filters.Regex('^🔙 بازگشت$'), handle_back_button),
            ],
        },
        fallbacks=[
            MessageHandler(filters.Regex('^بازگشت به منوی اصلی$'), start_command),
            MessageHandler(filters.Regex('^🔙 بازگشت$'), handle_back_button),
            CommandHandler('cancel', cancel)
        ]
    )
    
    # اضافه کردن هندلرها
    application.add_handler(CommandHandler("start", start_command))
    
    # Conversation Handler برای ثبت علائم - باید قبل از بقیه هندلرها باشه
    application.add_handler(symptoms_conv_handler)
    
    # هندلر برای منوی اصلی (به جز ثبت علائم)
    application.add_handler(MessageHandler(
        filters.Regex('^(آموزش|ارتباط با کارشناس)$'), 
        handle_menu_selection
    ))
    
    # هندلر برای "فشار خون" که می‌تونه از آموزش یا ثبت علائم باشه
    application.add_handler(MessageHandler(
        filters.Regex('^فشار خون$'),
        route_blood_pressure
    ))
    
    # هندلر برای منوی آموزش - بدون فشار خون
    application.add_handler(MessageHandler(
        filters.Regex('^(دیابت نوع ۲|بیماری قلبی عروقی)$'),
        handle_disease_selection
    ))
    
    # هندلر برای بازگشت به منوی اصلی از آموزش
    application.add_handler(MessageHandler(
        filters.Regex('^🔙 بازگشت$') & ~filters.Regex('^ثبت علائم$'),
        start_command
    ))
    
    # شروع ربات
    print("ربات در حال اجرا است...")
    application.run_polling(allowed_updates=["message"])

if __name__ == '__main__':
    main()
