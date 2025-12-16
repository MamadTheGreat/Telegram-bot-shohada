from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from keyboards import get_symptoms_menu_keyboard, get_back_keyboard, get_blood_sugar_menu_keyboard, get_history_menu_keyboard
from services.google_sheets_service import save_symptom, get_user_symptoms
from services.chart_service import generate_chart
import os

# States برای Conversation Handler
CHOOSING_SYMPTOM = 1
ENTERING_BLOOD_SUGAR_FASTING = 2
ENTERING_BLOOD_SUGAR_AFTER_MEAL = 3
ENTERING_BLOOD_PRESSURE_SYSTOLIC = 4
ENTERING_BLOOD_PRESSURE_DIASTOLIC = 5
ENTERING_WEIGHT = 6
VIEWING_HISTORY = 7

async def handle_symptoms_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش منوی ثبت علائم"""
    # علامت‌گذاری که در منوی ثبت علائم هستیم
    context.user_data['in_symptoms_menu'] = True
    
    message = """
📝 ثبت علائم

لطفاً علامتی که می‌خواهید ثبت کنید را انتخاب کنید:
    """
    await update.message.reply_text(
        message,
        reply_markup=get_symptoms_menu_keyboard()
    )
    return CHOOSING_SYMPTOM

async def handle_blood_sugar_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش منوی قند خون"""
    message = """
🩸 ثبت قند خون

لطفاً نوع اندازه‌گیری را انتخاب کنید:
    """
    await update.message.reply_text(
        message,
        reply_markup=get_blood_sugar_menu_keyboard()
    )
    return CHOOSING_SYMPTOM

async def ask_fasting_blood_sugar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """درخواست قند خون ناشتا"""
    await update.message.reply_text(
        "🩸 قند خون ناشتا\n\n"
        "لطفاً مقدار قند خون ناشتای خود را بر حسب mg/dL وارد کنید:\n"
        "(فقط عدد، مثال: 95)",
        reply_markup=get_back_keyboard()
    )
    context.user_data['symptom_type'] = 'قند ناشتا'
    return ENTERING_BLOOD_SUGAR_FASTING

async def ask_after_meal_blood_sugar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """درخواست قند خون بعد از غذا"""
    await update.message.reply_text(
        "🩸 قند خون بعد از غذا\n\n"
        "لطفاً مقدار قند خون بعد از غذای خود را بر حسب mg/dL وارد کنید:\n"
        "(فقط عدد، مثال: 140)",
        reply_markup=get_back_keyboard()
    )
    context.user_data['symptom_type'] = 'قند بعد از غذا'
    return ENTERING_BLOOD_SUGAR_AFTER_MEAL

