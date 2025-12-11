# ChatKit Backend v2.0

Python FastAPI backend для интеграции с OpenAI ChatKit, основанный на официальном примере OpenAI.

## Изменения в v2.0

- ✅ Использует **ChatKitServer** вместо прямого `sessions.create()`
- ✅ Endpoint изменен на `/api/chatkit` (вместо `/api/chatkit/session`)
- ✅ Не требуется client_secret - обрабатывается автоматически
- ✅ Использует **OpenAI Agents SDK** для интеллектуальных ответов
- ✅ In-memory хранилище для threads и messages
- ✅ max_tokens: 1024 (по требованию)

## Быстрый старт

### 1. Установка зависимостей

```bash
cd chatkit-backend

# Создать виртуальное окружение
python -m venv venv

# Активировать
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt
```

### 2. Настройка environment

Создайте `.env` файл:

```bash
cp .env.example .env
```

Добавьте ваш OpenAI API ключ:

```env
OPENAI_API_KEY=sk-proj-...
PORT=8080
ENVIRONMENT=development
```

### 3. Запуск сервера

```bash
python main.py

# или через uvicorn
uvicorn main:app --reload --port 8080
```

Сервер будет доступен на `http://localhost:8080`

## Endpoints

### GET /
Информация о сервисе

```bash
curl http://localhost:8080/
```

### GET /health
Health check

```bash
curl http://localhost:8080/health
```

### POST /api/chatkit
Главный endpoint для ChatKit

**Примечание:** Этот endpoint обрабатывается ChatKitServer и принимает специальный формат запросов от ChatKit UI. Прямое тестирование через curl не требуется - используйте frontend.

## Архитектура

```
┌─────────────────────────┐
│  ChatKit UI (Frontend)  │
└───────────┬─────────────┘
            │
            │ POST /api/chatkit
            │
┌───────────▼─────────────┐
│  ChatKitServer          │
│  (main.py)              │
└───────────┬─────────────┘
            │
            ├─► MemoryStore (хранение threads)
            │
            ├─► ThreadItemConverter (конвертация)
            │
            └─► OpenAI Agent (генерация ответов)
```

## Компоненты

### SimpleChatKitServer
Основной класс, наследуется от `ChatKitServer`. Обрабатывает:
- Создание и управление threads
- Streaming ответов от AI
- Конвертация сообщений

### MemoryStore
In-memory хранилище для:
- Thread metadata
- Thread items (сообщения)

**Примечание:** В production рекомендуется заменить на persistent storage (PostgreSQL, Redis и т.д.)

### ThreadItemConverter
Преобразует ChatKit thread items в формат для OpenAI Agents SDK.

## Деплой в Google Cloud Run

```bash
# Авторизация
gcloud auth login

# Установить проект
gcloud config set project YOUR_PROJECT_ID

# Деплой (automatic build)
gcloud run deploy chatkit-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY="sk-proj-..." \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 10 \
  --min-instances 0

# Получить URL
gcloud run services describe chatkit-backend \
  --region us-central1 \
  --format 'value(status.url)'
```

### После деплоя

1. Скопируйте Cloud Run URL
2. Обновите CORS origins в `main.py` если нужно
3. Обновите `.env.production` на фронтенде с новым URL

## Настройка CORS

В `main.py` обновите список `allow_origins`:

```python
allow_origins=[
    "https://your-production-domain.web.app",
    "https://your-production-domain.firebaseapp.com",
    "http://localhost:5173"  # для локальной разработки
]
```

Удалите `"*"` в production!

## Мониторинг

### Логи

```bash
# Real-time логи
gcloud run services logs tail chatkit-backend --region us-central1

# Последние 100 записей
gcloud run services logs read chatkit-backend \
  --region us-central1 \
  --limit 100
```

### Метрики

В GCP Console → Cloud Run → chatkit-backend

Отслеживайте:
- Request count
- Latency
- Error rate
- Memory usage

## Troubleshooting

### Ошибка: ModuleNotFoundError

```bash
# Убедитесь что все пакеты установлены
pip install -r requirements.txt

# Проверьте версии
pip list | grep -E "chatkit|agents|openai"
```

### Ошибка: CORS

Обновите `allow_origins` в `main.py` и переделплойте.

### Ошибка: OpenAI API

Проверьте:
1. `OPENAI_API_KEY` установлен правильно
2. У ключа есть доступ к Agents API
3. Достаточно quota на OpenAI аккаунте

## Environment Variables

- `OPENAI_API_KEY` (required) - OpenAI API ключ
- `PORT` (optional) - Порт сервера, по умолчанию 8080
- `ENVIRONMENT` (optional) - development/production

## Зависимости

- **fastapi** - Web framework
- **uvicorn** - ASGI сервер
- **openai** - OpenAI SDK
- **openai-agents-python** - OpenAI Agents SDK
- **openai-chatkit-python** - ChatKit Server SDK
- **pydantic** - Data validation

## Стоимость

### Google Cloud Run
- ~$0.00002400 за секунду выполнения
- Бесплатный tier: 2M requests/month

### OpenAI API
- Модель: gpt-5-mini
- max_tokens: 1024
- Стоимость зависит от использования

## Полезные команды

```bash
# Локальный запуск
python main.py

# С автоперезагрузкой
uvicorn main:app --reload --port 8080

# Проверка синтаксиса
python -m py_compile main.py

# Форматирование кода
black main.py memory_store.py thread_item_converter.py
```

## Следующие шаги

1. ✅ Запустите backend локально
2. ✅ Протестируйте с frontend
3. ✅ Деплойте в Cloud Run
4. 🔧 Замените MemoryStore на persistent storage (опционально)
5. 🔧 Добавьте custom tools для агента (опционально)
6. 🔧 Настройте мониторинг и alerts

## Поддержка

- [OpenAI ChatKit Docs](https://platform.openai.com/docs/guides/chatkit)
- [OpenAI Agents SDK](https://github.com/openai/openai-agents-python)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
