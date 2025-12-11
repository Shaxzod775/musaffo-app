import React, { useState } from 'react';
import { Wallet, Heart } from 'lucide-react';
import { FundProject, UserState } from '../types';
import { useLanguage } from '../context/LanguageContext';
import ImageWithSkeleton from '../components/ImageWithSkeleton';

interface Props {
    user: UserState;
    projects: FundProject[];
    isLoadingProjects: boolean;
    simulateDonation: () => void; // Keep for direct CTA
    onProjectClick: (project: FundProject) => void;
}

const FundView: React.FC<Props> = ({ user, projects, isLoadingProjects, simulateDonation, onProjectClick }) => {
    const { t } = useLanguage();
    const [activeTab, setActiveTab] = useState<'active' | 'completed'>('active');

    const Header = ({ title, subtitle }: { title: string, subtitle?: string }) => (
        <div className="bg-main-gradient pt-10 pb-16 px-6 rounded-b-[30px] shadow-lg shadow-[#40A7E3]/20 relative overflow-hidden">
            <div className="absolute inset-0 opacity-10" style={{
                backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M30 0L60 30L30 60L0 30z' fill='%23ffffff'/%3E%3C/svg%3E")`
            }} />
            <div className="relative z-10 text-white">
                <h1 className="text-3xl font-bold tracking-tight">{title}</h1>
                {subtitle && <p className="text-sm opacity-90 font-medium">{subtitle}</p>}
            </div>
        </div>
    );

    const filteredProjects = projects.filter(p => {
        if (activeTab === 'active') return p.status === 'active';
        if (activeTab === 'completed') return p.status === 'completed';
        return false;
    });

    return (
        <div className="pb-32 animate-fade-in bg-[#F3F4F6] min-h-screen">
            <Header title={t('fund_page_title')} subtitle={t('fund_page_subtitle')} />

            <div className="px-5 -mt-8 relative z-20 space-y-4">
                {/* CTA Card */}
                <div className="bg-white card-radius p-4 shadow-soft text-center space-y-3">
                    <div className="mx-auto w-10 h-10 bg-[#27AE60]/10 rounded-full flex items-center justify-center text-[#27AE60]">
                        <Wallet size={20} />
                    </div>

                    {user.isContributor && user.totalDonated && user.totalDonated > 0 ? (
                        // Thank you message for donors
                        <div className="space-y-3">
                            <div className="bg-gradient-to-r from-[#27AE60]/10 to-[#40A7E3]/10 rounded-xl p-4 border border-[#27AE60]/20">
                                <p className="text-sm text-[#1F2937] font-semibold">
                                    {t('fund_thank_you', { amount: user.totalDonated.toLocaleString() })}
                                </p>
                            </div>
                            <button onClick={simulateDonation} className="w-full bg-[#27AE60] text-white py-2.5 btn-radius font-bold shadow-button active:scale-95 transition-transform text-sm">
                                {t('fund_cta_btn')}
                            </button>
                            <p className="text-[9px] text-[#9CA3AF]">Agrobank</p>
                        </div>
                    ) : (
                        // CTA for new donors
                        <div className="space-y-3">
                            <div>
                                <h3 className="font-bold text-base">{t('fund_cta_title')}</h3>
                                <p className="text-[10px] text-[#4B5563] mt-1 max-w-[200px] mx-auto">{t('fund_cta_desc')}</p>
                            </div>
                            <div className="grid grid-cols-3 gap-2">
                                {[5000, 10000, 50000].map(amount => (
                                    <button key={amount} onClick={simulateDonation} className="py-1.5 border border-[#E5E7EB] rounded-lg text-xs font-bold hover:border-[#27AE60] hover:text-[#27AE60] active:bg-[#27AE60] active:text-white transition-all">
                                        {(amount / 1000).toFixed(0)}k UZS
                                    </button>
                                ))}
                            </div>
                            <button onClick={simulateDonation} className="w-full bg-[#27AE60] text-white py-2.5 btn-radius font-bold shadow-button active:scale-95 transition-transform flex justify-center items-center gap-2 text-sm">
                                {t('fund_cta_btn')}
                            </button>
                            <p className="text-[9px] text-[#9CA3AF]">Agrobank</p>
                        </div>
                    )}
                </div>

                {/* Projects List */}
                <div>
                    <div className="flex items-center justify-between mb-4 px-1">
                        <h2 className="text-lg font-bold text-[#1F2937]">{t('fund_projects_title')}</h2>
                    </div>

                    {/* Tabs */}
                    <div className="flex bg-white p-1 rounded-xl shadow-sm mb-4">
                        <button
                            onClick={() => setActiveTab('active')}
                            className={`flex-1 py-2 rounded-lg text-xs font-bold transition-all ${activeTab === 'active' ? 'bg-[#27AE60] text-white shadow-md' : 'text-[#9CA3AF]'}`}
                        >
                            {t('fund_status_active')}
                        </button>
                        <button
                            onClick={() => setActiveTab('completed')}
                            className={`flex-1 py-2 rounded-lg text-xs font-bold transition-all ${activeTab === 'completed' ? 'bg-[#27AE60] text-white shadow-md' : 'text-[#9CA3AF]'}`}
                        >
                            {t('fund_status_completed')}
                        </button>
                    </div>

                    <div className="grid gap-5 lg:grid-cols-2">
                        {isLoadingProjects ? (
                            // Skeleton loader
                            <>
                                {[1, 2, 3].map(i => (
                                    <div key={i} className="bg-white shadow-soft rounded-2xl overflow-hidden animate-pulse">
                                        <div className="h-40 bg-[#E5E7EB]"></div>
                                        <div className="p-4 space-y-3">
                                            <div className="h-3 bg-[#E5E7EB] rounded w-3/4"></div>
                                            <div className="h-3 bg-[#E5E7EB] rounded w-full"></div>
                                            <div className="h-3 bg-[#E5E7EB] rounded w-2/3"></div>
                                            <div className="h-1.5 bg-[#E5E7EB] rounded w-full"></div>
                                        </div>
                                    </div>
                                ))}
                            </>
                        ) : filteredProjects.length === 0 ? (
                            <div className="text-center py-10 text-[#9CA3AF] text-sm font-medium">
                                {t('no_projects_found')}
                            </div>
                        ) : (
                            filteredProjects.map(p => {
                                const percent = Math.min(100, Math.round((p.currentAmount / p.targetAmount) * 100));
                                let statusLabel = t('fund_status_active');
                                if (p.status === 'completed') statusLabel = t('fund_status_completed');
                                if (p.status === 'voting') statusLabel = t('fund_status_voting');

                                // Calculate user's contribution - split total donation equally across all active projects
                                const activeProjectsCount = projects.filter(proj => proj.status === 'active').length;
                                const userContribution = user.totalDonated && activeProjectsCount > 0
                                    ? Math.floor(user.totalDonated / activeProjectsCount)
                                    : 0;

                                return (
                                    <div key={p.id} onClick={() => onProjectClick(p)} className="bg-white shadow-soft rounded-2xl overflow-hidden cursor-pointer active:scale-95 transition-transform">
                                        <div className="relative h-40 bg-[#F3F4F6]">
                                            <ImageWithSkeleton
                                                src={p.image}
                                                alt={p.title}
                                                className="w-full h-full object-cover"
                                            />
                                            <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
                                            <div className="absolute bottom-3 left-3 text-white">
                                                <div className="text-[10px] font-bold uppercase opacity-80 mb-1">{statusLabel}</div>
                                                <h3 className="font-bold leading-none">{p.titleKey ? t(p.titleKey) : p.title}</h3>
                                            </div>
                                        </div>
                                        <div className="p-4">
                                            <p className="text-xs text-[#4B5563] mb-4">{p.descKey ? t(p.descKey) : p.description}</p>

                                            {/* User's contribution info */}
                                            {userContribution > 0 && p.status === 'active' && (
                                                <div className="bg-[#27AE60]/5 border border-[#27AE60]/20 rounded-lg px-3 py-2 mb-3">
                                                    <p className="text-[10px] text-[#27AE60] font-semibold">
                                                        💚 {t('your_contribution')}: {userContribution.toLocaleString()} {t('fund_currency')}
                                                    </p>
                                                </div>
                                            )}

                                            <div className="flex justify-between text-xs font-semibold mb-2">
                                                <span className="text-[#27AE60] animate-counter">{percent}% {t('fund_collected_label')}</span>
                                                <span className="text-[#9CA3AF]">{t('fund_target_label')}: {(p.targetAmount / 1000000).toFixed(0)}M</span>
                                            </div>
                                            <div className="w-full bg-[#E5E7EB] rounded-full h-1.5">
                                                <div className="bg-[#27AE60] h-1.5 rounded-full animate-progress-bar" style={{ width: `${percent}%` }}></div>
                                            </div>
                                        </div>
                                    </div>
                                )
                            })
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default FundView;
