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
const getNewsContent = (id: string, language: string): { paragraphs: string[] } => {
    const content: Record<string, Record<string, string[]>> = {
        '1': {
            ru: [
                'Президент Узбекистана подписал указ о новых субсидиях для предприятий, внедряющих экологически чистые технологии. Начиная с 2025 года, заводы смогут получить до 50% компенсации затрат на установку солнечных панелей и современных систем фильтрации.',
                'По оценкам экспертов, эта мера позволит сократить выбросы в атмосферу на 30% в течение следующих пяти лет. Особое внимание уделяется промышленным зонам Сергели и Яккасарай, где уровень загрязнения находится на критическом уровне.'
            ],
            uz: [
                'O\'zbekiston Prezidenti ekologik toza texnologiyalarni joriy etayotgan korxonalarga yangi subsidiyalar to\'g\'risidagi farmonni imzoladi. 2025 yildan boshlab zavodlar quyosh panellari va zamonaviy filtrlash tizimlarini o\'rnatish xarajatlarining 50 foizigacha kompensatsiya olishlari mumkin.',
                'Mutaxassislarning taxminlariga ko\'ra, bu chora keyingi besh yil ichida atmosferaga chiqarilgan chiqindilarni 30 foizga qisqartirish imkonini beradi. Ifloslanish darajasi juda yuqori bo\'lgan Sergeli va Yakkasaroy sanoat zonalariga alohida e\'tibor qaratilmoqda.'
            ],
            en: [
                'The President of Uzbekistan has signed a decree on new subsidies for enterprises implementing environmentally friendly technologies. Starting from 2025, factories will be able to receive up to 50% compensation for the installation of solar panels and modern filtration systems.',
                'According to expert estimates, this measure will reduce atmospheric emissions by 30% over the next five years. Special attention is paid to the industrial zones of Sergeli and Yakkasaray, where pollution levels are at critical levels.'
            ]
        },
        '2': {
            ru: [
                'Узгидромет прогнозирует дождь в Ташкенте во второй половине дня. Осадки ожидаются с 15:00 до 20:00. Это должно существенно улучшить качество воздуха в столице.',
                'Уровень PM2.5 может снизиться с текущих 180 мкг/м³ до 80-100 мкг/м³ после дождя. Жителям рекомендуется проветрить помещения во время и сразу после осадков.'
            ],
            uz: [
                'Uzgidromet Toshkentda kunning ikkinchi yarmida yomg\'ir yog\'ishini bashorat qilmoqda. Yog\'ingarchilik soat 15:00 dan 20:00 gacha kutilmoqda. Bu poytaxt havosini sezilarli darajada yaxshilashi kerak.',
                'PM2.5 darajasi yomg\'irdan keyin hozirgi 180 mkg/m³ dan 80-100 mkg/m³ gacha tushishi mumkin. Aholiga yomg\'ir vaqtida va undan keyin darhol xonalarni shamollatish tavsiya etiladi.'
            ],
            en: [
                'Uzhydromet forecasts rain in Tashkent in the afternoon. Precipitation is expected from 15:00 to 20:00. This should significantly improve air quality in the capital.',
                'PM2.5 levels may drop from the current 180 µg/m³ to 80-100 µg/m³ after the rain. Residents are advised to ventilate their premises during and immediately after the precipitation.'
            ]
        },
        '3': {
            ru: [
                'В ежегодном отчёте Всемирной организации здравоохранения Ташкент занял 47-е место в списке 50 городов мира с наиболее загрязнённым воздухом. Основными факторами загрязнения названы автомобильные выхлопы, промышленные выбросы и сжигание мусора.',
                'Эксперты ВОЗ рекомендуют Узбекистану ускорить переход на электротранспорт и усилить контроль за промышленными выбросами. По их оценкам, загрязнение воздуха ежегодно приводит к 15 000 преждевременных смертей в стране.'
            ],
            uz: [
                'Jahon sog\'liqni saqlash tashkilotining yillik hisobotida Toshkent dunyodagi 50 ta eng ifloslangan havo sifatiga ega shaharlar ro\'yxatida 47-o\'rinni egalladi. Ifloslanishning asosiy omillari sifatida avtomobil egzozlari, sanoat chiqindilari va chiqindilarni yoqish ko\'rsatildi.',
                'JSST mutaxassislari O\'zbekistonga elektr transportga o\'tishni tezlashtirish va sanoat chiqindilarini nazoratini kuchaytirishni tavsiya qilmoqda. Ularning hisob-kitoblariga ko\'ra, havo ifloslanishi har yili mamlakatda 15 000 ta erta o\'limga sabab bo\'lmoqda.'
            ],
            en: [
                'In the annual report by the World Health Organization, Tashkent ranked 47th in the list of 50 cities with the most polluted air in the world. The main pollution factors are vehicle exhaust, industrial emissions, and garbage burning.',
                'WHO experts recommend Uzbekistan to accelerate the transition to electric transport and strengthen control over industrial emissions. According to their estimates, air pollution leads to 15,000 premature deaths annually in the country.'
            ]
        },
        '4': {
            ru: [
                'В районе Сергели установлено 10 новых станций мониторинга качества воздуха. Датчики измеряют уровень PM2.5, PM10, CO2, NO2 и озона в режиме реального времени.',
                'Данные со станций доступны в приложении Musaffo и на сайте Экокомитета. Это позволит жителям района получать актуальную информацию о качестве воздуха и принимать меры для защиты своего здоровья.'
            ],
            uz: [
                'Sergeli tumanida 10 ta yangi havo sifati monitoring stansiyasi o\'rnatildi. Sensorlar PM2.5, PM10, CO2, NO2 va ozon darajasini real vaqt rejimida o\'lchaydi.',
                'Stansiyalardan olingan ma\'lumotlar Musaffo ilovasida va Ekoqo\'mita veb-saytida mavjud. Bu tuman aholisiga havo sifati haqida so\'nggi ma\'lumotlarni olish va sog\'liqlarini himoya qilish uchun choralar ko\'rish imkonini beradi.'
            ],
            en: [
                '10 new air quality monitoring stations have been installed in the Sergeli district. The sensors measure PM2.5, PM10, CO2, NO2, and ozone levels in real-time.',
                'Data from the stations is available in the Musaffo app and on the Eco-committee website. This will allow residents of the district to receive up-to-date information about air quality and take measures to protect their health.'
            ]
        }
    };

    return {
        paragraphs: content[id]?.[language] || content[id]?.['en'] || ['Content not available.']
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
    const content = getNewsContent(news.id, language);
    const imageUrl = "https://images.unsplash.com/photo-1621451537084-482c73073a0f?auto=format&fit=crop&q=80&w=800"; // Placeholder image

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
                    {content.paragraphs.map((paragraph, index) => (
                        <p key={index} className={index > 0 ? 'mt-4' : ''}>
                            {paragraph}
                        </p>
                    ))}
                </div>
            </div>

            {/* Footer Actions */}
            <div className="p-4 border-t border-[#E5E7EB] bg-white pb-safe">
                <button className="w-full bg-[#F3F4F6] text-[#1F2937] py-3.5 rounded-xl font-bold flex items-center justify-center gap-2 hover:bg-[#E5E7EB] active:scale-95 transition-all">
                    <Share2 size={20} /> {t('news_share')}
                </button>
            </div>
        </div>
    );
};

export default NewsDetail;
