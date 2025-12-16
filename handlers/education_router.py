from telegram import Update
from telegram.ext import ContextTypes

async def route_blood_pressure(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    مسیریابی برای "فشار خون" - 
    به آموزش یا ثبت علائم هدایت می‌کند
    """
    # چک کنیم که از کدوم منو اومده
    if context.user_data.get('in_symptoms_menu'):
        # از منوی ثبت علائم اومده
        from handlers.symptoms_handler import ask_blood_pressure_systolic
        return await ask_blood_pressure_systolic(update, context)
    else:
        # از منوی آموزش اومده
        from handlers.education_handler import handle_disease_selection
        return await handle_disease_selection(update, context)
