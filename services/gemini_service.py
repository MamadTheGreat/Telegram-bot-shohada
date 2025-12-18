import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_SYSTEM_PROMPT

# تنظیم API Key
genai.configure(api_key=GEMINI_API_KEY)

# تنظیمات مدل
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 2048,
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
]

async def ask_gemini(question: str, conversation_history: list = None) -> str:
    """
    ارسال سوال به Gemini و دریافت پاسخ
    
    Args:
        question: سوال کاربر
        conversation_history: تاریخچه گفتگو (اختیاری)
    
    Returns:
        پاسخ Gemini
    """
    try:
        # ساخت مدل
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",  # مدل رایگان
            generation_config=generation_config,
            safety_settings=safety_settings,
            system_instruction=GEMINI_SYSTEM_PROMPT
        )
        
        # شروع چت
        if conversation_history:
            chat = model.start_chat(history=conversation_history)
        else:
            chat = model.start_chat(history=[])
        
        # ارسال پیام
        response = chat.send_message(question)
        
        # استخراج متن پاسخ
        answer = response.text
        
        # اضافه کردن هشدار در صورتی که در پاسخ نباشد
        if "جایگزین مشاوره پزشک" not in answer and "جایگزین ویزیت" not in answer:
            answer += "\n\n⚠️ این راهنمایی کلی است و جایگزین مشاوره پزشک نمی‌شود. لطفاً با پزشک معالج خود مشورت کنید."
        
        return answer
        
    except Exception as e:
        print(f"خطا در ارتباط با Gemini: {e}")
        return (
            "❌ متأسفانه در حال حاضر امکان پاسخگویی وجود ندارد.\n\n"
            "لطفاً:\n"
            "• چند لحظه دیگر تلاش کنید\n"
            "• یا با شماره تماس 021-12345678 تماس بگیرید\n\n"
            "⚠️ در مواقع اورژانسی با 115 تماس بگیرید."
        )

async def ask_gemini_with_context(question: str, disease_context: str = None) -> str:
    """
    ارسال سوال با context مشخص (مثلاً نوع بیماری)
    
    Args:
        question: سوال کاربر
        disease_context: زمینه بیماری (دیابت، فشار خون، قلبی)
    
    Returns:
        پاسخ Gemini
    """
    if disease_context:
        full_question = f"زمینه: {disease_context}\n\nسوال: {question}"
    else:
        full_question = question
    
    return await ask_gemini(full_question)
