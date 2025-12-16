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
        types = []  # برای قند خون: ناشتا یا بعد از غذا
        
        for item in data:
            # نوع علامت (برای قند خون)
            types.append(item.get('type', ''))
            
            # تاریخ و ساعت
            date_str = item['date']
            time_str = item['time']
            
            # تبدیل تاریخ شمسی به datetime برای نمودار
            try:
                # تاریخ به فرمت YYYY-MM-DD شمسی هست
                date_parts = date_str.split('-')
                year, month, day = map(int, date_parts)
                
                # ساخت datetime شمسی
                jd = jdatetime.datetime(year, month, day)
                time_parts = time_str.split(':')
                jd = jd.replace(hour=int(time_parts[0]), minute=int(time_parts[1]), second=int(time_parts[2]))
                
                # تبدیل به میلادی برای محاسبات
                dt = jd.togregorian()
                
                # فرمت نمایش شمسی
                shamsi_str = f"{year}/{month:02d}/{day:02d} {time_parts[0]}:{time_parts[1]}"
                
            except Exception as e:
                print(f"خطا در تبدیل تاریخ: {e}")
                # اگه مشکلی بود، از روش قدیمی استفاده کن
                dt = datetime.now()
                shamsi_str = "---"
            
            dates.append(dt)
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
        fig, ax = plt.subplots(figsize=(14, 8))
        
        if title == "فشار خون" and len(values) > 0 and isinstance(values[0], tuple):
            # نمودار دو خطی برای فشار خون
            systolic_values = [v[0] for v in values]
            diastolic_values = [v[1] for v in values]
            
            # رسم خطوط
            line1 = ax.plot(range(len(dates)), systolic_values, marker='o', linestyle='-', 
                   linewidth=2.5, markersize=8, label='Systolic (Upper)', color='#e74c3c')
            line2 = ax.plot(range(len(dates)), diastolic_values, marker='s', linestyle='-', 
                   linewidth=2.5, markersize=8, label='Diastolic (Lower)', color='#3498db')
            
            # نمایش مقادیر روی نقاط - سیستولیک
            for i, (x, y) in enumerate(zip(range(len(dates)), systolic_values)):
                ax.annotate(f'{int(y)}', 
                           xy=(x, y), 
                           xytext=(0, 10),
                           textcoords='offset points',
                           ha='center',
                           fontsize=9,
                           fontweight='bold',
                           color='#c0392b',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#e74c3c', alpha=0.8))
            
            # نمایش مقادیر روی نقاط - دیاستولیک
            for i, (x, y) in enumerate(zip(range(len(dates)), diastolic_values)):
                ax.annotate(f'{int(y)}', 
                           xy=(x, y), 
                           xytext=(0, -15),
                           textcoords='offset points',
                           ha='center',
                           fontsize=9,
                           fontweight='bold',
                           color='#2874a6',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#3498db', alpha=0.8))
            
            ax.legend(fontsize=11, loc='upper left')
            
        elif title == "قند خون":
            # نمودار قند خون با تفکیک ناشتا و بعد از غذا
            fasting_indices = []
            fasting_values = []
            after_meal_indices = []
            after_meal_values = []
            
            for i, (val, typ) in enumerate(zip(values, types)):
                if 'ناشتا' in typ:
                    fasting_indices.append(i)
                    fasting_values.append(val)
                else:
                    after_meal_indices.append(i)
                    after_meal_values.append(val)
            
            # رسم نقاط ناشتا
            if fasting_indices:
                ax.plot(fasting_indices, fasting_values, marker='o', linestyle='-', 
                       linewidth=2.5, markersize=8, label='Fasting', color='#3498db')
                
                # نمایش مقادیر
                for x, y in zip(fasting_indices, fasting_values):
                    ax.annotate(f'{int(y)}', 
                               xy=(x, y), 
                               xytext=(0, 10),
                               textcoords='offset points',
                               ha='center',
                               fontsize=9,
                               fontweight='bold',
                               color='#2874a6',
                               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#3498db', alpha=0.8))
            
            # رسم نقاط بعد از غذا
            if after_meal_indices:
                ax.plot(after_meal_indices, after_meal_values, marker='s', linestyle='-', 
                       linewidth=2.5, markersize=8, label='After Meal', color='#e74c3c')
                
                # نمایش مقادیر
                for x, y in zip(after_meal_indices, after_meal_values):
                    ax.annotate(f'{int(y)}', 
                               xy=(x, y), 
                               xytext=(0, 10),
                               textcoords='offset points',
                               ha='center',
                               fontsize=9,
                               fontweight='bold',
                               color='#c0392b',
                               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#e74c3c', alpha=0.8))
            
            ax.legend(fontsize=11, loc='upper left')
            
        else:
            # نمودار یک خطی (وزن)
            ax.plot(range(len(dates)), values, marker='o', linestyle='-', 
                   linewidth=2.5, markersize=8, color='#2ecc71', label=english_title)
            
            # نمایش مقادیر روی نقاط
            for i, (x, y) in enumerate(zip(range(len(dates)), values)):
                ax.annotate(f'{y:.1f}', 
                           xy=(x, y), 
                           xytext=(0, 10),
                           textcoords='offset points',
                           ha='center',
                           fontsize=9,
                           fontweight='bold',
                           color='#27ae60',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#2ecc71', alpha=0.8))
        
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
