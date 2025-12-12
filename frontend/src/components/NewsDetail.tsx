import React, { useEffect } from 'react';
import { X, Share2, Tag, Calendar } from 'lucide-react';
import { NewsItem } from '../types';
import { useLanguage } from '../context/LanguageContext';
import ImageWithSkeleton from './ImageWithSkeleton';

interface Props {
    news: NewsItem;
    onClose: () => void;
}

// Full article content for each news item by ID
const getNewsContent = (id: string, language: string): { paragraphs: string[], imageUrl: string } => {
    const content: Record<string, Record<string, string[]>> = {
        '1': {
            ru: [
                'Ташкент и ряд областей накрыл плотный туман, который может негативно повлиять на качество воздуха. Узгидромет сообщает, что из-за устойчивых воздушных масс, слабого ветра, температурной инверсии и поступления пыли из внешних источников ожидается повышение концентрации частиц PM2.5 и PM10.',
                'Экспертные организации продолжают мониторинг качества воздуха и рекомендуют гражданам использовать средства защиты органов дыхания при выходе на улицу.'
            ],
            uz: [
                'Toshkent shahri va bir qancha viloyatlarda kuzatilayotgan qalin tuman havoning sifatiga salbiy ta\'sir ko\'rsatishi mumkin. O\'zgidromet ma\'muriyati xabar berdi-ki, barqaror havo massalari, zaif shamol, havo inversiyasi va havoda changning tashqi manbalardan kirib kelishi natijasida PM2,5 va PM10 zarrachalari kontsentratsiyasi ko\'tarilishi kutilmoqda.',
                'Ekspert tashkilotlar havo sifatini monitoring qilishni davom ettirmoqda va fuqarolarga tashqariga chiqqanda nafas olish yo\'llarini himoya qilish vositalaridan foydalanishni tavsiya qilmoqda.'
            ],
            en: [
                'Dense fog has covered Tashkent and several regions, which may negatively affect air quality. Uzhydromet reports that due to stable air masses, weak wind, temperature inversion, and dust entering from external sources, an increase in PM2.5 and PM10 particle concentrations is expected.',
                'Expert organizations continue to monitor air quality and recommend citizens to use respiratory protection when going outside.'
            ]
        },
        '2': {
            ru: [
                'В столице Узбекистана ведётся активная борьба с загрязнением воздуха. Различные государственные ведомства проводят совместные рейды, направленные на снижение уровня загрязнения атмосферы в Ташкенте.',
                'В рамках этой кампании особое внимание уделяется проверке котельных и теплоэнергетических объектов, где выявляются и пресекаются нарушения экологических норм. Координированные действия органов власти призваны обеспечить улучшение качества воздуха в городе и защиту здоровья населения.'
            ],
            uz: [
                'O\'zbekiston poytaxtida havo ifloslanishiga qarshi faol kurash olib borilmoqda. Turli davlat idoralari Toshkentda atmosfera ifloslanishi darajasini kamaytirish maqsadida qo\'shma reydlar o\'tkazmoqda.',
                'Ushbu kampaniya doirasida qozonxonalar va issiqlik energetikasi obyektlarini tekshirishga alohida e\'tibor qaratilmoqda, u yerda ekologik me\'yorlarning buzilishlari aniqlanmoqda va oldini olinmoqda. Hokimiyat organlarining muvofiklashtirilgan harakatlari shaharda havo sifatini yaxshilash va aholi sog\'lig\'ini himoya qilishga qaratilgan.'
            ],
            en: [
                'Active fight against air pollution is underway in the capital of Uzbekistan. Various government agencies are conducting joint raids aimed at reducing the level of atmospheric pollution in Tashkent.',
                'As part of this campaign, special attention is paid to inspecting boiler houses and thermal energy facilities, where violations of environmental standards are identified and prevented. Coordinated actions of authorities are designed to improve air quality in the city and protect public health.'
            ]
        },
        '3': {
            ru: [
                'В холодный период года система отопления в жилых помещениях может стать источником серьёзной опасности для жизни. По данным официальных органов, именно в осенне-зимний сезон значительно возрастает количество несчастных случаев, связанных с пожарами, электрическими короткими замыканиями и, в особенности, отравлениями угарным газом.',
                'Угарный газ — бесцветное вещество без запаха, которое является причиной большинства домашних трагедий. Специалисты рекомендуют соблюдать пять основных правил безопасности для защиты себя и своей семьи в холодное время года. Регулярное техническое обслуживание отопительных систем может предотвратить подавляющее большинство опасных ситуаций.'
            ],
            uz: [
                'Sovuq yil faslida turar-joylardagi isitish tizimi hayot uchun jiddiy xavf manbai bo\'lishi mumkin. Rasmiy organlar ma\'lumotlariga ko\'ra, kuz-qish mavsumida yong\'inlar, elektr qisqa tutashuvlari va ayniqsa uglerod oksidi bilan zaharlanish bilan bog\'liq baxtsiz hodisalar soni sezilarli darajada ortadi.',
                'Uglerod oksidi — rangsiz va hidsiz modda bo\'lib, ko\'pchilik uy fojеalarining sababi hisoblanadi. Mutaxassislar sovuq faslda o\'zingiz va oilangizni himoya qilish uchun beshta asosiy xavfsizlik qoidalariga rioya qilishni tavsiya qilmoqda. Isitish tizimlarini muntazam texnik xizmat ko\'rsatish ko\'pchilik xavfli vaziyatlarning oldini olishi mumkin.'
            ],
            en: [
                'In the cold season, the heating system in residential premises can become a source of serious danger to life. According to official data, it is during the autumn-winter season that the number of accidents related to fires, electrical short circuits, and especially carbon monoxide poisoning significantly increases.',
                'Carbon monoxide is a colorless, odorless substance that causes most home tragedies. Experts recommend following five basic safety rules to protect yourself and your family during the cold season. Regular maintenance of heating systems can prevent the vast majority of dangerous situations.'
            ]
        },
        '4': {
            ru: [
                'Согласно обсуждению на заседании «Час Правительства» в Законодательной палате Олий Мажлиса, на строительную деятельность приходится 6 процентов от общего объёма загрязнения воздуха в городе.',
                'Депутат от Экофракции Гулчехра Тожибоева подняла вопрос о необходимости соблюдения экологических норм и требований в ходе строительных работ. Министр строительства и жилищно-коммунального хозяйства дал развёрнутый ответ на озабоченность парламентариев касательно влияния строительного сектора на качество окружающей среды.'
            ],
            uz: [
                'Oliy Majlis Qonunchilik palatasida bo\'lib o\'tgan «Hukumat soati» majlisida muhokamaga ko\'ra, shahardagi umumiy havo ifloslanishining 6 foizi qurilish faoliyatiga to\'g\'ri keladi.',
                'Ekofraksiya deputati Gulchehra Tojiboyeva qurilish ishlari davomida ekologik me\'yorlar va talablarga rioya qilish zarurligi masalasini ko\'tardi. Qurilish va uy-joy kommunal xo\'jaligi vaziri parlamentarilarning qurilish sektorining atrof-muhit sifatiga ta\'siri bo\'yicha tashvishlariga batafsil javob berdi.'
            ],
            en: [
                'According to discussions at the "Government Hour" session in the Legislative Chamber of the Oliy Majlis, construction activity accounts for 6 percent of total air pollution in the city.',
                'Eco-faction deputy Gulchehra Tojiboyeva raised the issue of the need to comply with environmental standards and requirements during construction work. The Minister of Construction and Housing and Communal Services gave a detailed response to parliamentarians\' concerns about the impact of the construction sector on environmental quality.'
            ]
        },
        '5': {
            ru: [
                'Футбольный клуб «Андижан» подвергся критике за использование дымовой пиротехники на своём мероприятии. Инцидент стал известен благодаря видео, распространившемуся в социальных сетях.',
                'Особое возмущение вызвало то, что это произошло в период сложной экологической ситуации с качеством воздуха. Дымовые устройства, использованные на церемонии представления главного тренера, вызвали недовольство жителей города и подняли вопросы об охране окружающей среды.'
            ],
            uz: [
                'Futbol klubi "Andijon" o\'z tadbirida tutunli pirotexnika vositalarini ishlatgani uchun tanqidga uchradi. Voqea ijtimoiy tarmoqlarda tarqalgan video orqali ma\'lum bo\'ldi.',
                'Ayniqsa havoning murakkab ekologik holatida sodir etilgani ko\'plab shikoyatlarni keltirib chiqardi. Klubning bosh murabbiyni taqdim etish marasimida foydalanilgan tutun chiqaruvchi qurilmalar shahar aholisini qo\'zg\'atdi va atrof-muhitni muhofaza qilish bo\'yicha savollarni keltirib chiqardi.'
            ],
            en: [
                'Football club Andijan has been criticized for using smoke pyrotechnics at its event. The incident became known through a video that spread on social networks.',
                'Particular outrage was caused by the fact that this happened during a difficult environmental situation with air quality. Smoke devices used at the head coach presentation ceremony caused discontent among city residents and raised questions about environmental protection.'
            ]
        },
        '6': {
            ru: [
                'По прогнозам метеорологов, на территории Узбекистана сегодня ожидаются туман и усиленные ветры. Температурные показатели будут колебаться в диапазоне от 0 градусов в ночные часы до 21 градуса днём.',
                'Жителям рекомендуется учитывать эти погодные условия при планировании своей деятельности. В условиях тумана следует быть особенно осторожными на дорогах и использовать средства защиты органов дыхания.'
            ],
            uz: [
                'Meteorologlar bashoratiga ko\'ra, bugun O\'zbekiston hududida tuman va kuchaygan shamollar kutilmoqda. Harorat ko\'rsatkichlari kechasi 0 daraja, kunduzi 21 darajagacha bo\'ladi.',
                'Aholiga o\'z faoliyatini rejalashtirish da ushbu ob-havo sharoitlarini hisobga olish tavsiya etiladi. Tuman sharoitida yo\'llarda ayniqsa ehtiyot bo\'lish va nafas olish a\'zolarini himoya qilish vositalaridan foydalanish lozim.'
            ],
            en: [
                'According to meteorologists, fog and strong winds are expected in Uzbekistan today. Temperature will range from 0 degrees at night to 21 degrees during the day.',
                'Residents are advised to take these weather conditions into account when planning their activities. In foggy conditions, one should be especially careful on the roads and use respiratory protection.'
            ]
        },
        '7': {
            ru: [
                'Государственная служба гидрометеорологии опубликовала информацию о плотной дымке, которая в настоящее время наблюдается на территории республики. Метеорологи отмечают, что вредные вещества остаются в воздушных слоях и не рассеиваются.',
                'Это приводит к ухудшению качества атмосферы. Специалисты продолжают мониторить ситуацию с загрязнением воздуха в различных регионах страны и рекомендуют ограничить пребывание на открытом воздухе.'
            ],
            uz: [
                'Davlat gidrometeоrologiya xizmati respublika hududida hozirda kuzatilayotgan qalin tumanlik haqida ma\'lumot e\'lon qildi. Meteorologlar zararli moddalar havo qatlamlarida qolib, tarqalmasligini ta\'kidlamoqda.',
                'Bu atmosfera sifatining yomonlashishiga olib kelmoqda. Mutaxassislar mamlakatning turli hududlarida havo ifloslanishi vaziyatini monitoring qilishda davom etmoqda va ochiq havoda bo\'lishni cheklashni tavsiya qilmoqda.'
            ],
            en: [
                'The State Hydrometeorological Service has published information about the dense haze currently observed across the republic. Meteorologists note that harmful substances remain in the air layers and do not disperse.',
                'This leads to deterioration of atmospheric quality. Specialists continue to monitor the air pollution situation in various regions of the country and recommend limiting time spent outdoors.'
            ]
        }
    };

    // Image URLs for each news article
    const imageUrls: Record<string, string> = {
        '1': 'https://images.unsplash.com/photo-1485236715568-ddc5ee6ca227?auto=format&fit=crop&w=800&q=80', // Foggy city
        '2': 'https://images.unsplash.com/photo-1611273426858-450d8e3c9fce?auto=format&fit=crop&w=800&q=80', // Industrial inspection
        '3': 'https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80', // Home heating
        '4': 'https://images.unsplash.com/photo-1504307651254-35680f356dfd?auto=format&fit=crop&w=800&q=80', // Construction site
        '5': 'https://images.unsplash.com/photo-1574629810360-7efbbe195018?auto=format&fit=crop&w=800&q=80', // Football stadium
        '6': 'https://images.unsplash.com/photo-1534088568595-a066f410bcda?auto=format&fit=crop&w=800&q=80', // Foggy weather
        '7': 'https://images.unsplash.com/photo-1532178910-7815d6919875?auto=format&fit=crop&w=800&q=80', // Smoggy atmosphere
    };

    return {
        paragraphs: content[id]?.[language] || content[id]?.['en'] || ['Content not available.'],
        imageUrl: imageUrls[id] || 'https://images.unsplash.com/photo-1621451537084-482c73073a0f?auto=format&fit=crop&w=800&q=80'
    };
};

