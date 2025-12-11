import React from 'react';
import { Play, ExternalLink, ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useLanguage } from '../context/LanguageContext';

const DemoView: React.FC = () => {
    const navigate = useNavigate();
    const { t } = useLanguage();

    return (
        <div className="min-h-screen bg-[#F3F4F6] pb-20">
            {/* Header */}
            <div className="bg-main-gradient pt-10 pb-16 px-6 rounded-b-[30px] shadow-lg shadow-[#40A7E3]/20 relative overflow-hidden">
                <div className="absolute inset-0 opacity-10" style={{
                    backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M30 0L60 30L30 60L0 30z' fill='%23ffffff'/%3E%3C/svg%3E")`
                }} />
                <div className="relative z-10 flex items-center gap-4">
                    <button
                        onClick={() => navigate('/')}
                        className="p-2 bg-white/20 backdrop-blur rounded-full text-white hover:bg-white/30 transition-colors"
                    >
                        <ArrowLeft size={24} />
                    </button>
                    <div className="text-white">
                        <h1 className="text-3xl font-bold tracking-tight">{t('demo_title')}</h1>
                        <p className="text-sm opacity-90 font-medium">{t('demo_subtitle')}</p>
                    </div>
                </div>
            </div>

            <div className="px-5 -mt-10 relative z-20 space-y-6 max-w-4xl mx-auto">
                {/* Demo Video Section */}
                <div className="bg-white card-radius shadow-soft overflow-hidden">
                    <div className="aspect-video bg-gradient-to-br from-[#40A7E3] to-[#27AE60] relative flex items-center justify-center">
                        {/* Mock Video Player */}
                        <div className="absolute inset-0 bg-black/20 backdrop-blur-sm flex items-center justify-center">
                            <div className="text-center">
                                <div className="w-20 h-20 bg-white/30 backdrop-blur rounded-full flex items-center justify-center mb-4 mx-auto hover:bg-white/40 transition-all cursor-pointer">
                                    <Play size={32} className="text-white fill-white ml-1" />
                                </div>
                                <p className="text-white font-bold text-lg">{t('demo_video_title')}</p>
                                <p className="text-white/80 text-sm">{t('demo_video_duration')}</p>
                            </div>
                        </div>
                        {/* Placeholder Image */}
                        <img
                            src="https://images.unsplash.com/photo-1611273426858-450d8e3c9fce?auto=format&fit=crop&q=80&w=1200"
                            alt="Demo Preview"
                            className="w-full h-full object-cover opacity-40"
                        />
                    </div>
                    <div className="p-6">
                        <div className="flex items-center gap-2 mb-2">
                            <div className="w-2 h-2 bg-[#EB5757] rounded-full animate-pulse" />
                            <span className="text-xs font-bold text-[#9CA3AF] uppercase">{t('demo_video_label')}</span>
                        </div>
                        <h2 className="text-xl font-bold text-[#1F2937] mb-2">{t('demo_video_title')}</h2>
                        <p className="text-sm text-[#4B5563] leading-relaxed">
                            {t('demo_video_desc')}
                        </p>
                    </div>
                </div>

                {/* Description Section */}
                <div className="bg-white card-radius p-6 shadow-soft">
                    <h3 className="text-lg font-bold text-[#1F2937] mb-4 flex items-center gap-2">
                        <div className="w-1 h-6 bg-main-gradient rounded-full" />
                        {t('demo_about_title')}
                    </h3>
                    <div className="space-y-4 text-sm text-[#4B5563] leading-relaxed">
                        <p>
                            <strong className="text-[#1F2937]">Musaffo</strong> {t('demo_about_intro')}
                        </p>
                        <div>
                            <p className="font-bold text-[#1F2937] mb-2">{t('demo_features_title')}</p>
                            <ul className="space-y-2 ml-4">
                                <li className="flex items-start gap-2">
                                    <span className="text-[#27AE60] font-bold">✓</span>
                                    <span><strong>{t('demo_feature_aqi_title')}</strong> {t('demo_feature_aqi_desc')}</span>
                                </li>
                                <li className="flex items-start gap-2">
                                    <span className="text-[#27AE60] font-bold">✓</span>
                                    <span><strong>{t('demo_feature_fund_title')}</strong> {t('demo_feature_fund_desc')}</span>
                                </li>
                                <li className="flex items-start gap-2">
                                    <span className="text-[#27AE60] font-bold">✓</span>
                                    <span><strong>{t('demo_feature_market_title')}</strong> {t('demo_feature_market_desc')}</span>
                                </li>
                                <li className="flex items-start gap-2">
                                    <span className="text-[#27AE60] font-bold">✓</span>
                                    <span><strong>{t('demo_feature_community_title')}</strong> {t('demo_feature_community_desc')}</span>
                                </li>
                                <li className="flex items-start gap-2">
                                    <span className="text-[#27AE60] font-bold">✓</span>
                                    <span><strong>{t('demo_feature_ai_title')}</strong> {t('demo_feature_ai_desc')}</span>
                                </li>
                            </ul>
                        </div>
                        <p>
                            {t('demo_about_conclusion')}
                        </p>
                    </div>
                </div>

                {/* Technical Highlights */}
                <div className="bg-white card-radius p-6 shadow-soft">
                    <h3 className="text-lg font-bold text-[#1F2937] mb-4 flex items-center gap-2">
                        <div className="w-1 h-6 bg-main-gradient rounded-full" />
                        {t('demo_tech_title')}
                    </h3>
                    <div className="grid grid-cols-2 gap-4">
                        <div className="bg-[#F9FAFB] p-4 rounded-xl">
                            <p className="text-xs font-bold text-[#9CA3AF] uppercase mb-1">{t('demo_tech_frontend')}</p>
                            <p className="text-sm font-bold text-[#1F2937]">React + TypeScript</p>
                        </div>
                        <div className="bg-[#F9FAFB] p-4 rounded-xl">
                            <p className="text-xs font-bold text-[#9CA3AF] uppercase mb-1">{t('demo_tech_ai')}</p>
                            <p className="text-sm font-bold text-[#1F2937]">OpenAI API</p>
                        </div>
                        <div className="bg-[#F9FAFB] p-4 rounded-xl">
                            <p className="text-xs font-bold text-[#9CA3AF] uppercase mb-1">{t('demo_tech_styling')}</p>
                            <p className="text-sm font-bold text-[#1F2937]">Tailwind CSS</p>
                        </div>
                        <div className="bg-[#F9FAFB] p-4 rounded-xl">
                            <p className="text-xs font-bold text-[#9CA3AF] uppercase mb-1">{t('demo_tech_dataviz')}</p>
                            <p className="text-sm font-bold text-[#1F2937]">Recharts</p>
                        </div>
                    </div>
                </div>

                {/* Working Prototype Link */}
                <div className="bg-gradient-to-br from-[#40A7E3] to-[#27AE60] card-radius p-6 shadow-button text-white">
                    <h3 className="text-lg font-bold mb-2 flex items-center gap-2">
                        <ExternalLink size={20} />
                        {t('demo_prototype_title')}
                    </h3>
                    <p className="text-sm text-white/90 mb-4">
                        {t('demo_prototype_desc')}
                    </p>
                    <button
                        onClick={() => navigate('/')}
                        className="w-full bg-white/20 backdrop-blur hover:bg-white/30 py-3 rounded-xl text-sm font-bold border border-white/20 flex items-center justify-center gap-2 transition-all active:scale-95"
                    >
                        <Play size={16} />
                        {t('demo_prototype_btn')}
                    </button>
                </div>

                {/* Contact Section */}
                <div className="bg-white card-radius p-6 shadow-soft text-center">
                    <p className="text-xs text-[#9CA3AF] mb-2">{t('demo_built_for')}</p>
                    <p className="text-sm font-bold text-[#1F2937]">Musaffo v1.0.0</p>
                    <p className="text-xs text-[#4B5563] mt-2">
                        {t('demo_inquiries')} <a href="mailto:info@musaffo.uz" className="text-[#40A7E3] hover:underline">info@musaffo.uz</a>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default DemoView;
