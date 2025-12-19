import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_SYSTEM_PROMPT

# بررسی و تنظیم API Key
if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
    print("❌ خطا: GEMINI_API_KEY تنظیم نشده است!")
else:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        print(f"✅ Gemini API configured")
    except Exception as e:
        print(f"❌ خطا در تنظیم Gemini: {e}")

# تنظیمات ساده
generation_config = {
    "temperature": 0.7,
    "max_output_tokens": 2048,
}

async def ask_gemini(question: str, conversation_history: list = None) -> str:
    """
    ارسال سوال به Gemini و دریافت پاسخ
    """
    try:
        print(f"[GEMINI] Question: {question[:30]}...")
        
        # سوال کامل با system prompt
        full_question = f"""{GEMINI_SYSTEM_PROMPT}

سوال کاربر: {question}

لطفاً به فارسی پاسخ دهید."""
        
        # لیست مدل‌های قابل استفاده (به ترتیب اولویت)
        models_to_try = [
            "gemini-pro",
            "models/gemini-pro",
            "gemini-1.0-pro-latest",
            "gemini-1.0-pro"
        ]
        
        response = None
        used_model = None
        
        # امتحان هر مدل
        for model_name in models_to_try:
            try:
                print(f"[GEMINI] Trying model: {model_name}")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(
                    full_question,
                    generation_config=generation_config
                )
                used_model = model_name
                print(f"[GEMINI] ✅ Success with: {model_name}")
                break
            except Exception as e:
                print(f"[GEMINI] ❌ Failed with {model_name}: {str(e)[:50]}")
                continue
        
        # اگه هیچ مدلی کار نکرد
        if not response:
            raise Exception("هیچ مدلی در دسترس نیست")
        
        # استخراج پاسخ
        answer = response.text
        
        # اضافه کردن هشدار
        if "جایگزین مشاوره پزشک" not in answer:
            answer += "\n\n⚠️ این راهنمایی کلی است و جایگزین مشاوره پزشک نمی‌شود. لطفاً با پزشک معالج خود مشورت کنید."
        
        print(f"[GEMINI] Answer length: {len(answer)}")
        return answer
        
    except Exception as e:
        print(f"[GEMINI ERROR] {type(e).__name__}: {str(e)}")
        
        # پیام خطای کاربرپسند
        return (
            "❌ متأسفانه در حال حاضر امکان پاسخگویی وجود ندارد.\n\n"
            "لطفاً با شماره تماس 021-12345678 تماس بگیرید.\n\n"
            "⚠️ در مواقع اورژانسی با 115 تماس بگیرید."
        )

async def ask_gemini_with_context(question: str, disease_context: str = None) -> str:
    """
    ارسال سوال با context مشخص
    """
    if disease_context:
        full_question = f"زمینه: {disease_context}\n\nسوال: {question}"
    else:
        full_question = question
    
    return await ask_gemini(full_question)
