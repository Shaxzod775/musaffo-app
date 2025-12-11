import React, { useEffect } from 'react';
import { X, Wallet, CheckCircle, MapPin, Users } from 'lucide-react';
import { FundProject } from '../types';
import { useLanguage } from '../context/LanguageContext';

interface Props {
    project: FundProject;
    onClose: () => void;
    onDonate: () => void;
}

const ProjectDetail: React.FC<Props> = ({ project, onClose, onDonate }) => {
    const { t } = useLanguage();
    const percent = Math.min(100, Math.round((project.currentAmount / project.targetAmount) * 100));

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
            <div className="relative h-72 w-full shrink-0">
                <img
                    src={project.image}
                    className="w-full h-full object-cover"
                    alt={project.titleKey ? t(project.titleKey) : project.title}
                />
                <div className="absolute inset-0 bg-gradient-to-b from-black/50 via-transparent to-black/60"></div>
                <button
                    onClick={onClose}
                    className="absolute top-4 right-4 bg-black/20 backdrop-blur p-2 rounded-full text-white hover:bg-black/40 transition-colors"
                >
                    <X size={24} />
                </button>

                <div className="absolute bottom-6 left-6 right-6 text-white">
                    <div className="flex gap-2 mb-2">
                        <span className={`px-2 py-1 rounded-md text-[10px] font-bold uppercase ${project.status === 'completed' ? 'bg-[#27AE60]' : 'bg-[#40A7E3]'
                            }`}>
                            {project.status === 'completed' ? t('fund_status_completed') : t('fund_status_active')}
                        </span>
                    </div>
                    <h1 className="text-2xl font-bold leading-tight">{project.titleKey ? t(project.titleKey) : project.title}</h1>
                </div>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-6 bg-[#F9FAFB]">

                {/* Progress Card */}
                <div className="bg-white p-5 rounded-2xl shadow-sm border border-[#E5E7EB] mb-6">
                    <div className="flex justify-between items-end mb-2">
                        <div>
                            <p className="text-xs text-[#9CA3AF] font-bold uppercase">{t('fund_collected_label')}</p>
                            <p className="text-2xl font-bold text-[#27AE60]">{project.currentAmount.toLocaleString()} <span className="text-sm text-[#9CA3AF]">{t('fund_currency')}</span></p>
                        </div>
                        <div className="text-right">
                            <p className="text-xs text-[#9CA3AF] font-bold uppercase">{t('fund_target_label')}</p>
                            <p className="text-sm font-bold text-[#1F2937]">{(project.targetAmount / 1000000).toFixed(1)}M {t('fund_currency')}</p>
                        </div>
                    </div>
                    <div className="w-full bg-[#F3F4F6] rounded-full h-2.5 mb-4">
                        <div className="bg-[#27AE60] h-2.5 rounded-full transition-all duration-1000" style={{ width: `${percent}%` }}></div>
                    </div>
                    <div className="flex justify-between text-xs text-[#4B5563]">
                        <span className="flex items-center gap-1"><Users size={14} /> 1,240 {t('fund_collected')}</span>
                        <span>{percent}%</span>
                    </div>
                </div>

                {/* Description */}
                <div className="mb-8">
                    <h3 className="font-bold text-[#1F2937] mb-3">{t('initiative_about_title')}</h3>
                    <p className="text-sm text-[#4B5563] leading-relaxed mb-3">{project.descKey ? t(project.descKey) : project.description}</p>
                    {project.detailKey && (
                        <p className="text-sm text-[#4B5563] leading-relaxed">
                            {t(project.detailKey)}
                        </p>
                    )}
                </div>

                {/* Completed Report (if completed) */}
                {project.status === 'completed' && (
                    <div className="mb-8">
                        <h3 className="font-bold text-[#1F2937] mb-3 flex items-center gap-2">
                            <CheckCircle className="text-[#27AE60]" size={20} /> {t('fund_report')}
                        </h3>
                        <div className="grid grid-cols-2 gap-2">
                            <img src="https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?auto=format&fit=crop&q=80&w=300" className="rounded-xl h-24 object-cover" />
                            <img src="https://images.unsplash.com/photo-1466692476868-aef1dfb1e735?auto=format&fit=crop&q=80&w=300" className="rounded-xl h-24 object-cover" />
                        </div>
                        <p className="text-xs text-[#4B5563] mt-2 italic">
                            {t('project_mirabad_desc')}
                        </p>
                    </div>
                )}
            </div>

            {/* Footer CTA */}
            {project.status !== 'completed' && (
                <div className="p-4 border-t border-[#E5E7EB] bg-white pb-safe">
                    <button
                        onClick={onDonate}
                        className="w-full bg-[#27AE60] text-white py-3.5 rounded-xl font-bold flex items-center justify-center gap-2 shadow-button active:scale-95 transition-all"
                    >
                        <Wallet size={20} /> {t('fund_cta_btn')}
                    </button>
                </div>
            )}
        </div>
    );
};

export default ProjectDetail;
