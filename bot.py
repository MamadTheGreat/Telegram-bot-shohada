import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import BOT_TOKEN
from handlers.start_handler import start_command
from handlers.menu_handler import handle_menu_selection
from handlers.education_handler import handle_education_menu, handle_disease_selection
from handlers.symptoms_handler import handle_symptoms_menu

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
