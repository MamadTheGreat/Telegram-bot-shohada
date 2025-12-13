from telegram import Update
from telegram.ext import ContextTypes

user_symptoms = {}

async def symptoms_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_symptoms[query.from_user.id] = {}

    await query.edit_message_text(
        text="🩺 لطفاً عدد فشار سیستولیک (عدد بالا) را وارد کنید:"
    )
    context.user_data["step"] = "systolic"

async def symptoms_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    step = context.user_data.get("step")

    try:
        value = int(update.message.text)
    except ValueError:
        await update.message.reply_text("❌ لطفاً فقط عدد وارد کنید")
        return

    if step == "systolic":
        user_symptoms[user_id]["systolic"] = value
        context.user_data["step"] = "diastolic"
        await update.message.reply_text(
            "عدد فشار دیاستولیک (عدد پایین) را وارد کنید:"
        )

    elif step == "diastolic":
        user_symptoms[user_id]["diastolic"] = value
        context.user_data.pop("step")

        s = user_symptoms[user_id]["systolic"]
        d = user_symptoms[user_id]["diastolic"]

        await update.message.reply_text(
            f"✅ فشار ثبت شد:\n\n"
            f"سیستول: {s}\n"
            f"دیاستول: {d}"
        )