async def save_blood_sugar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ذخیره قند خون"""
    try:
        value = float(update.message.text)
        
        if value < 0 or value > 600:
            await update.message.reply_text(
                "❌ مقدار وارد شده نامعتبر است!\n"
                "لطفاً عددی بین 0 تا 600 وارد کنید."
            )
            return ENTERING_BLOOD_SUGAR_FASTING
        
        user = update.effective_user
        symptom_type = context.user_data.get('symptom_type', 'قند خون')
        
        # ذخیره در گوگل شیت
        success = await save_symptom(
            user_id=user.id,
            username=user.username or "بدون نام",
            symptom_type=symptom_type,
            value=f"{value} mg/dL"
        )
        
        if success:
            await update.message.reply_text(
                f"✅ {symptom_type} شما با موفقیت ثبت شد!\n\n"
                f"📊 مقدار: {value} mg/dL\n\n"
                "می‌توانید علامت دیگری ثبت کنید یا به منوی اصلی برگردید.",
                reply_markup=get_symptoms_menu_keyboard()
            )
        else:
            await update.message.reply_text(
                "❌ خطا در ذخیره اطلاعات. لطفاً دوباره تلاش کنید.",
                reply_markup=get_symptoms_menu_keyboard()
            )
        
        return CHOOSING_SYMPTOM
        
    except ValueError:
        await update.message.reply_text(
            "❌ لطفاً فقط عدد وارد کنید!\n"
            "مثال: 95"
        )
        return ENTERING_BLOOD_SUGAR_FASTING

async def ask_blood_pressure_systolic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """درخواست فشار خون سیستولیک"""
    await update.message.reply_text(
        "💓 ثبت فشار خون\n\n"
        "لطفاً فشار خون سیستولیک (عدد بزرگ‌تر) را وارد کنید:\n"
        "(فقط عدد، مثال: 120)",
        reply_markup=get_back_keyboard()
    )
    return ENTERING_BLOOD_PRESSURE_SYSTOLIC

async def ask_blood_pressure_diastolic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """درخواست فشار خون دیاستولیک"""
    try:
        systolic = int(update.message.text)
        
        if systolic < 70 or systolic > 250:
            await update.message.reply_text(
                "❌ مقدار نامعتبر است!\n"
                "فشار خون سیستولیک معمولاً بین 70 تا 250 است.\n"
                "لطفاً دوباره وارد کنید:"
            )
            return ENTERING_BLOOD_PRESSURE_SYSTOLIC
        
        context.user_data['systolic'] = systolic
        
        await update.message.reply_text(
            "💓 ثبت فشار خون\n\n"
            "لطفاً فشار خون دیاستولیک (عدد کوچک‌تر) را وارد کنید:\n"
            "(فقط عدد، مثال: 80)"
        )
        return ENTERING_BLOOD_PRESSURE_DIASTOLIC
        
    except ValueError:
        await update.message.reply_text(
            "❌ لطفاً فقط عدد وارد کنید!\n"
            "مثال: 120"
        )
        return ENTERING_BLOOD_PRESSURE_SYSTOLIC

async def save_blood_pressure(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ذخیره فشار خون"""
    try:
        diastolic = int(update.message.text)
        
        if diastolic < 40 or diastolic > 150:
            await update.message.reply_text(
                "❌ مقدار نامعتبر است!\n"
                "فشار خون دیاستولیک معمولاً بین 40 تا 150 است.\n"
                "لطفاً دوباره وارد کنید:"
            )
            return ENTERING_BLOOD_PRESSURE_DIASTOLIC
        
        systolic = context.user_data.get('systolic')
        user = update.effective_user
        
        # ذخیره در گوگل شیت
        success = await save_symptom(
            user_id=user.id,
            username=user.username or "بدون نام",
            symptom_type="فشار خون",
            value=f"{systolic}/{diastolic} mmHg"
        )
        
        if success:
            await update.message.reply_text(
                f"✅ فشار خون شما با موفقیت ثبت شد!\n\n"
                f"📊 مقدار: {systolic}/{diastolic} mmHg\n\n"
                "می‌توانید علامت دیگری ثبت کنید یا به منوی اصلی برگردید.",
                reply_markup=get_symptoms_menu_keyboard()
            )
        else:
            await update.message.reply_text(
                "❌ خطا در ذخیره اطلاعات. لطفاً دوباره تلاش کنید.",
                reply_markup=get_symptoms_menu_keyboard()
            )
        
        return CHOOSING_SYMPTOM
        
    except ValueError:
        await update.message.reply_text(
            "❌ لطفاً فقط عدد وارد کنید!\n"
            "مثال: 80"
        )
        return ENTERING_BLOOD_PRESSURE_DIASTOLIC

async def ask_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """درخواست وزن"""
    await update.message.reply_text(
        "⚖️ ثبت وزن\n\n"
        "لطفاً وزن خود را بر حسب کیلوگرم وارد کنید:\n"
        "(می‌توانید اعشار هم وارد کنید، مثال: 75.5)",
        reply_markup=get_back_keyboard()
    )
    return ENTERING_WEIGHT

async def save_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ذخیره وزن"""
    try:
        weight = float(update.message.text)
        
        if weight < 20 or weight > 300:
            await update.message.reply_text(
                "❌ مقدار نامعتبر است!\n"
                "لطفاً عددی بین 20 تا 300 وارد کنید."
            )
            return ENTERING_WEIGHT
        
        user = update.effective_user
        
        # ذخیره در گوگل شیت
        success = await save_symptom(
            user_id=user.id,
            username=user.username or "بدون نام",
            symptom_type="وزن",
            value=f"{weight} kg"
        )
        
        if success:
            await update.message.reply_text(
                f"✅ وزن شما با موفقیت ثبت شد!\n\n"
                f"⚖️ مقدار: {weight} کیلوگرم\n\n"
                "می‌توانید علامت دیگری ثبت کنید یا به منوی اصلی برگردید.",
                reply_markup=get_symptoms_menu_keyboard()
            )
        else:
            await update.message.reply_text(
                "❌ خطا در ذخیره اطلاعات. لطفاً دوباره تلاش کنید.",
                reply_markup=get_symptoms_menu_keyboard()
            )
        
        return CHOOSING_SYMPTOM
        
    except ValueError:
        await update.message.reply_text(
            "❌ لطفاً عدد صحیح وارد کنید!\n"
            "مثال: 75.5"
        )
        return ENTERING_WEIGHT

async def show_history_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش منوی تاریخچه"""
    message = """
📊 تاریخچه علائم

لطفاً نمودار مورد نظر را انتخاب کنید:
    """
    await update.message.reply_text(
        message,
        reply_markup=get_history_menu_keyboard()
    )
    return VIEWING_HISTORY

