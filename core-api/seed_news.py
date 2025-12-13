"""
Seed script to add eco news to Firebase
Run: python seed_news.py
"""
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta

# Initialize Firebase
cred = credentials.Certificate('musaffo-33cf5-firebase-adminsdk-fbsvc-9215754308.json')
try:
    firebase_admin.initialize_app(cred)
except ValueError:
    pass  # Already initialized

db = firestore.client()

# News data with translations
news_data = [
    {
        "source": "O'zgidromet",
        "tag": "Gov",
        "imageUrl": "https://images.unsplash.com/photo-1485236715568-ddc5ee6ca227?auto=format&fit=crop&w=800&q=80",
        "translations": {
            "ru": {
                "title": "Туман может повысить уровень PM2.5 — Узгидромет",
                "summary": "Плотный туман и инверсия способствуют накоплению мелких частиц в воздухе.",
                "content": [
                    "Ташкент и ряд областей накрыл плотный туман, который может негативно повлиять на качество воздуха. Узгидромет сообщает, что из-за устойчивых воздушных масс, слабого ветра, температурной инверсии и поступления пыли из внешних источников ожидается повышение концентрации частиц PM2.5 и PM10.",
                    "Экспертные организации продолжают мониторинг качества воздуха и рекомендуют гражданам использовать средства защиты органов дыхания при выходе на улицу."
                ]
            },
            "uz": {
                "title": "Tuman PM2.5 darajasini oshirishi mumkin — O'zgidromet",
                "summary": "Qalin tuman va inversiya havodagi mayda zarralar to'planishiga sabab bo'lmoqda.",
                "content": [
                    "Toshkent shahri va bir qancha viloyatlarda kuzatilayotgan qalin tuman havoning sifatiga salbiy ta'sir ko'rsatishi mumkin. O'zgidromet ma'muriyati xabar berdi-ki, barqaror havo massalari, zaif shamol, havo inversiyasi va havoda changning tashqi manbalardan kirib kelishi natijasida PM2,5 va PM10 zarrachalari kontsentratsiyasi ko'tarilishi kutilmoqda.",
                    "Ekspert tashkilotlar havo sifatini monitoring qilishni davom ettirmoqda va fuqarolarga tashqariga chiqqanda nafas olish yo'llarini himoya qilish vositalaridan foydalanishni tavsiya qilmoqda."
                ]
            },
            "en": {
                "title": "Fog may increase PM2.5 levels — Uzhydromet",
                "summary": "Dense fog and inversion contribute to accumulation of fine particles in air.",
                "content": [
                    "Dense fog has covered Tashkent and several regions, which may negatively affect air quality. Uzhydromet reports that due to stable air masses, weak wind, temperature inversion, and dust entering from external sources, an increase in PM2.5 and PM10 particle concentrations is expected.",
                    "Expert organizations continue to monitor air quality and recommend citizens to use respiratory protection when going outside."
                ]
            }
        }
    },
    {
        "source": "Kun.uz",
        "tag": "Gov",
        "imageUrl": "https://images.unsplash.com/photo-1611273426858-450d8e3c9fce?auto=format&fit=crop&w=800&q=80",
        "translations": {
            "ru": {
                "title": "Борьба с загрязнением воздуха в Ташкенте",
                "summary": "Госорганы проводят рейды по проверке котельных и теплоэнергетических объектов.",
                "content": [
                    "В столице Узбекистана ведётся активная борьба с загрязнением воздуха. Различные государственные ведомства проводят совместные рейды, направленные на снижение уровня загрязнения атмосферы в Ташкенте.",
                    "В рамках этой кампании особое внимание уделяется проверке котельных и теплоэнергетических объектов, где выявляются и пресекаются нарушения экологических норм. Координированные действия органов власти призваны обеспечить улучшение качества воздуха в городе и защиту здоровья населения."
                ]
            },
            "uz": {
                "title": "Toshkentda havo ifloslanishiga qarshi kurash",
                "summary": "Davlat organlari qozonxonalar va issiqlik energetika obyektlarini tekshirmoqda.",
                "content": [
                    "O'zbekiston poytaxtida havo ifloslanishiga qarshi faol kurash olib borilmoqda. Turli davlat idoralari Toshkentda atmosfera ifloslanishi darajasini kamaytirish maqsadida qo'shma reydlar o'tkazmoqda.",
                    "Ushbu kampaniya doirasida qozonxonalar va issiqlik energetikasi obyektlarini tekshirishga alohida e'tibor qaratilmoqda, u yerda ekologik me'yorlarning buzilishlari aniqlanmoqda va oldini olinmoqda. Hokimiyat organlarining muvofiklashtirilgan harakatlari shaharda havo sifatini yaxshilash va aholi sog'lig'ini himoya qilishga qaratilgan."
                ]
            },
            "en": {
                "title": "Fight against air pollution in Tashkent",
                "summary": "Authorities conduct raids inspecting boilers and thermal energy facilities.",
                "content": [
                    "Active fight against air pollution is underway in the capital of Uzbekistan. Various government agencies are conducting joint raids aimed at reducing the level of atmospheric pollution in Tashkent.",
                    "As part of this campaign, special attention is paid to inspecting boiler houses and thermal energy facilities, where violations of environmental standards are identified and prevented. Coordinated actions of authorities are designed to improve air quality in the city and protect public health."
                ]
            }
        }
    },
    {
        "source": "MyGov.uz",
        "tag": "Global",
        "imageUrl": "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80",
        "translations": {
            "ru": {
                "title": "Опасность отопления зимой",
                "summary": "Отравление угарным газом — главная причина домашних трагедий в холодный сезон.",
                "content": [
                    "В холодный период года система отопления в жилых помещениях может стать источником серьёзной опасности для жизни. По данным официальных органов, именно в осенне-зимний сезон значительно возрастает количество несчастных случаев, связанных с пожарами, электрическими короткими замыканиями и, в особенности, отравлениями угарным газом.",
                    "Угарный газ — бесцветное вещество без запаха, которое является причиной большинства домашних трагедий. Специалисты рекомендуют соблюдать пять основных правил безопасности для защиты себя и своей семьи в холодное время года. Регулярное техническое обслуживание отопительных систем может предотвратить подавляющее большинство опасных ситуаций."
                ]
            },
            "uz": {
                "title": "Qishda isitish tizimi xavfi",
                "summary": "Uglerod oksidi bilan zaharlanish — sovuq mavsumda uy fojеalarining asosiy sababi.",
                "content": [
                    "Sovuq yil faslida turar-joylardagi isitish tizimi hayot uchun jiddiy xavf manbai bo'lishi mumkin. Rasmiy organlar ma'lumotlariga ko'ra, kuz-qish mavsumida yong'inlar, elektr qisqa tutashuvlari va ayniqsa uglerod oksidi bilan zaharlanish bilan bog'liq baxtsiz hodisalar soni sezilarli darajada ortadi.",
                    "Uglerod oksidi — rangsiz va hidsiz modda bo'lib, ko'pchilik uy fojеalarining sababi hisoblanadi. Mutaxassislar sovuq faslda o'zingiz va oilangizni himoya qilish uchun beshta asosiy xavfsizlik qoidalariga rioya qilishni tavsiya qilmoqda. Isitish tizimlarini muntazam texnik xizmat ko'rsatish ko'pchilik xavfli vaziyatlarning oldini olishi mumkin."
                ]
            },
            "en": {
                "title": "Winter heating system dangers",
                "summary": "Carbon monoxide poisoning is the main cause of home tragedies in cold season.",
                "content": [
                    "In the cold season, the heating system in residential premises can become a source of serious danger to life. According to official data, it is during the autumn-winter season that the number of accidents related to fires, electrical short circuits, and especially carbon monoxide poisoning significantly increases.",
                    "Carbon monoxide is a colorless, odorless substance that causes most home tragedies. Experts recommend following five basic safety rules to protect yourself and your family during the cold season. Regular maintenance of heating systems can prevent the vast majority of dangerous situations."
                ]
            }
        }
    },
    {
        "source": "Daryo",
        "tag": "Gov",
        "imageUrl": "https://images.unsplash.com/photo-1504307651254-35680f356dfd?auto=format&fit=crop&w=800&q=80",
        "translations": {
            "ru": {
                "title": "Строительство даёт 6% загрязнения воздуха",
                "summary": "Депутат Экофракции подняла вопрос о соблюдении экологических норм на стройках.",
                "content": [
                    "Согласно обсуждению на заседании «Час Правительства» в Законодательной палате Олий Мажлиса, на строительную деятельность приходится 6 процентов от общего объёма загрязнения воздуха в городе.",
                    "Депутат от Экофракции Гулчехра Тожибоева подняла вопрос о необходимости соблюдения экологических норм и требований в ходе строительных работ. Министр строительства и жилищно-коммунального хозяйства дал развёрнутый ответ на озабоченность парламентариев касательно влияния строительного сектора на качество окружающей среды."
                ]
            },
            "uz": {
                "title": "Qurilish havo ifloslanishining 6% ini tashkil etadi",
                "summary": "Ekofraksiya deputati qurilishlarda ekologik me'yorlarga rioya qilish masalasini ko'tardi.",
                "content": [
                    "Oliy Majlis Qonunchilik palatasida bo'lib o'tgan «Hukumat soati» majlisida muhokamaga ko'ra, shahardagi umumiy havo ifloslanishining 6 foizi qurilish faoliyatiga to'g'ri keladi.",
                    "Ekofraksiya deputati Gulchehra Tojiboyeva qurilish ishlari davomida ekologik me'yorlar va talablarga rioya qilish zarurligi masalasini ko'tardi. Qurilish va uy-joy kommunal xo'jaligi vaziri parlamentarilarning qurilish sektorining atrof-muhit sifatiga ta'siri bo'yicha tashvishlariga batafsil javob berdi."
                ]
            },
            "en": {
                "title": "Construction accounts for 6% of air pollution",
                "summary": "Eco-faction deputy raised the issue of environmental compliance at construction sites.",
                "content": [
                    "According to discussions at the \"Government Hour\" session in the Legislative Chamber of the Oliy Majlis, construction activity accounts for 6 percent of total air pollution in the city.",
                    "Eco-faction deputy Gulchehra Tojiboyeva raised the issue of the need to comply with environmental standards and requirements during construction work. The Minister of Construction and Housing and Communal Services gave a detailed response to parliamentarians' concerns about the impact of the construction sector on environmental quality."
                ]
            }
        }
    },
    {
        "source": "Kun.uz",
        "tag": "Global",
        "imageUrl": "https://images.unsplash.com/photo-1574629810360-7efbbe195018?auto=format&fit=crop&w=800&q=80",
        "translations": {
            "ru": {
                "title": "ФК «Андижан» под критикой за пиротехнику",
                "summary": "Клуб использовал дымовые устройства при сложной экологической ситуации.",
                "content": [
                    "Футбольный клуб «Андижан» подвергся критике за использование дымовой пиротехники на своём мероприятии. Инцидент стал известен благодаря видео, распространившемуся в социальных сетях.",
                    "Особое возмущение вызвало то, что это произошло в период сложной экологической ситуации с качеством воздуха. Дымовые устройства, использованные на церемонии представления главного тренера, вызвали недовольство жителей города и подняли вопросы об охране окружающей среды."
                ]
            },
            "uz": {
                "title": "\"Andijon\" FK pirotexnika uchun tanqid ostida",
                "summary": "Klub murakkab ekologik vaziyatda tutunli qurilmalardan foydalandi.",
                "content": [
                    "Futbol klubi \"Andijon\" o'z tadbirida tutunli pirotexnika vositalarini ishlatgani uchun tanqidga uchradi. Voqea ijtimoiy tarmoqlarda tarqalgan video orqali ma'lum bo'ldi.",
                    "Ayniqsa havoning murakkab ekologik holatida sodir etilgani ko'plab shikoyatlarni keltirib chiqardi. Klubning bosh murabbiyni taqdim etish marasimida foydalanilgan tutun chiqaruvchi qurilmalar shahar aholisini qo'zg'atdi va atrof-muhitni muhofaza qilish bo'yicha savollarni keltirib chiqardi."
                ]
            },
            "en": {
                "title": "FC Andijan criticized for pyrotechnics",
                "summary": "Club used smoke devices during difficult environmental situation.",
                "content": [
                    "Football club Andijan has been criticized for using smoke pyrotechnics at its event. The incident became known through a video that spread on social networks.",
                    "Particular outrage was caused by the fact that this happened during a difficult environmental situation with air quality. Smoke devices used at the head coach presentation ceremony caused discontent among city residents and raised questions about environmental protection."
                ]
            }
        }
    },
    {
        "source": "O'zgidromet",
        "tag": "Global",
        "imageUrl": "https://images.unsplash.com/photo-1534088568595-a066f410bcda?auto=format&fit=crop&w=800&q=80",
        "translations": {
            "ru": {
                "title": "Сегодня ожидаются туман и сильные ветры",
                "summary": "Температура от 0°C ночью до 21°C днём. Учитывайте погоду при планировании.",
                "content": [
                    "По прогнозам метеорологов, на территории Узбекистана сегодня ожидаются туман и усиленные ветры. Температурные показатели будут колебаться в диапазоне от 0 градусов в ночные часы до 21 градуса днём.",
                    "Жителям рекомендуется учитывать эти погодные условия при планировании своей деятельности. В условиях тумана следует быть особенно осторожными на дорогах и использовать средства защиты органов дыхания."
                ]
            },
            "uz": {
                "title": "Bugun tuman va kuchli shamol kutilmoqda",
                "summary": "Harorat kechasi 0°C dan kunduzi 21°C gacha. Ob-havoni hisobga oling.",
                "content": [
                    "Meteorologlar bashoratiga ko'ra, bugun O'zbekiston hududida tuman va kuchaygan shamollar kutilmoqda. Harorat ko'rsatkichlari kechasi 0 daraja, kunduzi 21 darajagacha bo'ladi.",
                    "Aholiga o'z faoliyatini rejalashtirishda ushbu ob-havo sharoitlarini hisobga olish tavsiya etiladi. Tuman sharoitida yo'llarda ayniqsa ehtiyot bo'lish va nafas olish a'zolarini himoya qilish vositalaridan foydalanish lozim."
                ]
            },
            "en": {
                "title": "Fog and strong winds expected today",
                "summary": "Temperature from 0°C at night to 21°C during day. Consider weather when planning.",
                "content": [
                    "According to meteorologists, fog and strong winds are expected in Uzbekistan today. Temperature will range from 0 degrees at night to 21 degrees during the day.",
                    "Residents are advised to take these weather conditions into account when planning their activities. In foggy conditions, one should be especially careful on the roads and use respiratory protection."
                ]
            }
        }
    },
    {
        "source": "O'zgidromet",
        "tag": "Gov",
        "imageUrl": "https://images.unsplash.com/photo-1532178910-7815d6919875?auto=format&fit=crop&w=800&q=80",
        "translations": {
            "ru": {
                "title": "Загрязняющие вещества накапливаются в атмосфере",
                "summary": "Вредные вещества не рассеиваются из-за плотной дымки над страной.",
                "content": [
                    "Государственная служба гидрометеорологии опубликовала информацию о плотной дымке, которая в настоящее время наблюдается на территории республики. Метеорологи отмечают, что вредные вещества остаются в воздушных слоях и не рассеиваются.",
                    "Это приводит к ухудшению качества атмосферы. Специалисты продолжают мониторить ситуацию с загрязнением воздуха в различных регионах страны и рекомендуют ограничить пребывание на открытом воздухе."
                ]
            },
            "uz": {
                "title": "Ifloslantiruvchi moddalar atmosferada to'planmoqda",
                "summary": "Qalin tuman sababli zararli moddalar tarqalmamoqda.",
                "content": [
                    "Davlat gidrometeоrologiya xizmati respublika hududida hozirda kuzatilayotgan qalin tumanlik haqida ma'lumot e'lon qildi. Meteorologlar zararli moddalar havo qatlamlarida qolib, tarqalmasligini ta'kidlamoqda.",
                    "Bu atmosfera sifatining yomonlashishiga olib kelmoqda. Mutaxassislar mamlakatning turli hududlarida havo ifloslanishi vaziyatini monitoring qilishda davom etmoqda va ochiq havoda bo'lishni cheklashni tavsiya qilmoqda."
                ]
            },
            "en": {
                "title": "Pollutants accumulating in atmosphere",
                "summary": "Harmful substances not dispersing due to dense haze over country.",
                "content": [
                    "The State Hydrometeorological Service has published information about the dense haze currently observed across the republic. Meteorologists note that harmful substances remain in the air layers and do not disperse.",
                    "This leads to deterioration of atmospheric quality. Specialists continue to monitor the air pollution situation in various regions of the country and recommend limiting time spent outdoors."
                ]
            }
        }
    }
]


def delete_all_news():
    """Delete all existing news from Firebase"""
    print("Deleting all existing news...")
    news_ref = db.collection('news')
    docs = news_ref.stream()
    deleted = 0
    for doc in docs:
        doc.reference.delete()
        deleted += 1
    print(f"Deleted {deleted} news articles")


def seed_news():
    """Add all news articles to Firebase"""
    print("Seeding news articles...")

    for i, news in enumerate(news_data):
        # Set timestamp with hours offset to simulate different times
        news['timestamp'] = datetime.now() - timedelta(hours=i+1)
        news['createdAt'] = datetime.now() - timedelta(hours=i+1)

        doc_ref = db.collection('news').document()
        doc_ref.set(news)
        print(f"Added: {news['translations']['ru']['title'][:50]}...")

    print(f"\nSuccessfully added {len(news_data)} news articles to Firebase!")


if __name__ == "__main__":
    delete_all_news()
    seed_news()
