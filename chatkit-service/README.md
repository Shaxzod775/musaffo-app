# Air Quality Eco Fund - Backend API

FastAPI backend с интеграцией IQAir API и ChatKit для стриминга с OpenAI.

## Возможности

- 🌍 Получение данных о качестве воздуха из IQAir API
- 💬 ChatKit интеграция с OpenAI streaming
- 🔄 CORS поддержка для frontend
- 📊 Автоматическая инъекция данных о качестве воздуха в контекст AI

## Установка

### 1. Создайте виртуальное окружение

```bash
cd backend
python -m venv venv

# Активация (Windows)
venv\Scripts\activate

# Активация (macOS/Linux)
source venv/bin/activate
```

### 2. Установите зависимости

```bash
pip install -r requirements.txt
```

### 3. Настройте переменные окружения

Отредактируйте файл `.env`:

```env
# IQAir API Configuration
IQAIR_API_KEY=9dab5d99-05fc-4359-bdaf-498590da28b4

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Server Configuration
PORT=8000
HOST=0.0.0.0

# CORS Origins
CORS_ORIGINS=http://localhost:3000,https://air-quality-eco-fund-2.vercel.app
```

## Запуск

### Development mode

```bash
python main.py
```

Или с uvicorn напрямую:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### 1. Health Check

```
GET /
```

**Response:**
```json
{
  "status": "ok",
  "message": "Air Quality Eco Fund API is running",
  "version": "1.0.0"
}
```

### 2. Get Air Quality Data

```
GET /api/air-quality?city=Tashkent&country=Uzbekistan
```

**Parameters:**
- `city` (optional): Название города (по умолчанию: Tashkent)
- `country` (optional): Название страны (по умолчанию: Uzbekistan)

**Response:**
```json
{
  "status": "success",
  "data": {
    "city": "Tashkent",
    "country": "Uzbekistan",
    "current": {
      "pollution": {
        "aqius": 85,
        "mainus": "p2"
      },
      "weather": {
        "tp": 25,
        "hu": 45,
        "ws": 3.5
      }
    }
  }
}
```

### 3. ChatKit Endpoint (Streaming)

```
POST /api/chatkit
```

**Request Body:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Какое качество воздуха в Ташкенте?"
    }
  ],
  "stream": true,
  "model": "gpt-4o",
  "temperature": 0.7,
  "max_tokens": 2000
}
```

**Response:** Server-Sent Events (SSE) stream

```
data: {"type": "content", "content": "Сейчас"}

data: {"type": "content", "content": " в Ташкенте"}

data: {"type": "done"}
```

### 4. Upload URL

```
POST /api/upload-url
```

**Request Body:**
```json
{
  "filename": "image.png",
  "content_type": "image/png"
}
```

**Response:**
```json
{
  "upload_url": "https://your-storage.com/upload/image.png",
  "file_url": "https://your-storage.com/files/image.png"
}
```

## Особенности ChatKit интеграции

### Автоматическая инъекция данных о качестве воздуха

Backend автоматически определяет, когда пользователь спрашивает о качестве воздуха, и добавляет актуальные данные из IQAir API в контекст AI.

**Ключевые слова для триггера:**
- воздух, качество, aqi, загрязнение, экология

**Поддерживаемые города:**
- Ташкент (Tashkent) - Узбекистан
- Москва (Moscow) - Россия
- Алматы (Almaty) - Казахстан

### Стриминг

Все ответы от AI отправляются в режиме реального времени через Server-Sent Events (SSE), что позволяет пользователю видеть генерацию ответа по мере её происхождения.

## Деплой

### Vercel/Railway/Render

1. Добавьте переменные окружения в настройках проекта
2. Установите build command: `pip install -r requirements.txt`
3. Установите start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t air-quality-backend .
docker run -p 8000:8000 --env-file .env air-quality-backend
```

## Лицензия

MIT
