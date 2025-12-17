import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from config import BOT_TOKEN
from handlers.start_handler import start_command
from handlers.menu_handler import handle_menu_selection, show_contact_expert
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
from handlers.nursing_consultation import (
    start_consultation, select_disease, answer_question, cancel_consultation,
    SELECTING_DISEASE, ANSWERING_QUESTIONS
)
from keyboards import get_main_menu_keyboard

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
                MessageHandler(filters.Regex('^🔙 بازگشت$'), handle_back_button),
                MessageHandler(filters.TEXT & ~filters.COMMAND, save_blood_sugar)
            ],
            ENTERING_BLOOD_SUGAR_AFTER_MEAL: [
                MessageHandler(filters.Regex('^🔙 بازگشت$'), handle_back_button),
                MessageHandler(filters.TEXT & ~filters.COMMAND, save_blood_sugar)
            ],
            ENTERING_BLOOD_PRESSURE_SYSTOLIC: [
                MessageHandler(filters.Regex('^🔙 بازگشت$'), handle_back_button),
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_blood_pressure_diastolic)
            ],
            ENTERING_BLOOD_PRESSURE_DIASTOLIC: [
                MessageHandler(filters.Regex('^🔙 بازگشت$'), handle_back_button),
                MessageHandler(filters.TEXT & ~filters.COMMAND, save_blood_pressure)
            ],
            ENTERING_WEIGHT: [
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
            MessageHandler(filters.Regex('^🔙 بازگشت$'), handle_back_button),
            CommandHandler('cancel', cancel)
        ]
    )
    
    # Conversation Handler برای مشاوره پرستاری
    nursing_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex('^🩺 مشاوره پرستاری$'), start_consultation)
        ],
        states={
            SELECTING_DISEASE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, select_disease)
            ],
            ANSWERING_QUESTIONS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, answer_question)
            ]
        },
        fallbacks=[
            MessageHandler(filters.Regex('^🔙 بازگشت'), cancel_consultation),
            CommandHandler('cancel', cancel_consultation)
        ]
    )
    
    # اضافه کردن هندلرها به ترتیب اولویت
    
    # 1. دستور /start
    application.add_handler(CommandHandler("start", start_command))
    
    # 2. Conversation Handlers - باید قبل از message handlers عادی باشن
    application.add_handler(nursing_conv_handler)
    application.add_handler(symptoms_conv_handler)
    
    # 3. هندلر اطلاعات تماس
    async def show_contact_info(update, context):
        await update.message.reply_text(
            "📞 اطلاعات تماس\n\n"
            "برای دریافت مشاوره تخصصی:\n\n"
            "☎️ تلفن: 021-12345678\n"
            "📱 موبایل: 0912-345-6789\n"
            "📧 ایمیل: info@hospital.com\n"
            "🕐 ساعات پاسخگویی: 8 صبح تا 8 شب\n\n"
            "⚠️ در مواقع اورژانسی با 115 تماس بگیرید.",
            reply_markup=get_main_menu_keyboard()
        )
    
    application.add_handler(MessageHandler(
        filters.Regex('^📞 اطلاعات تماس$'),
        show_contact_info
    ))
    
    # 4. هندلر بازگشت از منوی ارتباط با کارشناس
    async def back_to_main(update, context):
        # فقط اگه در conversation نباشیم
        if 'nursing' not in context.user_data and 'in_symptoms_menu' not in context.user_data:
            await start_command(update, context)
    
    application.add_handler(MessageHandler(
        filters.Regex('^🔙 بازگشت$'),
        back_to_main
    ))
    
    # 5. هندلر منوی اصلی
    application.add_handler(MessageHandler(
        filters.Regex('^(آموزش|ارتباط با کارشناس)$'), 
        handle_menu_selection
    ))
    
    # 6. هندلر منوی آموزش - بیماری‌ها
    application.add_handler(MessageHandler(
        filters.Regex('^(دیابت نوع ۲|فشار خون|بیماری قلبی عروقی)$'),
        handle_disease_selection
    ))
    
    # شروع ربات
    print("🤖 ربات در حال اجرا است...")
    print("✅ Health check server راه‌اندازی شد")
    print("📡 در حال listening برای پیام‌های تلگرام...")
    
    application.run_polling(allowed_updates=["message"])

if __name__ == '__main__':
    main()
