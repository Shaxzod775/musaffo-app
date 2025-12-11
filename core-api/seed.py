"""
Seed script to populate Firestore with initial data
Run once: python3 seed.py
"""
from datetime import datetime
from app.config.firebase import get_db

db = get_db()

def seed_projects():
    """Seed projects collection"""
    print("Seeding projects...")
    
    projects = [
        # Active projects
        {
            'id': '1',
            'titleKey': 'project_greenbelt_title',
            'descKey': 'project_greenbelt_desc',
            'title': "Yashil Belbog'",
            'description': 'Высадка 1000 чинар для защиты Сергели от пыли.',
            'targetAmount': 500000000,
            'currentAmount': 325000000,
            'status': 'active',
            'image': 'https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?auto=format&fit=crop&q=80&w=400',
            'createdAt': datetime.now(),
            'updatedAt': datetime.now()
        },
        {
            'id': '4',
            'titleKey': 'project_yakka_title',
            'descKey': 'project_yakka_desc',
            'title': 'Мониторинг промзоны Яккасарай',
            'description': 'Установка 25 IoT сенсоров для контроля выбросов заводов.',
            'targetAmount': 180000000,
            'currentAmount': 95000000,
            'status': 'active',
            'image': 'https://images.unsplash.com/photo-1581092160562-40aa08e78837?auto=format&fit=crop&q=80&w=400',
            'createdAt': datetime.now(),
            'updatedAt': datetime.now()
        },
        {
            'id': '5',
            'titleKey': 'project_bike_title',
            'descKey': 'project_bike_desc',
            'title': 'Велодорожки Юнусабад',
            'description': 'Строительство 5км велодорожек для снижения выхлопов.',
            'targetAmount': 350000000,
            'currentAmount': 120000000,
            'status': 'active',
            'image': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?auto=format&fit=crop&q=80&w=400',
            'createdAt': datetime.now(),
            'updatedAt': datetime.now()
        },
        # Completed projects
        {
            'id': '2',
            'titleKey': 'project_schools_title',
            'descKey': 'project_schools_desc',
            'title': 'Фильтры для школ №34, №110',
            'description': 'Установка HEPA фильтров в классах.',
            'targetAmount': 200000000,
            'currentAmount': 200000000,
            'status': 'completed',
            'image': 'https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&q=80&w=400',
            'createdAt': datetime.now(),
            'updatedAt': datetime.now()
        },
        {
            'id': '6',
            'titleKey': 'project_mirabad_title',
            'descKey': 'project_mirabad_desc',
            'title': 'Озеленение Мирабад',
            'description': 'Высадка 500 деревьев в районе Мирабад. Завершено в сентябре 2025.',
            'targetAmount': 85000000,
            'currentAmount': 85000000,
            'status': 'completed',
            'image': 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&q=80&w=400',
            'createdAt': datetime.now(),
            'updatedAt': datetime.now()
        },
        # Voting initiatives
        {
            'id': '3',
            'titleKey': 'project_sensors_title',
            'descKey': 'project_sensors_desc',
            'title': 'Датчики в промзоне',
            'description': 'Установка 50 локальных сенсоров для мониторинга заводов.',
            'targetAmount': 150000000,
            'currentAmount': 45000000,
            'status': 'voting',
            'image': 'https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?auto=format&fit=crop&q=80&w=400',
            'votesFor': 1205,
            'votesAgainst': 45,
            'createdAt': datetime.now(),
            'updatedAt': datetime.now()
        },
        {
            'id': '7',
            'titleKey': 'project_fines_title',
            'descKey': 'project_fines_desc',
            'title': 'Штрафы за сжигание мусора',
            'description': 'Инициатива введения штрафов 5 млн сум за сжигание мусора в черте города.',
            'targetAmount': 0,
            'currentAmount': 0,
            'status': 'voting',
            'image': 'https://images.unsplash.com/photo-1532996122724-e3c354a0b15b?auto=format&fit=crop&q=80&w=400',
            'votesFor': 892,
            'votesAgainst': 120,
            'createdAt': datetime.now(),
            'updatedAt': datetime.now()
        }
    ]
    
    for project in projects:
        project_id = project.pop('id')
        db.collection('projects').document(project_id).set(project)
        print(f"  ✓ Created project: {project['title']}")
    
    print(f"Seeded {len(projects)} projects\n")

def seed_news():
    """Seed news collection"""
    print("Seeding news...")
    
    news_items = [
        {
            'id': '1',
            'titleKey': 'news_1_title',
            'title': 'Указ Президента: Экология',
            'category': 'Gov',
            'content': {
                'ru': 'Новые субсидии на солнечные панели и фильтры для заводов с 2025 года.',
                'uz': '2025 yildan zavodlar uchun quyosh panellari va filtrlar uchun yangi subsidiyalar.',
                'en': 'New subsidies for solar panels and filters for factories from 2025.'
            },
            'imageUrl': 'https://images.unsplash.com/photo-1621451537084-482c73073a0f?auto=format&fit=crop&q=80&w=800',
            'timestamp': datetime.now(),
            'createdAt': datetime.now()
        },
        {
            'id': '2',
            'titleKey': 'news_2_title',
            'title': 'AQI 165: Воздух вредный',
            'category': 'Global',
            'content': {
                'ru': 'Uzhydromet рекомендует носить маски.',
                'uz': 'Uzhydromet niqob kiyishni tavsiya qiladi.',
                'en': 'Uzhydromet recommends wearing masks.'
            },
            'imageUrl': 'https://images.unsplash.com/photo-1621451537084-482c73073a0f?auto=format&fit=crop&q=80&w=800',
            'timestamp': datetime.now(),
            'createdAt': datetime.now()
        },
        {
            'id': '3',
            'titleKey': 'news_3_title',
            'title': 'ВОЗ: Загрязнение в Азии',
            'category': 'Global',
            'content': {
                'ru': 'Города Центральной Азии сокращают выбросы на 30% к 2030.',
                'uz': 'Markaziy Osiyodagi shaharlar 2030 yilgacha emissiyalarni 30% ga kamaytiradi.',
                'en': 'Central Asian cities aim to reduce emissions by 30% by 2030.'
            },
            'imageUrl': 'https://images.unsplash.com/photo-1621451537084-482c73073a0f?auto=format&fit=crop&q=80&w=800',
            'timestamp': datetime.now(),
            'createdAt': datetime.now()
        },
        {
            'id': '4',
            'titleKey': 'news_4_title',
            'title': 'Новые датчики: AI анализ',
            'category': 'Tech',
            'content': {
                'ru': 'Установлены 10 новых IoT датчиков с AI-анализом воздуха в Яккасарае.',
                'uz': 'Yakkasaroyda AI tahlil qilish bilan 10 ta yangi IoT sensorlari o\'rnatildi.',
                'en': '10 new IoT sensors with AI air analysis installed in Yakkasaray.'
            },
            'imageUrl': 'https://images.unsplash.com/photo-1621451537084-482c73073a0f?auto=format&fit=crop&q=80&w=800',
            'timestamp': datetime.now(),
            'createdAt': datetime.now()
        }
    ]
    
    for news in news_items:
        news_id = news.pop('id')
        db.collection('news').document(news_id).set(news)
        print(f"  ✓ Created news: {news['title']}")
    
    print(f"Seeded {len(news_items)} news items\n")

def seed_voting():
    """Seed voting collection"""
    print("Seeding voting initiatives...")
    
    voting_items = [
        {
            'id': '3',
            'titleKey': 'project_sensors_title',
            'title': 'Датчики в промзоне',
            'description': 'Установка 50 локальных сенсоров для мониторинга заводов.',
            'votesFor': 1205,
            'votesAgainst': 45,
            'status': 'active',
            'voters': [],
            'createdAt': datetime.now()
        },
        {
            'id': '7',
            'titleKey': 'project_fines_title',
            'title': 'Штрафы за сжигание мусора',
            'description': 'Инициатива введения штрафов 5 млн сум за сжигание мусора в черте города.',
            'votesFor': 892,
            'votesAgainst': 120,
            'status': 'active',
            'voters': [],
            'createdAt': datetime.now()
        }
    ]
    
    for voting in voting_items:
        voting_id = voting.pop('id')
        db.collection('voting').document(voting_id).set(voting)
        print(f"  ✓ Created voting: {voting['title']}")
    
    print(f"Seeded {len(voting_items)} voting initiatives\n")

def main():
    print("=" * 50)
    print("SEEDING FIRESTORE DATABASE")
    print("=" * 50 + "\n")
    
    # Clear existing data (optional - comment out if you want to keep existing data)
    # print("Clearing existing data...")
    # for collection in ['projects', 'news', 'voting', 'donations', 'donors', 'reports']:
    #     docs = db.collection(collection).stream()
    #     for doc in docs:
    #         doc.reference.delete()
    
    seed_projects()
    seed_news()
    seed_voting()
    
    print("=" * 50)
    print("✅ SEEDING COMPLETED!")
    print("=" * 50)
    print("\nYou can now run your frontend and it will load data from Firestore")

if __name__ == '__main__':
    main()
