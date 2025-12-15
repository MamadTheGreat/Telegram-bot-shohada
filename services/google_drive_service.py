from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from config import GOOGLE_CREDENTIALS_FILE, MAIN_FOLDER_ID
import io
import os

# Scopes مورد نیاز برای دسترسی به Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def get_drive_service():
    """ایجاد سرویس Google Drive"""
    credentials = Credentials.from_service_account_file(
        GOOGLE_CREDENTIALS_FILE,
        scopes=SCOPES
    )
    service = build('drive', 'v3', credentials=credentials)
    return service

def find_folder_by_name(folder_name, parent_id=None):
    """
    پیدا کردن فولدر بر اساس نام
    
    Args:
        folder_name: نام فولدر
        parent_id: ID فولدر والد (اختیاری)
    
    Returns:
        ID فولدر یا None
    """
    try:
        service = get_drive_service()
        
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        
        if parent_id:
            query += f" and '{parent_id}' in parents"
        
        results = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        
        items = results.get('files', [])
        
        if items:
            return items[0]['id']
        return None
        
    except Exception as e:
        print(f"خطا در پیدا کردن فولدر: {e}")
        return None

async def get_videos_from_folder(folder_name):
    """
    دریافت لیست ویدیوها از یک فولدر در Google Drive
    
    Args:
        folder_name: نام فولدر بیماری
    
    Returns:
        لیستی از دیکشنری‌های حاوی اطلاعات ویدیو
    """
    try:
        service = get_drive_service()
        
        # پیدا کردن ID فولدر
        folder_id = find_folder_by_name(folder_name, MAIN_FOLDER_ID)
        
        if not folder_id:
            print(f"فولدر {folder_name} پیدا نشد")
            return []
        
        # جستجوی فایل‌های ویدیویی در فولدر
        query = (
            f"'{folder_id}' in parents and "
            f"(mimeType contains 'video/' or "
            f"name contains '.mp4' or name contains '.avi' or "
            f"name contains '.mov' or name contains '.mkv') and "
            f"trashed=false"
        )
        
        results = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name, mimeType, size, webContentLink)',
            orderBy='name'
        ).execute()
        
        items = results.get('files', [])
        
        videos = []
        for item in items:
            file_id = item['id']
            
            videos.append({
                'id': file_id,
                'name': item['name'],
                'mime_type': item.get('mimeType', 'video/mp4'),
                'size': int(item.get('size', 0))
            })
        
        return videos
        
    except Exception as e:
        print(f"خطا در دریافت ویدیوها: {e}")
        return []

def make_file_public(file_id):
    """
    عمومی کردن یک فایل در Google Drive
    این تابع را برای هر ویدیو قبل از ارسال اجرا کنید
    
    Args:
        file_id: ID فایل در Google Drive
    """
    try:
        service = get_drive_service()
        
        permission = {
            'type': 'anyone',
            'role': 'reader'
        }
        
        service.permissions().create(
            fileId=file_id,
            body=permission
        ).execute()
        
        return True
        
    except Exception as e:
        print(f"خطا در عمومی کردن فایل: {e}")
        return False

async def download_file_from_drive(file_id, file_name):
    """
    دانلود فایل از Google Drive
    
    Args:
        file_id: ID فایل در Google Drive
        file_name: نام فایل
    
    Returns:
        مسیر فایل دانلود شده
    """
    try:
        service = get_drive_service()
        
        # دانلود فایل
        request = service.files().get_media(fileId=file_id)
        
        # ذخیره در /tmp
        file_path = os.path.join('/tmp', file_name)
        
        with io.FileIO(file_path, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    print(f"دانلود {int(status.progress() * 100)}% انجام شد.")
        
        return file_path
        
    except Exception as e:
        print(f"خطا در دانلود فایل: {e}")
        return None
