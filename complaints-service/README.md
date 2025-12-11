# Complaints AI Service

Backend сервис для анализа экологических жалоб с помощью Claude Haiku AI.

## Функции

- Анализ фотографий нарушений с помощью Claude Haiku
- Определение типа нарушения и потенциального штрафа
- Расчёт вознаграждения заявителю (15%)
- Сохранение результатов в Firebase

## Запуск

```bash
# Установка зависимостей
pip install -r requirements.txt

# Настройка переменных окружения
cp .env.example .env
# Заполните AWS и Firebase credentials

# Запуск
python main.py
```

## API Endpoints

- `POST /analyze-complaint` - Анализ жалобы с фото
- `GET /complaints/{id}` - Получить результат анализа
- `GET /health` - Health check

## Переменные окружения

- `AWS_ACCESS_KEY_ID` - AWS Access Key
- `AWS_SECRET_ACCESS_KEY` - AWS Secret Key  
- `AWS_REGION` - AWS Region (default: us-east-1)
- `FIREBASE_CREDENTIALS` - Path to Firebase service account JSON
