import React, { useState, useRef, useEffect } from 'react';
import { Wind, Shield, Leaf, ChevronDown } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

interface Props {
    onFinish: () => void;
}

const Onboarding: React.FC<Props> = ({ onFinish }) => {
    const [step, setStep] = useState(0);
    const [showLanguageDropdown, setShowLanguageDropdown] = useState(false);
    const { t, setLanguage, language } = useLanguage();
    const dropdownRef = useRef<HTMLDivElement>(null);

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setShowLanguageDropdown(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const steps = [
        {
            title: t('onboarding_1_title'),
            desc: t('onboarding_1_desc'),
            image: "https://images.unsplash.com/photo-1611273426858-450d8e3c9fce?auto=format&fit=crop&q=80&w=600",
            icon: <Wind size={48} className="text-[#EB5757]" />
        },
        {
            title: t('onboarding_2_title'),
            desc: t('onboarding_2_desc'),
            image: "https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?auto=format&fit=crop&q=80&w=600",
            icon: <Shield size={48} className="text-[#40A7E3]" />
        },
        {
            title: t('onboarding_3_title'),
            desc: t('onboarding_3_desc'),
            image: "https://images.unsplash.com/photo-1466692476868-aef1dfb1e735?auto=format&fit=crop&q=80&w=600",
            icon: <Leaf size={48} className="text-[#27AE60]" />
        }
    ];

    const current = steps[step];

    return (
        <div className="fixed inset-0 bg-white z-[200] flex flex-col">
            {/* Language Selection Dropdown */}
            {step === 0 && (
                <div className="absolute top-10 right-5 z-50" ref={dropdownRef}>
                    <button
                        onClick={() => setShowLanguageDropdown(!showLanguageDropdown)}
                        className="bg-white/80 backdrop-blur px-4 py-2 rounded-full shadow-sm text-sm font-bold text-[#1F2937] outline-none border border-[#E5E7EB] cursor-pointer flex items-center gap-2 hover:bg-white transition-colors"
                    >
                        <span>{language === 'uz' ? "O'zbek" : "Русский"}</span>
                        <ChevronDown size={16} className={`transition-transform ${showLanguageDropdown ? 'rotate-180' : ''}`} />
                    </button>

                    {/* Dropdown Menu */}
                    {showLanguageDropdown && (
                        <div className="absolute top-full mt-2 right-0 bg-[#4B5563] rounded-xl shadow-lg overflow-hidden min-w-[140px] animate-fade-in">
                            <button
                                onClick={() => {
                                    setLanguage('uz');
                                    setShowLanguageDropdown(false);
                                }}
                                className={`w-full px-4 py-3 text-left text-sm font-bold flex items-center gap-2 transition-colors ${
                                    language === 'uz' ? 'bg-[#4B5563] text-white' : 'bg-[#4B5563] text-white/70 hover:bg-[#374151]'
                                }`}
                            >
                                {language === 'uz' && <span className="text-white">✓</span>}
                                <span>O'zbek</span>
                            </button>
                            <button
                                onClick={() => {
                                    setLanguage('ru');
                                    setShowLanguageDropdown(false);
                                }}
                                className={`w-full px-4 py-3 text-left text-sm font-bold flex items-center gap-2 transition-colors ${
                                    language === 'ru' ? 'bg-[#4B5563] text-white' : 'bg-[#4B5563] text-white/70 hover:bg-[#374151]'
                                }`}
                            >
                                {language === 'ru' && <span className="text-white">✓</span>}
                                <span>Русский</span>
                            </button>
                        </div>
                    )}
                </div>
            )}

            <div className="relative h-[60%] bg-[#F3F4F6]">
                <img src={current.image} className="w-full h-full object-cover" alt="Onboarding" />
                <div className="absolute inset-0 bg-gradient-to-b from-transparent to-white"></div>
            </div>
            <div className="flex-1 px-8 pt-4 pb-10 flex flex-col items-center text-center relative z-10 -mt-10">
                <div className="mb-6 bg-white p-4 rounded-full shadow-button">
                    {current.icon}
                </div>
                <h2 className="text-2xl font-bold text-[#1F2937] mb-3">{current.title}</h2>
                <p className="text-sm text-[#4B5563] leading-relaxed mb-8">{current.desc}</p>

                <div className="mt-auto w-full space-y-4">
                    <div className="flex justify-center gap-2 mb-4">
                        {steps.map((_, i) => (
                            <div key={i} className={`h-2 rounded-full transition-all ${i === step ? 'w-8 bg-[#40A7E3]' : 'w-2 bg-[#E5E7EB]'}`} />
                        ))}
                    </div>
                    <button
                        onClick={() => {
                            if (step < steps.length - 1) setStep(step + 1);
                            else onFinish();
                        }}
                        className="w-full bg-main-gradient text-white py-4 btn-radius font-bold text-lg shadow-button active:scale-95 transition-transform"
                    >
                        {step === steps.length - 1 ? t('btn_start') : t('btn_next')}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Onboarding;
