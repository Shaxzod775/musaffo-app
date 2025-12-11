import React from 'react';
import { ArrowLeft, AlertTriangle, Shield, Heart, Wind, Baby, User, Activity } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

interface HealthRecommendationsProps {
    onBack: () => void;
    aqiLevel: string;
    aqi: number;
}

const HealthRecommendations: React.FC<HealthRecommendationsProps> = ({ onBack, aqiLevel, aqi }) => {
    const { t, language } = useLanguage();

    const recommendations = {
        good: {
            title: { ru: 'Качество воздуха отличное', uz: "Havo sifati a'lo", en: 'Air quality is excellent' },
            description: {
                ru: 'Воздух чистый, никаких ограничений для активности на улице.',
                uz: "Havo toza, ko'chada faoliyat uchun hech qanday cheklovlar yo'q.",
                en: 'Air is clean, no restrictions for outdoor activity.'
            },

            tips: [
                { ru: 'Наслаждайтесь прогулками', uz: 'Sayr qilishdan zavqlaning', en: 'Enjoy outdoor walks' },
                { ru: 'Занимайтесь спортом на улице', uz: "Ko'chada sport bilan shug'ullaning", en: 'Exercise outdoors' },
                { ru: 'Проветривайте помещения', uz: 'Xonalarni shamollating', en: 'Ventilate rooms' }
            ],
            color: 'bg-green-500'
        },
        moderate: {
            title: { ru: 'Умеренное качество воздуха', uz: "O'rtacha havo sifati", en: 'Moderate air quality' },
            description: {
                ru: 'Чувствительные люди могут испытывать легкий дискомфорт.',
                uz: "Sezgir odamlar engil noqulaylik his qilishi mumkin.",
                en: 'Sensitive individuals may experience slight discomfort.'
            },

            risks: [
                { ru: 'Раздражение глаз и горла', uz: "Ko'z va tomoq tirnashi", en: 'Eye and throat irritation' },
                { ru: 'Легкое затруднение дыхания у астматиков', uz: 'Astmatiklarda engil nafas olish qiyinligi', en: 'Mild breathing difficulty for asthmatics' }
            ],
            tips: [
                { ru: 'Ограничьте длительную активность на улице', uz: "Uzoq muddatli tashqi faoliyatni cheklang", en: 'Limit prolonged outdoor activity' },
                { ru: 'Следите за симптомами', uz: "Alomatlarni kuzating", en: 'Monitor symptoms' }
            ],
            color: 'bg-yellow-500'
        },
        unhealthy_sensitive: {
            title: { ru: 'Вредно для чувствительных групп', uz: 'Sezgir guruhlar uchun zararli', en: 'Unhealthy for sensitive groups' },
            description: {
                ru: 'Дети, пожилые и люди с заболеваниями легких/сердца подвержены риску.',
                uz: "Bolalar, keksalar va o'pka/yurak kasalliklari bor odamlar xavf ostida.",
                en: 'Children, elderly, and people with lung/heart conditions are at risk.'
            },

            risks: [
                { ru: 'Приступы астмы', uz: 'Astma xurujlari', en: 'Asthma attacks' },
                { ru: 'Обострение ХОБЛ', uz: 'XOBL kuchayishi', en: 'COPD exacerbation' },
                { ru: 'Затрудненное дыхание', uz: 'Nafas olish qiyinligi', en: 'Breathing difficulties' },
                { ru: 'Кашель и хрипы', uz: "Yo'tal va xirillash", en: 'Coughing and wheezing' }
            ],
            tips: [
                { ru: 'Носите маску N95/FFP2 на улице', uz: "Ko'chada N95/FFP2 niqob taqing", en: 'Wear N95/FFP2 mask outdoors' },
                { ru: 'Используйте очиститель воздуха дома', uz: 'Uyda havo tozalagichidan foydalaning', en: 'Use air purifier at home' },
                { ru: 'Избегайте физических нагрузок на улице', uz: "Ko'chada jismoniy mashqlardan saqlaning", en: 'Avoid outdoor exercise' },
                { ru: 'Держите окна закрытыми', uz: "Derazalarni yopiq tuting", en: 'Keep windows closed' }
            ],
            color: 'bg-orange-500'
        },
        unhealthy: {
            title: { ru: 'Вредно для всех', uz: 'Hamma uchun zararli', en: 'Unhealthy for everyone' },
            description: {
                ru: 'Все могут испытывать проблемы со здоровьем. Ограничьте время на улице.',
                uz: "Hamma sog'liq muammolarini his qilishi mumkin. Tashqarida vaqtni cheklang.",
                en: 'Everyone may experience health effects. Limit outdoor time.'
            },

            risks: [
                { ru: 'Воспаление дыхательных путей', uz: "Nafas yo'llari yallig'lanishi", en: 'Respiratory inflammation' },
                { ru: 'Сердечно-сосудистые проблемы', uz: 'Yurak-qon tomir muammolari', en: 'Cardiovascular issues' },
                { ru: 'Головные боли и усталость', uz: "Bosh og'rig'i va charchoq", en: 'Headaches and fatigue' },
                { ru: 'Снижение функций легких', uz: "O'pka faoliyatining pasayishi", en: 'Reduced lung function' }
            ],
            tips: [
                { ru: 'Оставайтесь дома по возможности', uz: 'Iloji boricha uyda qoling', en: 'Stay indoors if possible' },
                { ru: 'Закройте все окна и двери', uz: 'Barcha deraza va eshiklarni yoping', en: 'Close all windows and doors' },
                { ru: 'Включите HEPA-очиститель воздуха', uz: 'HEPA havo tozalagichni yoqing', en: 'Run HEPA air purifier' },
                { ru: 'Пейте больше воды', uz: "Ko'proq suv iching", en: 'Drink more water' },
                { ru: 'Обратитесь к врачу при симптомах', uz: "Alomatlar bo'lsa shifokorga murojaat qiling", en: 'See doctor if symptoms occur' }
            ],
            color: 'bg-red-500'
        },
        very_unhealthy: {
            title: { ru: 'Очень вредно', uz: 'Juda zararli', en: 'Very unhealthy' },
            description: {
                ru: 'Серьезные риски для здоровья. Увеличение обращений в скорую помощь.',
                uz: "Jiddiy sog'liq xavflari. Tez yordam chaqiruvlari ko'payadi.",
                en: 'Serious health risks. Emergency room visits increase.'
            },

            risks: [
                { ru: 'Тяжелые приступы астмы', uz: "Og'ir astma xurujlari", en: 'Severe asthma attacks' },
                { ru: 'Инфаркты и инсульты у групп риска', uz: 'Xavf guruhlari uchun infarkt va insult', en: 'Heart attacks and strokes for at-risk groups' },
                { ru: 'Острый бронхит', uz: "O'tkir bronxit", en: 'Acute bronchitis' },
                { ru: 'Серьезное воспаление легких', uz: "O'pkaning jiddiy yallig'lanishi", en: 'Serious lung inflammation' }
            ],
            tips: [
                { ru: 'НЕ ВЫХОДИТЕ на улицу!', uz: "Ko'chaga CHIQMANG!", en: 'DO NOT go outside!' },
                { ru: 'Используйте респиратор даже в помещении', uz: 'Xonada ham respiratordan foydalaning', en: 'Use respirator even indoors' },
                { ru: 'Имейте лекарства под рукой', uz: "Dorilarni qo'l ostida saqlang", en: 'Keep medications handy' },
                { ru: 'Звоните в скорую при ухудшении', uz: "Holat yomonlashsa tez yordamga qo'ng'iroq qiling", en: 'Call emergency if worsening' }
            ],
            color: 'bg-purple-600'
        },
        hazardous: {
            title: { ru: 'ОПАСНО ДЛЯ ЖИЗНИ', uz: 'HAYOT UCHUN XAVFLI', en: 'HAZARDOUS' },
            description: {
                ru: 'Чрезвычайная ситуация! Опасно для всех без исключения.',
                uz: 'Favqulodda holat! Hammaga istisnosiz xavfli.',
                en: 'Health emergency! Dangerous for everyone without exception.'
            },

            risks: [
                { ru: 'Острые сердечно-сосудистые события', uz: "O'tkir yurak-qon tomir hodisalari", en: 'Acute cardiovascular events' },
                { ru: 'Тяжелое повреждение легких', uz: "O'pkaning og'ir shikastlanishi", en: 'Severe lung damage' },
                { ru: 'Риск преждевременной смерти', uz: 'Erta o\'lim xavfi', en: 'Risk of premature death' },
                { ru: 'Необратимые последствия для здоровья', uz: "Sog'liq uchun qaytarilmas oqibatlar", en: 'Irreversible health effects' }
            ],
            tips: [
                { ru: 'ЭВАКУИРУЙТЕСЬ если возможно', uz: 'Iloji bo\'lsa EVAKUATSIYA qiling', en: 'EVACUATE if possible' },
                { ru: 'Полная изоляция от уличного воздуха', uz: "Ko'cha havosidan to'liq izolyatsiya", en: 'Complete isolation from outdoor air' },
                { ru: 'Влажные полотенца на вентиляцию', uz: 'Ventilyatsiyaga nam sochiqlar', en: 'Wet towels on ventilation' },
                { ru: 'Немедленно обратитесь к врачу при любых симптомах', uz: "Har qanday alomatda darhol shifokorga murojaat qiling", en: 'Seek medical help immediately for any symptoms' }
            ],
            color: 'bg-rose-900'
        }
    };

    const level = aqiLevel || 'moderate';
    const rec = recommendations[level as keyof typeof recommendations] || recommendations.moderate;
    const lang = language as 'ru' | 'uz' | 'en';

    return (
        <div className="min-h-screen bg-gray-50 pb-20">
            {/* Header */}
            <div className={`${rec.color} text-white p-4`}>
                <div className="flex items-center gap-3 mb-4">
                    <button onClick={onBack} className="p-2 hover:bg-white/20 rounded-full transition-colors">
                        <ArrowLeft className="w-6 h-6" />
                    </button>
                    <h1 className="text-xl font-bold">{t('health_recommendations_title') || 'Рекомендации'}</h1>
                </div>
                <div className="text-center py-4">
                    <div className="text-6xl font-bold mb-2">{aqi}</div>
                    <div className="text-lg opacity-90">AQI</div>
                </div>
            </div>

            <div className="p-4 space-y-4">
                {/* Title & Description */}
                <div className="bg-white rounded-xl p-4 shadow-sm">
                    <h2 className="text-xl font-bold text-gray-900 mb-2">{rec.title[lang]}</h2>
                    <p className="text-gray-600">{rec.description[lang]}</p>
                </div>

                {/* Statistic Banner */}
                {'statistic' in rec && (
                    <div className="bg-gradient-to-r from-amber-50 to-red-50 border-l-4 border-red-400 rounded-xl p-3 shadow-sm">
                        <p className="text-sm font-semibold text-gray-800 leading-snug">
                            {(rec.statistic as { ru: string; uz: string; en: string })[lang]}
                        </p>
                    </div>
                )}

                {/* Health Risks */}
                {'risks' in rec && rec.risks && (
                    <div className="bg-white rounded-xl p-4 shadow-sm">
                        <div className="flex items-center gap-2 mb-3">
                            <AlertTriangle className="w-5 h-5 text-red-500" />
                            <h3 className="font-bold text-gray-900">{t('health_risks_title') || 'Риски для здоровья'}</h3>
                        </div>
                        <ul className="space-y-2">
                            {(rec.risks as Array<{ ru: string; uz: string; en: string }>).map((risk, i) => (
                                <li key={i} className="flex items-start gap-2 text-gray-700">
                                    <span className="w-2 h-2 bg-red-400 rounded-full mt-2 flex-shrink-0" />
                                    {risk[lang]}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}

                {/* Recommendations */}
                <div className="bg-white rounded-xl p-4 shadow-sm">
                    <div className="flex items-center gap-2 mb-3">
                        <Shield className="w-5 h-5 text-green-500" />
                        <h3 className="font-bold text-gray-900">{t('protective_measures') || 'Меры защиты'}</h3>
                    </div>
                    <ul className="space-y-2">
                        {rec.tips.map((tip, i) => (
                            <li key={i} className="flex items-start gap-2 text-gray-700">
                                <span className="w-2 h-2 bg-green-400 rounded-full mt-2 flex-shrink-0" />
                                {tip[lang]}
                            </li>
                        ))}
                    </ul>
                </div>

                {/* At-Risk Groups */}
                <div className="bg-white rounded-xl p-4 shadow-sm">
                    <div className="flex items-center gap-2 mb-3">
                        <Heart className="w-5 h-5 text-pink-500" />
                        <h3 className="font-bold text-gray-900">{t('at_risk_groups') || 'Группы риска'}</h3>
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                        <div className="flex items-center gap-2 text-gray-700">
                            <Baby className="w-4 h-4 text-blue-400" />
                            <span>{t('children') || 'Дети'}</span>
                        </div>
                        <div className="flex items-center gap-2 text-gray-700">
                            <User className="w-4 h-4 text-gray-400" />
                            <span>{t('elderly') || 'Пожилые'}</span>
                        </div>
                        <div className="flex items-center gap-2 text-gray-700">
                            <Wind className="w-4 h-4 text-cyan-400" />
                            <span>{t('asthma_patients') || 'Астматики'}</span>
                        </div>
                        <div className="flex items-center gap-2 text-gray-700">
                            <Activity className="w-4 h-4 text-red-400" />
                            <span>{t('heart_patients') || 'Сердечники'}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default HealthRecommendations;
