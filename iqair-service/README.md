# IQAir Service

Микросервис для получения данных о качестве воздуха из IQAir API.

## Особенности
- Кеширование данных (10 минут)
- Health risks на основе AQI
- Переводы на 3 языка (ru/uz/en)

## Запуск

```bash
# Установка зависимостей
pip install -r requirements.txt

# Создать .env файл
cp .env.example .env
# Добавить IQAIR_API_KEY

# Запуск
python main.py
```

По умолчанию запускается на порту **8002**.

## API Endpoints

### GET /api/air-quality
Параметры:
- `city` (default: "Tashkent")
- `country` (default: "Uzbekistan")

Response:
```json
{
  "status": "success",
  "source": "cache|api",
  "data": { ... },
  "healthRisks": {
    "level": "unhealthy",
    "warning_ru": "...",
    "warning_uz": "...",
    "warning_en": "...",
    "affected_groups": [...],
    "severity": "high"
  }
}
```
