from telegram import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu_keyboard():
    """کیبورد منوی اصلی"""
    keyboard = [
        [KeyboardButton("آموزش")],
        [KeyboardButton("ثبت علائم")],
        [KeyboardButton("ارتباط با کارشناس")]
    ]
    return ReplyKeyboardMarkup(
        keyboard, 
        resize_keyboard=True,
        one_time_keyboard=False
    )

def get_education_menu_keyboard():
    """کیبورد منوی آموزش"""
    keyboard = [
        [KeyboardButton("دیابت نوع ۲")],
        [KeyboardButton("فشار خون")],
        [KeyboardButton("بیماری قلبی عروقی")],
        [KeyboardButton("🔙 بازگشت")]
    ]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )

def get_back_keyboard():
    """کیبورد بازگشت به منوی اصلی"""
    keyboard = [
        [KeyboardButton("بازگشت به منوی اصلی")]
    ]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )
