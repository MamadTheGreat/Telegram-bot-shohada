from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu():
    keyboard = [
        [InlineKeyboardButton("📚 آموزش بیماری", callback_data="education")],
        [InlineKeyboardButton("🩺 ثبت علائم", callback_data="symptoms")],
        [InlineKeyboardButton("❓ سوالات رایج", callback_data="faq")],
    ]
    return InlineKeyboardMarkup(keyboard)

def education_menu():
    keyboard = [
        [InlineKeyboardButton("دیابت", callback_data="edu_diabetes")],
        [InlineKeyboardButton("بازگشت ⬅️", callback_data="back_main")],
    ]
    return InlineKeyboardMarkup(keyboard)
