from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime
from config import GOOGLE_CREDENTIALS_FILE, GOOGLE_SHEET_ID, USER_DATA_SHEET, SYMPTOMS_SHEET

# Scopes مورد نیاز برای دسترسی به Google Sheets
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_sheets_service():
    """ایجاد سرویس Google Sheets"""
    credentials = Credentials.from_service_account_file(
        GOOGLE_CREDENTIALS_FILE,
        scopes=SCOPES
    )
    service = build('sheets', 'v4', credentials=credentials)
    return service

async def log_user_start(user_id, username, full_name):
    """
    ثبت اطلاعات کاربر هنگام شروع به کار با ربات
    
    Args:
        user_id: شناسه کاربر در تلگرام
        username: نام کاربری
        full_name: نام کامل کاربر
    """
    try:
        service = get_sheets_service()
        sheet = service.spreadsheets()
        
        # بررسی وجود هدرها
        result = sheet.values().get(
            spreadsheetId=GOOGLE_SHEET_ID,
            range=f'{USER_DATA_SHEET}!A1:E1'
        ).execute()
        
        values = result.get('values', [])
        
        # اگر هدر وجود نداشت، اضافه کنیم
        if not values:
            header = [['User ID', 'Username', 'Full Name', 'First Interaction', 'Last Interaction']]
            sheet.values().update(
                spreadsheetId=GOOGLE_SHEET_ID,
                range=f'{USER_DATA_SHEET}!A1:E1',
                valueInputOption='RAW',
                body={'values': header}
            ).execute()
        
        # بررسی اینکه آیا کاربر قبلا ثبت شده
        result = sheet.values().get(
            spreadsheetId=GOOGLE_SHEET_ID,
            range=f'{USER_DATA_SHEET}!A:A'
        ).execute()
        
        existing_users = result.get('values', [])
        user_exists = False
        row_number = 0
        
        for idx, row in enumerate(existing_users[1:], start=2):  # شروع از ردیف 2 (بعد از هدر)
            if row and str(row[0]) == str(user_id):
                user_exists = True
                row_number = idx
                break
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if user_exists:
            # به‌روزرسانی Last Interaction
            sheet.values().update(
                spreadsheetId=GOOGLE_SHEET_ID,
                range=f'{USER_DATA_SHEET}!E{row_number}',
                valueInputOption='RAW',
                body={'values': [[current_time]]}
            ).execute()
        else:
            # افزودن کاربر جدید
            new_row = [[user_id, username, full_name, current_time, current_time]]
            sheet.values().append(
                spreadsheetId=GOOGLE_SHEET_ID,
                range=f'{USER_DATA_SHEET}!A:E',
                valueInputOption='RAW',
                body={'values': new_row}
            ).execute()
        
        return True
        
    except Exception as e:
        print(f"خطا در ثبت اطلاعات کاربر: {e}")
        return False

async def log_symptom(user_id, username, symptom_data):
    """
    ثبت علائم کاربر در گوگل شیت
    این تابع در مرحله بعدی استفاده خواهد شد
    
    Args:
        user_id: شناسه کاربر
        username: نام کاربری
        symptom_data: دیکشنری حاوی اطلاعات علائم
    """
    try:
        service = get_sheets_service()
        sheet = service.spreadsheets()
        
        # بررسی وجود هدرها در شیت علائم
        result = sheet.values().get(
            spreadsheetId=GOOGLE_SHEET_ID,
            range=f'{SYMPTOMS_SHEET}!A1:F1'
        ).execute()
        
        values = result.get('values', [])
        
        # اگر هدر وجود نداشت، اضافه کنیم
        if not values:
            header = [['User ID', 'Username', 'Date', 'Time', 'Symptom Type', 'Details']]
            sheet.values().update(
                spreadsheetId=GOOGLE_SHEET_ID,
                range=f'{SYMPTOMS_SHEET}!A1:F1',
                valueInputOption='RAW',
                body={'values': header}
            ).execute()
        
        # افزودن علائم جدید
        current_date = datetime.now().strftime('%Y-%m-%d')
        current_time = datetime.now().strftime('%H:%M:%S')
        
        new_row = [[
            user_id,
            username,
            current_date,
            current_time,
            symptom_data.get('type', ''),
            symptom_data.get('details', '')
        ]]
        
        sheet.values().append(
            spreadsheetId=GOOGLE_SHEET_ID,
            range=f'{SYMPTOMS_SHEET}!A:F',
            valueInputOption='RAW',
            body={'values': new_row}
        ).execute()
        
        return True
        
    except Exception as e:
        print(f"خطا در ثبت علائم: {e}")
        return False
