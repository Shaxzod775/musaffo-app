import React from 'react';
import { Wind, Droplets, Thermometer, Wallet, ArrowRight, Settings, ChevronRight, Leaf } from 'lucide-react';
import AirQualityGauge from '../components/AirQualityGauge';
import CasinoCounter from '../components/CasinoCounter';
import { AirQualityData, NewsItem, Tab } from '../types';
import { useLanguage } from '../context/LanguageContext';

interface Stats {
    totalDonations: number;
    totalDonors: number;
    totalProjects: number;
    activeProjects: number;
}

interface Props {
    aqiData: AirQualityData;
    aqiLoading?: boolean;
    news: NewsItem[];
    newsLoading?: boolean;
    stats?: Stats;
    statsLoading?: boolean;
    setActiveTab: (tab: Tab) => void;
    onNewsClick: (news: NewsItem) => void;
    onDonateClick: () => void;
    onSettingsClick: () => void;
    onHealthRecommendationsClick?: () => void;
}

const HomeView: React.FC<Props> = ({
    aqiData,
    aqiLoading = false,
    news,
    newsLoading = false,
    stats,
    statsLoading = false,
    setActiveTab,
    onNewsClick,
    onDonateClick,
    onSettingsClick,
    onHealthRecommendationsClick
}) => {
    const { t } = useLanguage();

    // Format number with spaces (1 000 000)
    // const formatNumber = (num: number): string => {
    //     return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
    // };

    const Header = ({ title, subtitle, rightElement }: { title: string, subtitle?: string, rightElement?: React.ReactNode }) => (
        <div className="bg-main-gradient pt-10 pb-16 px-6 rounded-b-[30px] shadow-lg shadow-[#40A7E3]/20 relative overflow-hidden">
            <div className="absolute inset-0 opacity-10" style={{
                backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M30 0L60 30L30 60L0 30z' fill='%23ffffff'/%3E%3C/svg%3E")`
            }} />
            <div className="relative z-10 flex justify-between items-start">
                <div className="text-white">
                    <h1 className="text-3xl font-bold tracking-tight">{title}</h1>
                    {subtitle && <p className="text-sm opacity-90 font-medium">{subtitle}</p>}
                </div>
                {rightElement}
            </div>
        </div>
    );

    return (
        <div className="pb-32 animate-fade-in bg-[#F3F4F6] min-h-screen relative">
            <Header
                title={t('home_greeting')}
                subtitle={t('home_subtitle')}
                rightElement={
                    <button onClick={onSettingsClick} className="p-2 bg-white/20 backdrop-blur rounded-full text-white hover:bg-white/30 transition-colors">
                        <Settings size={24} />
                    </button>
                }
            />

            <div className="px-5 -mt-10 relative z-20 space-y-6">
                {/* Desktop Layout - AQI and Fund side by side */}
                <div className="lg:grid lg:grid-cols-2 lg:gap-6 space-y-6 lg:space-y-0">
                    {/* AQI Widget */}
                    <AirQualityGauge
                        data={aqiData}
                        isLoading={aqiLoading}
                        onRecommendationsClick={onHealthRecommendationsClick}
                    />

                    {/* Fund Widget */}
                    <div onClick={() => setActiveTab('fund')} className="cursor-pointer group h-full flex flex-col">
                        <div className="flex justify-between items-end mb-3 px-1 lg:hidden">
                            <h2 className="text-lg font-bold text-[#1F2937]">{t('fund_widget_title')}</h2>
                            <span className="text-[#40A7E3] text-xs font-bold flex items-center group-hover:underline">{t('fund_report')} <ChevronRight size={14} /></span>
                        </div>
                        <div className="bg-gradient-to-br from-[#27AE60] to-[#219653] card-radius p-6 text-white shadow-button relative overflow-hidden transition-transform active:scale-95 flex-1 flex flex-col justify-center">
                            <div className="absolute top-0 right-0 p-4 opacity-10 transform translate-x-4 -translate-y-4 rotate-12">
                                <Leaf size={140} />
                            </div>
                            <div className="relative z-10 text-center w-full">
                                <p className="text-white/90 text-base font-bold uppercase tracking-widest mb-3">{t('fund_collected')}</p>
                                <div className="mb-4 flex justify-center">
                                    <div className="relative inline-block">
                                        <h3 className="font-bold tracking-tight text-5xl sm:text-5xl lg:text-5xl">
                                            <span className="whitespace-nowrap">
                                                {statsLoading || !stats || stats.totalDonations === 0 ? (
                                                    <span className="opacity-50">0</span>
                                                ) : (
                                                    <CasinoCounter
                                                        value={stats.totalDonations}
                                                        isLoading={statsLoading}
                                                    />
                                                )}
                                            </span>
                                        </h3>
                                        <span className="absolute bottom-0 right-0 translate-x-full pl-1 text-sm font-medium opacity-80">{t('fund_currency')}</span>
                                    </div>
                                </div>

                                <button onClick={onDonateClick} className="w-full bg-white/20 backdrop-blur hover:bg-white/30 py-3 rounded-xl text-xs font-bold border border-white/20 flex items-center justify-center gap-2">
                                    <Wallet size={16} /> {t('btn_contribute')}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                {/* News Feed */}
                <div>
                    <h2 className="text-lg font-bold text-[#1F2937] mb-3 px-1">{t('news_title')}</h2>
                    <div className="space-y-4 lg:grid lg:grid-cols-2 lg:gap-4 lg:space-y-0">
                        {newsLoading ? (
                            // Skeleton loading
                            [...Array(4)].map((_, index) => (
                                <div key={index} className="bg-white p-5 card-radius shadow-soft flex flex-col gap-3 animate-pulse">
                                    <div className="flex justify-between items-start">
                                        <div className="bg-[#E5E7EB] h-5 w-16 rounded-md"></div>
                                        <div className="bg-[#E5E7EB] h-3 w-20 rounded"></div>
                                    </div>
                                    <div className="bg-[#E5E7EB] h-4 w-full rounded"></div>
                                    <div className="bg-[#E5E7EB] h-4 w-3/4 rounded"></div>
                                    <div className="space-y-2">
                                        <div className="bg-[#E5E7EB] h-3 w-full rounded"></div>
                                        <div className="bg-[#E5E7EB] h-3 w-5/6 rounded"></div>
                                    </div>
                                </div>
                            ))
                        ) : (
                            news.map(item => (
                                <div key={item.id} onClick={() => onNewsClick(item)} className="bg-white p-5 card-radius shadow-soft flex flex-col gap-3 active:bg-gray-50 transition-colors cursor-pointer hover:shadow-md">
                                    <div className="flex justify-between items-start">
                                        <span className="bg-[#40A7E3]/10 text-[#40A7E3] px-2 py-1 rounded-md text-[10px] font-bold uppercase">{item.tag}</span>
                                        <span className="text-[#9CA3AF] text-[10px]">{item.time}</span>
                                    </div>
                                    <h3 className="font-bold text-[#1F2937] text-sm leading-snug">{item.title}</h3>
                                    <p className="text-xs text-[#4B5563] leading-relaxed">{item.summary}</p>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default HomeView;

