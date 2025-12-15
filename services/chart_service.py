import matplotlib
matplotlib.use('Agg')  # برای محیط بدون GUI
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import os
import uuid

# تنظیمات فونت فارسی
plt.rcParams['font.family'] = 'DejaVu Sans'

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
        values = []
        
        for item in data:
            # ترکیب تاریخ و ساعت
            datetime_str = f"{item['date']} {item['time']}"
            dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
            dates.append(dt)
            
            # استخراج مقدار عددی
            value_str = item['value'].split()[0]  # جدا کردن عدد از واحد
            
            # برای فشار خون، میانگین سیستولیک و دیاستولیک
            if '/' in value_str:
                systolic, diastolic = map(float, value_str.split('/'))
                values.append((systolic, diastolic))
            else:
                values.append(float(value_str))
        
        # ساخت نمودار
        fig, ax = plt.subplots(figsize=(12, 6))
        
        if title == "فشار خون" and len(values) > 0 and isinstance(values[0], tuple):
            # نمودار دو خطی برای فشار خون
            systolic_values = [v[0] for v in values]
            diastolic_values = [v[1] for v in values]
            
            ax.plot(dates, systolic_values, marker='o', linestyle='-', 
                   linewidth=2, markersize=6, label='Systolic', color='#e74c3c')
            ax.plot(dates, diastolic_values, marker='s', linestyle='-', 
                   linewidth=2, markersize=6, label='Diastolic', color='#3498db')
            ax.legend(fontsize=10)
        else:
            # نمودار یک خطی
            ax.plot(dates, values, marker='o', linestyle='-', 
                   linewidth=2, markersize=8, color='#2ecc71')
        
        # تنظیمات محور X (تاریخ)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.xticks(rotation=45, ha='right')
        
        # برچسب‌ها و عنوان
        ax.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax.set_ylabel(f'{title} ({unit})', fontsize=12, fontweight='bold')
        ax.set_title(f'{title} Chart', fontsize=14, fontweight='bold', pad=20)
        
        # شبکه
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # تنظیمات layout
        plt.tight_layout()
        
        # ذخیره نمودار
        filename = f"chart_{uuid.uuid4().hex}.png"
        filepath = os.path.join('/tmp', filename)
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        return filepath
        
    except Exception as e:
        print(f"خطا در ساخت نمودار: {e}")
        raise e
