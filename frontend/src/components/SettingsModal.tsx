import React, { useState } from 'react';
import { X, Globe, ChevronRight, Bell, Shield, Play } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useLanguage } from '../context/LanguageContext';
import PrivacyModal from './PrivacyModal';

interface Props {
    onClose: () => void;
}

const SettingsModal: React.FC<Props> = ({ onClose }) => {
    const { language, setLanguage, t } = useLanguage();
    const navigate = useNavigate();
    const [showPrivacy, setShowPrivacy] = useState(false);

    const languages = [
        { code: 'uz', label: "O'zbekcha", flag: '🇺🇿' },
        { code: 'ru', label: 'Русский', flag: '🇷🇺' },
        { code: 'en', label: 'English', flag: '🇬🇧' }
    ];

    if (showPrivacy) {
        return <PrivacyModal onClose={() => setShowPrivacy(false)} />;
    }

    return (
        <div className="fixed inset-0 z-[100] bg-white flex flex-col animate-slide-up">
            {/* Header */}
            <div className="px-6 py-4 border-b border-[#F3F4F6] flex items-center justify-between bg-white sticky top-0 z-10">
                <h2 className="text-xl font-bold text-[#1F2937]">{t('settings_title')}</h2>
                <button onClick={onClose} className="p-2 bg-[#F3F4F6] rounded-full hover:bg-[#E5E7EB]">
                    <X size={20} />
                </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6 bg-[#F9FAFB]">

                {/* Language Section */}
                <div className="bg-white rounded-2xl p-4 shadow-sm border border-[#E5E7EB] mb-6">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="w-8 h-8 bg-[#40A7E3]/10 rounded-full flex items-center justify-center text-[#40A7E3]">
                            <Globe size={18} />
                        </div>
                        <h3 className="font-bold text-[#1F2937]">{t('settings_language')}</h3>
                    </div>
                    <div className="space-y-2">
                        {languages.map(lang => (
                            <button
                                key={lang.code}
                                onClick={() => setLanguage(lang.code as 'uz' | 'ru' | 'en')}
                                className={`w-full flex items-center justify-between p-3 rounded-xl transition-all ${language === lang.code
                                    ? 'bg-[#27AE60]/10 border border-[#27AE60] text-[#27AE60]'
                                    : 'bg-[#F3F4F6] border border-transparent text-[#4B5563]'
                                    }`}
                            >
                                <span className="font-bold flex items-center gap-2">
                                    <span className="text-lg">{lang.flag}</span> {lang.label}
                                </span>
                                {language === lang.code && <div className="w-3 h-3 bg-[#27AE60] rounded-full shadow-sm" />}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Other Settings (Mock) */}
                <div className="bg-white rounded-2xl shadow-sm border border-[#E5E7EB] overflow-hidden">
                    <button
                        onClick={() => {
                            onClose();
                            navigate('/demo');
                        }}
                        className="w-full flex items-center justify-between p-4 border-b border-[#F3F4F6] hover:bg-[#F9FAFB] transition-colors"
                    >
                        <div className="flex items-center gap-3">
                            <Play size={20} className="text-[#40A7E3]" />
                            <span className="font-bold text-[#1F2937]">{t('settings_demo')}</span>
                        </div>
                        <ChevronRight size={20} className="text-[#9CA3AF]" />
                    </button>
                    <button
                        onClick={() => setShowPrivacy(true)}
                        className="w-full flex items-center justify-between p-4 hover:bg-[#F9FAFB]"
                    >
                        <div className="flex items-center gap-3">
                            <Shield size={20} className="text-[#9CA3AF]" />
                            <span className="font-bold text-[#1F2937]">{t('settings_privacy')}</span>
                        </div>
                        <ChevronRight size={20} className="text-[#9CA3AF]" />
                    </button>
                </div>

                <p className="text-center text-xs text-[#9CA3AF] mt-8">
                    Musaffo App v1.0.0 (Hackathon Build)
                </p>
            </div>
        </div>
    );
};

export default SettingsModal;