const formatTime = (time: string, t: (key: string) => string): string => {
    // Parse time like "2 soat oldin", "30 min oldin", "5 soat oldin", "1 kun oldin"
    const match = time.match(/(\d+)\s*(soat|min|kun)/);
    if (match) {
        const [, num, unit] = match;
        if (unit === 'soat') return `${num} ${t('news_time_hours_ago')} `;
        if (unit === 'min') return `${num} ${t('news_time_minutes_ago')} `;
        if (unit === 'kun') return `${num} ${t('news_time_days_ago')} `;
    }
    return time;
};

const NewsDetail: React.FC<Props> = ({ news, onClose }) => {
    const { t, language } = useLanguage();

    // Use content from API if available, otherwise fall back to static content
    const apiContent = news.translations?.[language]?.content || news.translations?.ru?.content;
    const staticContent = getNewsContent(news.id, language);

    const paragraphs = apiContent || staticContent.paragraphs;
    const imageUrl = news.imageUrl || staticContent.imageUrl;

    // Block body scroll when modal is open
    useEffect(() => {
        document.body.style.overflow = 'hidden';
        return () => {
            document.body.style.overflow = 'unset';
        };
    }, []);

    return (
        <div className="fixed inset-0 z-[100] bg-white flex flex-col animate-slide-up">
            {/* Header Image */}
            <div className="relative h-64 w-full shrink-0">
                <ImageWithSkeleton
                    src={imageUrl}
                    className="w-full h-full object-cover"
                    alt={news.title}
                />
                <div className="absolute inset-0 bg-gradient-to-b from-black/30 to-transparent"></div>
                <button
                    onClick={onClose}
                    className="absolute top-4 right-4 bg-black/20 backdrop-blur p-2 rounded-full text-white hover:bg-black/40 transition-colors"
                >
                    <X size={24} />
                </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-6">
                <div className="flex gap-2 mb-4">
                    <span className="bg-[#40A7E3]/10 text-[#40A7E3] px-3 py-1 rounded-lg text-xs font-bold uppercase flex items-center gap-1">
                        <Tag size={12} /> {news.tag}
                    </span>
                    <span className="bg-[#F3F4F6] text-[#9CA3AF] px-3 py-1 rounded-lg text-xs font-bold flex items-center gap-1">
                        <Calendar size={12} /> {formatTime(news.time, t)}
                    </span>
                </div>

                <h1 className="text-2xl font-bold text-[#1F2937] mb-4 leading-tight">{news.title}</h1>

                <div className="prose prose-sm text-[#4B5563]">
                    <p className="font-medium text-lg text-[#1F2937] mb-4">{news.summary}</p>
                    {paragraphs.map((paragraph, index) => (
                        <p key={index} className={index > 0 ? 'mt-4' : ''}>
                            {paragraph}
                        </p>
                    ))}
                </div>
            </div>

            {/* Footer Actions */}
            <div className="p-4 border-t border-[#E5E7EB] bg-white pb-safe">
                <button
                    onClick={async () => {
                        const shareData = {
                            title: news.title || '',
                            text: news.summary || '',
                            url: window.location.href
                        };

                        try {
                            if (navigator.share) {
                                await navigator.share(shareData);
                            } else {
                                // Fallback: copy to clipboard
                                const text = `${shareData.title}\n\n${shareData.text}\n\n${shareData.url}`;
                                await navigator.clipboard.writeText(text);
                                alert(language === 'ru' ? 'Скопировано в буфер обмена!' : language === 'uz' ? 'Nusxalandi!' : 'Copied to clipboard!');
                            }
                        } catch (err) {
                            console.log('Share cancelled or failed');
                        }
                    }}
                    className="w-full bg-[#F3F4F6] text-[#1F2937] py-3.5 rounded-xl font-bold flex items-center justify-center gap-2 hover:bg-[#E5E7EB] active:scale-95 transition-all"
                >
                    <Share2 size={20} /> {t('news_share')}
                </button>
            </div>
        </div>
    );
};

export default NewsDetail;
