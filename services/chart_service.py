import matplotlib
matplotlib.use('Agg')  # برای محیط بدون GUI
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import jdatetime
import os
import uuid

# تنظیمات فونت - از فونت انگلیسی استفاده می‌کنیم
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

async def generate_chart(data, title, unit):
    """
    ساخت نمودار از داده‌های علائم
    
    Args:
        data: لیست دیکشنری‌های حاوی date, time, type, value
        title: عنوان نمودار
        unit: واحد اندازه‌گیری
    
    Returns:
        مسیر فایل نمودار
    """
    try:
        # تبدیل داده‌ها
        dates = []
        shamsi_dates = []
        values = []
        
        for item in data:
            # ترکیب تاریخ و ساعت
            datetime_str = f"{item['date']} {item['time']}"
            dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
            dates.append(dt)
            
            # تبدیل به شمسی
            jd = jdatetime.datetime.fromgregorian(datetime=dt)
            shamsi_str = jd.strftime('%Y/%m/%d %H:%M')
            shamsi_dates.append(shamsi_str)
            
            # استخراج مقدار عددی
            value_str = item['value'].split()[0]  # جدا کردن عدد از واحد
            
            # برای فشار خون، میانگین سیستولیک و دیاستولیک
            if '/' in value_str:
                systolic, diastolic = map(float, value_str.split('/'))
                values.append((systolic, diastolic))
            else:
                values.append(float(value_str))
        
        # ترجمه عناوین به انگلیسی
        title_translations = {
            "قند خون": "Blood Sugar",
            "فشار خون": "Blood Pressure",
            "وزن": "Weight"
        }
        
        english_title = title_translations.get(title, title)
        
        # ساخت نمودار
        fig, ax = plt.subplots(figsize=(14, 7))
        
        if title == "فشار خون" and len(values) > 0 and isinstance(values[0], tuple):
            # نمودار دو خطی برای فشار خون
            systolic_values = [v[0] for v in values]
            diastolic_values = [v[1] for v in values]
            
            ax.plot(range(len(dates)), systolic_values, marker='o', linestyle='-', 
                   linewidth=2.5, markersize=7, label='Systolic (Upper)', color='#e74c3c')
            ax.plot(range(len(dates)), diastolic_values, marker='s', linestyle='-', 
                   linewidth=2.5, markersize=7, label='Diastolic (Lower)', color='#3498db')
            ax.legend(fontsize=11, loc='upper left')
        else:
            # نمودار یک خطی
            ax.plot(range(len(dates)), values, marker='o', linestyle='-', 
                   linewidth=2.5, markersize=8, color='#2ecc71', label=english_title)
        
        # تنظیمات محور X (تاریخ شمسی)
        ax.set_xticks(range(len(shamsi_dates)))
        ax.set_xticklabels(shamsi_dates, rotation=45, ha='right', fontsize=9)
        
        # برچسب‌ها و عنوان
        ax.set_xlabel('Date (Shamsi)', fontsize=12, fontweight='bold')
        ax.set_ylabel(f'{english_title} ({unit})', fontsize=12, fontweight='bold')
        ax.set_title(f'{english_title} History Chart', fontsize=15, fontweight='bold', pad=20)
        
        # شبکه
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)
        
        # تنظیمات layout
        plt.tight_layout()
        
        # ذخیره نمودار
        filename = f"chart_{uuid.uuid4().hex}.png"
        filepath = os.path.join('/tmp', filename)
        plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return filepath
        
    except Exception as e:
        print(f"خطا در ساخت نمودار: {e}")
        raise e
