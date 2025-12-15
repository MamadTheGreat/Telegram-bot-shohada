import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime

# تنظیم credentials از environment variable
if os.getenv("GOOGLE_CREDENTIALS_JSON"):
    with open("credentials.json", "w") as f:
        f.write(os.getenv("GOOGLE_CREDENTIALS_JSON"))

GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

print("=" * 50)
print("🔍 تست نوشتن در Google Sheets")
print("=" * 50)

try:
    # ساخت سرویس
    credentials = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()
    
    print(f"\n✅ اتصال به Google Sheets موفق بود")
    print(f"📊 GOOGLE_SHEET_ID: {GOOGLE_SHEET_ID}")
    
    # لیست تب‌ها
    print(f"\n📋 تب‌های موجود:")
    sheet_metadata = sheet.get(spreadsheetId=GOOGLE_SHEET_ID).execute()
    sheets = sheet_metadata.get('sheets', [])
    
    for s in sheets:
        print(f"  ✅ {s['properties']['title']}")
    
    # تست ساخت تب جدید
    test_user_id = 999999
    user_sheet_name = f"User_{test_user_id}"
    
    print(f"\n🔧 تست ساخت تب: {user_sheet_name}")
    
    sheet_exists = any(s['properties']['title'] == user_sheet_name for s in sheets)
    
    if not sheet_exists:
        requests = [{
            'addSheet': {
                'properties': {
                    'title': user_sheet_name
                }
            }
        }]
        result = sheet.batchUpdate(
            spreadsheetId=GOOGLE_SHEET_ID,
            body={'requests': requests}
        ).execute()
        print(f"  ✅ تب جدید ساخته شد")
        
        # اضافه کردن هدر
        header = [['تاریخ', 'ساعت', 'نوع علامت', 'مقدار']]
        sheet.values().update(
            spreadsheetId=GOOGLE_SHEET_ID,
            range=f'{user_sheet_name}!A1:D1',
            valueInputOption='RAW',
            body={'values': header}
        ).execute()
        print(f"  ✅ هدر اضافه شد")
    else:
        print(f"  ℹ️  تب از قبل وجود دارد")
    
    # تست نوشتن یک رکورد
    print(f"\n📝 تست نوشتن رکورد...")
    current_date = datetime.now().strftime('%Y-%m-%d')
    current_time = datetime.now().strftime('%H:%M:%S')
    
    new_row = [[current_date, current_time, "تست", "123 mg/dL"]]
    
    result = sheet.values().append(
        spreadsheetId=GOOGLE_SHEET_ID,
        range=f'{user_sheet_name}!A:D',
        valueInputOption='RAW',
        body={'values': new_row}
    ).execute()
    
    print(f"  ✅ رکورد با موفقیت نوشته شد!")
    print(f"  📊 تعداد سطرهای به‌روز شده: {result.get('updates', {}).get('updatedRows', 0)}")
    
    # خواندن رکورد
    print(f"\n📖 تست خواندن داده‌ها...")
    result = sheet.values().get(
        spreadsheetId=GOOGLE_SHEET_ID,
        range=f'{user_sheet_name}!A2:D'
    ).execute()
    
    rows = result.get('values', [])
    print(f"  ✅ تعداد رکوردها: {len(rows)}")
    
    if rows:
        print(f"  📄 آخرین رکورد: {rows[-1]}")
    
    print("\n" + "=" * 50)
    print("✅ همه تست‌ها موفقیت‌آمیز بود!")
    print("=" * 50)

except FileNotFoundError:
    print("❌ فایل credentials.json پیدا نشد!")
    
except Exception as e:
    print(f"❌ خطا: {e}")
    print(f"💡 نوع خطا: {type(e).__name__}")
    import traceback
    traceback.print_exc()

print("\n")
