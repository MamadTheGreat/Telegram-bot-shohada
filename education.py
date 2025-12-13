from telegram import Update
from telegram.ext import ContextTypes
from menus import education_menu

async def education_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        text="لطفاً بیماری مورد نظر را انتخاب کنید:",
        reply_markup=education_menu()
    )

async def diabetes_education(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        text=(
            "📘 آموزش دیابت\n\n"
            "دیابت بیماری مزمن متابولیک است که با افزایش قند خون مشخص می‌شود.\n\n"
            "▪️ کنترل رژیم غذایی\n"
            "▪️ فعالیت بدنی منظم\n"
            "▪️ پایش قند خون\n"
        )
    )
