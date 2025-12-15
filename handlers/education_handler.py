from telegram import Update
from telegram.ext import ContextTypes
from keyboards import get_education_menu_keyboard, get_back_keyboard
from services.google_drive_service import get_videos_from_folder, download_file_from_drive
from config import DISEASE_FOLDERS
import os

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
                file_size_mb = video.get('size', 0) / (1024 * 1024)
                
                if file_size_mb > 50:
                    # اگه فایل بزرگ‌تره از 50MB، لینک بفرست
                    web_link = f"https://drive.google.com/file/d/{video['id']}/view"
                    await update.message.reply_text(
                        f"📹 {video['name']}\n"
                        f"📊 حجم: {file_size_mb:.1f} MB\n\n"
                        f"⚠️ این فایل بزرگ‌تر از 50MB است و نمی‌تواند مستقیماً ارسال شود.\n\n"
                        f"🔗 لینک دانلود:\n{web_link}\n\n"
                        f"{idx}/{len(videos)}"
                    )
                else:
                    # دانلود فایل از Google Drive
                    await update.message.reply_text(
                        f"⏳ در حال دانلود {video['name']}..."
                    )
                    
                    file_path = await download_file_from_drive(video['id'], video['name'])
                    
                    if file_path and os.path.exists(file_path):
                        # ارسال فایل
                        with open(file_path, 'rb') as video_file:
                            await update.message.reply_video(
                                video=video_file,
                                caption=f"📹 {video['name']}\n\n{idx}/{len(videos)}",
                                read_timeout=120,
                                write_timeout=120,
                                connect_timeout=60,
                                supports_streaming=True
                            )
                        
                        # حذف فایل موقت
                        os.remove(file_path)
                    else:
                        # اگه دانلود نشد، لینک بفرست
                        web_link = f"https://drive.google.com/file/d/{video['id']}/view"
                        await update.message.reply_text(
                            f"📹 {video['name']}\n\n"
                            f"⚠️ متأسفانه دانلود امکان‌پذیر نبود.\n\n"
                            f"🔗 لینک مشاهده:\n{web_link}\n\n"
                            f"{idx}/{len(videos)}"
                        )
                        
            except Exception as e:
                print(f"خطا در پردازش فایل {video['name']}: {e}")
                web_link = f"https://drive.google.com/file/d/{video['id']}/view"
                await update.message.reply_text(
                    f"❌ خطا در ارسال: {video['name']}\n\n"
                    f"🔗 لینک مشاهده:\n{web_link}"
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
