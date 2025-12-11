# Core API Service

Основной API сервис для Musaffo - управление проектами, донатами, статистикой.

## Особенности
- Firestore database
- CRUD для projects, donations, voting, reports
- Stats API
- AQI proxy (использует iqair-service)

## Запуск

```bash
# Установка зависимостей
pip install -r requirements.txt

# Создать .env файл
cp .env.example .env
# Настроить Firebase credentials

# Запуск
python main.py
```

По умолчанию запускается на порту **8001**.

## API Endpoints

### Projects
- GET /api/projects
- POST /api/projects
- GET /api/projects/{id}
- PUT /api/projects/{id}
- DELETE /api/projects/{id}

### Donations
- POST /api/donations
- GET /api/donations/donor/{userId}

### Voting
- POST /api/voting

### Stats
- GET /api/stats

### AQI (proxy to iqair-service)
- GET /api/air-quality
