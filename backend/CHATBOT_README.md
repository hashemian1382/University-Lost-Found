# Chatbot API Documentation

## Overview
این سرویس یک chatbot هوشمند است که از ChatGPT API استفاده می‌کند تا از توضیحات کاربر به زبان طبیعی، اطلاعات ساختار‌یافته‌ای برای آیتم‌های گم‌شده یا پیدا شده استخراج کند و سپس به صورت خودکار در دیتابیس جستجو می‌کند تا آیتم‌های مشابه را پیدا کند.

## 🚀 Quick Start

### 1. نصب پکیج‌های مورد نیاز
```bash
cd backend
source .venv/bin/activate  # یا استفاده از virtual environment خودتان
pip install -r requirements.txt
```

### 2. تنظیم API Key
فایل `.env` را ویرایش کنید و API Key خود را جایگزین کنید:
```bash
OPENAI_API_KEY=sk-your-actual-api-key-here
```

برای دریافت API Key به [platform.openai.com/api-keys](https://platform.openai.com/api-keys) مراجعه کنید.

### 3. تست اتصال به OpenAI
قبل از استفاده، اتصال خود را تست کنید:
```bash
cd backend
/Users/ghost/Desktop/University-Lost-Found/.venv/bin/python core/test_openai.py
```

اگر همه چیز درست باشد، این پیام را خواهید دید:
```
✅ ALL TESTS PASSED!
Your OpenAI API is configured correctly and working!
```

### 4. اجرای سرور
```bash
cd backend
/Users/ghost/Desktop/University-Lost-Found/.venv/bin/python manage.py runserver
```

### 5. باز کردن فرانتند
فایل `frontend/chatbot.html` را در مرورگر باز کنید یا از صفحه اصلی روی دکمه "AI Assistant" کلیک کنید.

## 📡 API Endpoint

### POST `/api/chatbot/`

این endpoint توضیحات کاربر را دریافت، اطلاعات را استخراج، و آیتم‌های مشابه را جستجو می‌کند.

**Authentication:** Required (JWT Token)

**Request Body:**
```json
{
  "description": "من گوشی آیفون آبی رنگم رو دم کتابخونه گم کردم. صفحه نمایشش شکسته و پشتش یک استیکر داره",
  "search": true  // Optional: false برای غیرفعال کردن جستجو
}
```

**Response (Success - 200):**
```json
{
  "extracted_info": {
    "type": "LOST",
    "title": "iPhone 13 Pro Max - Blue",
    "description": "iPhone 13 Pro Max in blue color with a cracked screen and a sticker on the back. Lost near the library.",
    "location_description": "Near the library",
    "latitude": null,
    "longitude": null,
    "tags": ["Electronics"]
  },
  "similar_items": [
    {
      "id": 5,
      "title": "Blue iPhone with cracked screen",
      "description": "Found an iPhone near library...",
      "type": "FOUND",
      "author_name": "John Doe",
      "tags_details": [{"id": 1, "name": "Electronics"}],
      "created_at": "2026-02-15T10:30:00Z",
      "match_score": 0.85
    }
  ],
  "total_matches": 1
}
```

## 🎯 نحوه کار سیستم

### 1. استخراج اطلاعات (AI Service)
- کاربر توضیحات را به زبان طبیعی می‌نویسد
- ChatGPT اطلاعات ساختاریافته را استخراج می‌کند:
  - نوع (گم‌شده یا پیدا شده)
  - عنوان
  - توضیحات کامل
  - مکان
  - مختصات جغرافیایی (در صورت امکان)
  - تگ‌های مرتبط

### 2. جستجوی هوشمند (Search Service)
- جستجو در آیتم‌های نوع مخالف (اگر گم‌شده، در پیدا شده‌ها جستجو می‌کند)
- جستجو بر اساس:
  - کلمات کلیدی در عنوان و توضیحات
  - تگ‌های مشترک
  - نزدیکی مکانی (اگر مختصات وجود داشته باشد)

### 3. محاسبه امتیاز شباهت (Match Score)
هر آیتم بر اساس این فاکتورها امتیاز می‌گیرد:
- **تگ‌ها (40%)**: تعداد تگ‌های مشترک
- **کلمات کلیدی (40%)**: تشابه در عنوان و توضیحات
- **مکان (20%)**: نزدیکی جغرافیایی

## 🖥️ استفاده در Frontend

### HTML
صفحه `chatbot.html` یک رابط کاربری کامل دارد با:
- ✅ Textarea برای ورود توضیحات
- ✅ نمونه‌های آماده برای تست سریع
- ✅ نمایش اطلاعات استخراج شده
- ✅ لیست آیتم‌های مشابه با امتیاز Match
- ✅ لینک مستقیم به صفحه جزئیات آیتم

### JavaScript Example
```javascript
async function searchWithAI(description) {
  const response = await fetch('http://localhost:8000/api/chatbot/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ 
      description: description,
      search: true 
    })
  });
  
  const data = await response.json();
  console.log('Extracted:', data.extracted_info);
  console.log('Found items:', data.similar_items);
}
```

## 📁 ساختار فایل‌ها

```
backend/
├── core/
│   ├── ai_service.py           # سرویس اتصال به ChatGPT
│   ├── search_service.py       # سرویس جستجوی هوشمند
│   ├── serializers.py          # Serializers جدید
│   ├── views.py                # ChatBotView
│   ├── urls.py                 # Route: /api/chatbot/
│   └── test_openai.py          # اسکریپت تست اتصال
├── .env                        # تنظیمات (شامل API Key)
└── CHATBOT_README.md           # این فایل

frontend/
├── chatbot.html                # صفحه رابط کاربری
└── assets/js/
    └── chatbot.js              # لاجیک frontend
```

## 🧪 تست کردن

### 1. تست Backend
```bash
# تست اتصال OpenAI
cd backend
/Users/ghost/Desktop/University-Lost-Found/.venv/bin/python core/test_openai.py

# تست با curl
curl -X POST http://localhost:8000/api/chatbot/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"description": "من کیف مشکی رنگم رو توی کافه گم کردم"}'
```

### 2. تست Frontend
1. سرور را اجرا کنید
2. `frontend/chatbot.html` را باز کنید
3. لاگین کنید
4. یکی از نمونه‌ها را امتحان کنید یا توضیحات خود را بنویسید

### نمونه توضیحات برای تست:
```
✅ "I lost my blue iPhone 13 near the library yesterday. It has a cracked screen and a sticker on the back."

✅ "Found a brown leather bag in the gym. Contains some books and a water bottle."

✅ "من کیف قهوه‌ای رنگم رو توی سالن ورزشی پیدا کردم. توش چند تا کتاب و یک بطری آب بود"

✅ "I can't find my black wallet. Last saw it in the cafeteria this morning. It has my student ID."
```

## ⚙️ تنظیمات پیشرفته

### تغییر مدل AI
در فایل `core/ai_service.py`:
```python
response = self.client.chat.completions.create(
    model="gpt-3.5-turbo",  # یا "gpt-4" برای نتایج بهتر
    ...
)
```

### تغییر تعداد نتایج جستجو
در فایل `core/search_service.py`:
```python
def search_similar_items(extracted_data: Dict, max_results: int = 10):
    # تغییر max_results برای تعداد بیشتر یا کمتر
```

### تغییر وزن‌های Match Score
در فایل `core/search_service.py` متد `get_match_score()`:
```python
# وزن تگ‌ها
max_score += 0.4  # تغییر از 0.4 به عدد دلخواه

# وزن کلمات کلیدی  
max_score += 0.4  # تغییر از 0.4 به عدد دلخواه

# وزن مکان
max_score += 0.2  # تغییر از 0.2 به عدد دلخواه
```

## 🔒 امنیت

- ✅ API Key در فایل `.env` ذخیره می‌شود (نه در کد)
- ✅ Authentication با JWT الزامی است
- ✅ فایل `.env` در `.gitignore` قرار دارد
- ⚠️ هرگز API Key را commit نکنید

## 💰 هزینه‌ها

- هر درخواست به ChatGPT API هزینه دارد
- مدل `gpt-3.5-turbo` ارزان‌تر از `gpt-4` است
- برای کاهش هزینه:
  - از caching استفاده کنید
  - تعداد token‌ها را محدود کنید
  - از rate limiting استفاده کنید

## 🐛 رفع مشکلات

### خطا: "OPENAI_API_KEY environment variable is not set"
**راه حل:** API Key را در فایل `.env` قرار دهید

### خطا: "Session expired. Please login again"
**راه حل:** دوباره لاگین کنید - JWT token منقضی شده

### خطا: Import "openai" could not be resolved
**راه حل:** 
```bash
/Users/ghost/Desktop/University-Lost-Found/.venv/bin/python -m pip install openai
```

### نتایج جستجو خالی است
**بررسی کنید:**
- آیا آیتم‌های نوع مخالف در دیتابیس وجود دارد؟
- آیا تگ‌ها یا کلمات کلیدی مشترکی وجود دارد؟

## 📚 مستندات بیشتر

- [OpenAI API Documentation](https://platform.openai.com/docs/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [ChatGPT Best Practices](https://platform.openai.com/docs/guides/prompt-engineering)

## 🎉 ویژگی‌های پیاده‌سازی شده

✅ استخراج هوشمند اطلاعات از متن  
✅ جستجوی خودکار آیتم‌های مشابه  
✅ محاسبه امتیاز شباهت (Match Score)  
✅ فرانتند کامل و زیبا  
✅ مدیریت خطا و Loading states  
✅ نمونه‌های آماده برای تست  
✅ اسکریپت تست اتصال  
✅ مستندات کامل  

## 📞 پشتیبانی

در صورت بروز مشکل:
1. ابتدا اسکریپت تست را اجرا کنید
2. لاگ‌های سرور را بررسی کنید
3. Console مرورگر را بررسی کنید

---

**نسخه:** 1.0.0  
**آخرین بروزرسانی:** February 16, 2026


## Setup

### 1. نصب پکیج‌های مورد نیاز
```bash
cd backend
source venv/bin/activate  # یا استفاده از virtual environment خودتان
pip install -r requirements.txt
```

### 2. تنظیم API Key
فایل `.env` را ویرایش کرده و API Key خود را جایگزین کنید:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

## API Endpoint

### POST `/api/chatbot/`

این endpoint توضیحات کاربر را دریافت کرده و اطلاعات ساختار‌یافته برمی‌گرداند.

**Authentication:** Required (JWT Token)

**Request Body:**
```json
{
  "description": "من گوشی آیفون آبی رنگم رو دم کتابخونه گم کردم. صفحه نمایشش شکسته و پشتش یک استیکر داره"
}
```

**Response (Success - 200):**
```json
{
  "type": "LOST",
  "title": "iPhone 13 Pro Max - Blue",
  "description": "iPhone 13 Pro Max in blue color with a cracked screen and a sticker on the back. Lost near the library.",
  "location_description": "Near the library",
  "latitude": null,
  "longitude": null,
  "tags": ["Electronics"]
}
```

**Response (Error - 400):**
```json
{
  "description": ["This field is required."]
}
```

**Response (Error - 500):**
```json
{
  "error": "Failed to process description",
  "details": "Error message here"
}
```

## استفاده در کد

### Python Example
```python
import requests

url = "http://localhost:8000/api/chatbot/"
headers = {
    "Authorization": "Bearer YOUR_JWT_TOKEN",
    "Content-Type": "application/json"
}
data = {
    "description": "من کیف قهوه‌ای رنگم رو توی سالن ورزشی پیدا کردم"
}

response = requests.post(url, json=data, headers=headers)
result = response.json()

print(f"Type: {result['type']}")
print(f"Title: {result['title']}")
print(f"Tags: {result['tags']}")
```

### JavaScript/Frontend Example
```javascript
async function extractItemInfo(description) {
  const response = await fetch('http://localhost:8000/api/chatbot/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ description })
  });
  
  if (!response.ok) {
    throw new Error('Failed to extract item info');
  }
  
  return await response.json();
}

// استفاده
const description = "من کیف قهوه‌ای رنگم رو توی سالن ورزشی پیدا کردم";
const itemInfo = await extractItemInfo(description);
console.log(itemInfo);
```

## ساختار فایل‌ها

### 1. `core/ai_service.py`
سرویس اصلی که با ChatGPT API ارتباط برقرار می‌کند:
- `ChatBotService`: کلاس اصلی سرویس
- `extract_item_info()`: متد استخراج اطلاعات از توضیحات کاربر
- `_create_system_prompt()`: ساخت prompt برای ChatGPT
- `_validate_and_clean_result()`: اعتبارسنجی و پاکسازی نتایج

### 2. `core/serializers.py`
- `ChatBotRequestSerializer`: اعتبارسنجی ورودی
- `ChatBotResponseSerializer`: اعتبارسنجی خروجی

### 3. `core/views.py`
- `ChatBotView`: API View برای endpoint چت‌بات

### 4. `core/urls.py`
- Route: `/api/chatbot/`

## ویژگی‌های AI Service

### استخراج خودکار:
1. **نوع آیتم**: گم‌شده (LOST) یا پیدا شده (FOUND)
2. **عنوان**: یک عنوان کوتاه و توصیفی
3. **توضیحات**: توضیحات کامل شامل رنگ، برند، وضعیت و ویژگی‌های منحصر به فرد
4. **مکان**: توضیحات مکان
5. **مختصات**: latitude و longitude (در صورت امکان)
6. **تگ‌ها**: تگ‌های مرتبط از لیست تگ‌های موجود

### تگ‌های موجود:
- Electronics
- Books
- Clothing
- ID Cards
- Keys
- Wallet
- Bags
- Accessories
- Other

### ویژگی‌های هوشمند:
- ✅ استنباط نوع آیتم از روی متن (اگر صراحتاً ذکر نشده باشد)
- ✅ استخراج مختصات جغرافیایی در صورت ذکر مکان‌های خاص
- ✅ اعتبارسنجی و پاکسازی خودکار داده‌ها
- ✅ مدیریت خطاها و ارائه پیام‌های مناسب
- ✅ استفاده از JSON mode برای پاسخ‌های ساختاریافته

## نکات مهم

1. **API Key**: حتماً API Key خود را در فایل `.env` قرار دهید
2. **Authentication**: endpoint نیازمند احراز هویت با JWT است
3. **Rate Limiting**: توجه به محدودیت‌های OpenAI API داشته باشید
4. **Error Handling**: همیشه خطاها را مدیریت کنید
5. **Cost**: هر درخواست هزینه‌ای برای OpenAI API دارد

## Testing

برای تست API می‌توانید از cURL استفاده کنید:

```bash
curl -X POST http://localhost:8000/api/chatbot/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"description": "من کیف مشکی رنگم رو توی کافه گم کردم"}'
```

یا از Swagger UI در `http://localhost:8000/swagger/` استفاده کنید.

## مراحل بعدی

در مرحله بعدی می‌توان این امکانات را اضافه کرد:
1. جستجوی خودکار آیتم‌های مشابه بعد از استخراج اطلاعات
2. پیشنهاد آیتم‌های مرتبط به کاربر
3. ذخیره تاریخچه مکالمات
4. بهبود prompt برای نتایج دقیق‌تر
5. پشتیبانی از زبان‌های مختلف

## License
This project is part of the University Lost & Found system.