async def send_blood_sugar_chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ارسال نمودار قند خون"""
    user = update.effective_user
    
    processing_msg = await update.message.reply_text(
        "⏳ در حال تهیه نمودار قند خون...\nلطفاً کمی صبر کنید."
    )
    
    try:
        # دریافت داده‌های قند خون
        data = await get_user_symptoms(user.id, "قند")
        
        if not data:
            await processing_msg.delete()
            await update.message.reply_text(
                "❌ هنوز هیچ داده‌ای برای قند خون ثبت نشده است!\n\n"
                "ابتدا از منوی 'ثبت علائم' قند خون خود را ثبت کنید.",
                reply_markup=get_history_menu_keyboard()
            )
            return VIEWING_HISTORY
        
        # ساخت نمودار
        chart_path = await generate_chart(data, "قند خون", "mg/dL")
        
        await processing_msg.delete()
        
        # ارسال نمودار
        with open(chart_path, 'rb') as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=f"📊 نمودار قند خون\n\n"
                        f"📈 تعداد رکوردها: {len(data)}\n"
                        f"📅 از {data[0]['date']} تا {data[-1]['date']}",
                reply_markup=get_history_menu_keyboard()
            )
        
        # حذف فایل موقت
        os.remove(chart_path)
        
    except Exception as e:
        print(f"خطا در ساخت نمودار قند خون: {e}")
        await processing_msg.delete()
        await update.message.reply_text(
            "❌ خطا در تهیه نمودار. لطفاً دوباره تلاش کنید.",
            reply_markup=get_history_menu_keyboard()
        )
    
    return VIEWING_HISTORY

async def send_blood_pressure_chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ارسال نمودار فشار خون"""
    user = update.effective_user
    
    processing_msg = await update.message.reply_text(
        "⏳ در حال تهیه نمودار فشار خون...\nلطفاً کمی صبر کنید."
    )
    
    try:
        data = await get_user_symptoms(user.id, "فشار خون")
        
        if not data:
            await processing_msg.delete()
            await update.message.reply_text(
                "❌ هنوز هیچ داده‌ای برای فشار خون ثبت نشده است!",
                reply_markup=get_history_menu_keyboard()
            )
            return VIEWING_HISTORY
        
        chart_path = await generate_chart(data, "فشار خون", "mmHg")
        
        await processing_msg.delete()
        
        with open(chart_path, 'rb') as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=f"📊 نمودار فشار خون\n\n"
                        f"📈 تعداد رکوردها: {len(data)}",
                reply_markup=get_history_menu_keyboard()
            )
        
        os.remove(chart_path)
        
    except Exception as e:
        print(f"خطا در ساخت نمودار فشار خون: {e}")
        await processing_msg.delete()
        await update.message.reply_text(
            "❌ خطا در تهیه نمودار.",
            reply_markup=get_history_menu_keyboard()
        )
    
    return VIEWING_HISTORY

async def send_weight_chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ارسال نمودار وزن"""
    user = update.effective_user
    
    processing_msg = await update.message.reply_text(
        "⏳ در حال تهیه نمودار وزن...\nلطفاً کمی صبر کنید."
    )
    
    try:
        data = await get_user_symptoms(user.id, "وزن")
        
        if not data:
            await processing_msg.delete()
            await update.message.reply_text(
                "❌ هنوز هیچ داده‌ای برای وزن ثبت نشده است!",
                reply_markup=get_history_menu_keyboard()
            )
            return VIEWING_HISTORY
        
        chart_path = await generate_chart(data, "وزن", "kg")
        
        await processing_msg.delete()
        
        with open(chart_path, 'rb') as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=f"📊 نمودار وزن\n\n"
                        f"📈 تعداد رکوردها: {len(data)}",
                reply_markup=get_history_menu_keyboard()
            )
        
        os.remove(chart_path)
        
    except Exception as e:
        print(f"خطا در ساخت نمودار وزن: {e}")
        await processing_msg.delete()
        await update.message.reply_text(
            "❌ خطا در تهیه نمودار.",
            reply_markup=get_history_menu_keyboard()
        )
    
    return VIEWING_HISTORY

async def handle_back_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر دکمه بازگشت - برگشت به منوی اصلی"""
    from keyboards import get_main_menu_keyboard
    from handlers.start_handler import start_command
    
    # پاک کردن user_data
    context.user_data.clear()
    
    # برگشت به منوی اصلی
    return await start_command(update, context)
    """لغو عملیات"""
    from keyboards import get_main_menu_keyboard
    
    # پاک کردن user_data
    context.user_data.clear()
    
    await update.message.reply_text(
        "عملیات لغو شد.",
        reply_markup=get_main_menu_keyboard()
    )
    return ConversationHandler.END
