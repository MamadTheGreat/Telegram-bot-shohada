from telegram import Update
from telegram.ext import ContextTypes
from keyboards import get_education_menu_keyboard, get_back_keyboard
from services.google_drive_service import get_videos_from_folder
from config import DISEASE_FOLDERS

async def handle_education_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش منوی آموزش"""
    message = """
📚 منوی آموزش

لطفا موضوع مورد نظر خود را انتخاب کنید:
    """
    await update.message.reply_text(
        message,
        reply_markup=get_education_menu_keyboard()
    )

async def handle_disease_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    هندلر انتخاب بیماری و ارسال فایل‌های آموزشی
    """
    disease_name = update.message.text
    
    # نمایش پیام در حال پردازش
    processing_message = await update.message.reply_text(
        f"⏳ در حال دریافت ویدیوهای آموزشی {disease_name}...\nلطفا کمی صبر کنید."
    )
    
    try:
        # دریافت فولدر نام از نقشه
        folder_name = DISEASE_FOLDERS.get(disease_name)
        
        if not folder_name:
            await update.message.reply_text(
                "❌ متأسفانه این بیماری در سیستم یافت نشد.",
                reply_markup=get_education_menu_keyboard()
            )
            return
        
        # دریافت لیست ویدیوها از Google Drive
        videos = await get_videos_from_folder(folder_name)
        
        if not videos:
            await update.message.reply_text(
                f"❌ هیچ فایل آموزشی برای {disease_name} یافت نشد.",
                reply_markup=get_education_menu_keyboard()
            )
            await processing_message.delete()
            return
        
        # حذف پیام در حال پردازش
        await processing_message.delete()
        
        # ارسال پیام توضیحات
        await update.message.reply_text(
            f"✅ {len(videos)} فایل آموزشی برای {disease_name} پیدا شد.\n"
            f"در حال ارسال..."
        )
        
        # ارسال هر ویدیو
        for idx, video in enumerate(videos, 1):
            try:
                # بررسی حجم فایل (تلگرام محدودیت 50MB داره)
                file_size_mb = int(video.get('size', 0)) / (1024 * 1024)
                
                if file_size_mb > 50:
                    # اگه فایل بزرگ‌تره از 50MB، لینک بفرست
                    await update.message.reply_text(
                        f"📹 {video['name']}\n"
                        f"📊 حجم: {file_size_mb:.1f} MB\n\n"
                        f"⚠️ این فایل بزرگ‌تر از 50MB است و نمی‌تواند مستقیماً ارسال شود.\n\n"
                        f"🔗 لینک دانلود:\n{video['web_link']}\n\n"
                        f"{idx}/{len(videos)}"
                    )
                else:
                    # تلاش برای ارسال به عنوان ویدیو
                    try:
                        await update.message.reply_video(
                            video=video['url'],
                            caption=f"📹 {video['name']}\n\n{idx}/{len(videos)}",
                            read_timeout=60,
                            write_timeout=60,
                            connect_timeout=60
                        )
                    except Exception as video_error:
                        # اگه ارسال به عنوان ویدیو نشد، لینک بفرست
                        print(f"خطا در ارسال ویدیو {video['name']}: {video_error}")
                        await update.message.reply_text(
                            f"📹 {video['name']}\n"
                            f"📊 حجم: {file_size_mb:.1f} MB\n\n"
                            f"⚠️ متأسفانه ارسال مستقیم امکان‌پذیر نبود.\n\n"
                            f"🔗 لینک دانلود:\n{video['web_link']}\n\n"
                            f"💡 روی لینک کلیک کنید تا فایل دانلود شود.\n\n"
                            f"{idx}/{len(videos)}"
                        )
                        
            except Exception as e:
                print(f"خطا در پردازش فایل {video['name']}: {e}")
                await update.message.reply_text(
                    f"❌ خطا در ارسال: {video['name']}"
                )
        
        # پیام پایانی
        await update.message.reply_text(
            f"✅ همه فایل‌های آموزشی {disease_name} ارسال شدند.\n\n"
            "آیا موضوع دیگری می‌خواهید یاد بگیرید؟",
            reply_markup=get_education_menu_keyboard()
        )
        
    except Exception as e:
        print(f"خطا در پردازش انتخاب بیماری: {e}")
        await update.message.reply_text(
            "❌ متأسفانه خطایی رخ داد. لطفا دوباره تلاش کنید.",
            reply_markup=get_education_menu_keyboard()
        )
        try:
            await processing_message.delete()
        except:
            pass
