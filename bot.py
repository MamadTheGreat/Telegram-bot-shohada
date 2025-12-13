from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import TELEGRAM_BOT_TOKEN, WEBHOOK_URL, PORT
from menus import main_menu
from education import education_entry, diabetes_education
from symptoms import symptoms_entry, symptoms_input

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "به ربات شهداء خوش آمدید 🌱",
        reply_markup=main_menu()
    )

async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        text="منوی اصلی:",
        reply_markup=main_menu()
    )

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(CallbackQueryHandler(education_entry, pattern="^education$"))
    app.add_handler(CallbackQueryHandler(diabetes_education, pattern="^edu_diabetes$"))

    app.add_handler(CallbackQueryHandler(symptoms_entry, pattern="^symptoms$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, symptoms_input))

    app.add_handler(CallbackQueryHandler(main_menu_handler, pattern="^back_main$"))

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL
    )

if __name__ == "__main__":
    main()
