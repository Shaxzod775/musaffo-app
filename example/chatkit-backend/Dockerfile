FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY main.py memory_store.py thread_item_converter.py weather_widget.py aqi_widget.py attachment_store.py firebase_service.py claude_document_agent.py ./

# Копируем credentials для Firebase
COPY credentials.json ./

# Cloud Run использует переменную окружения PORT
ENV PORT=8080

# Установка BASE_URL для production (будет переопределено через Cloud Run env vars)
ENV BASE_URL=https://chatkit-backend-266356020989.us-central1.run.app

# Команда запуска приложения
CMD exec uvicorn main:app --host 0.0.0.0 --port $PORT
