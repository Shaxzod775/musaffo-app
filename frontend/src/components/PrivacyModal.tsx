import React from 'react';
import { X } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

interface Props {
    onClose: () => void;
}

const PrivacyModal: React.FC<Props> = ({ onClose }) => {
    const { t } = useLanguage();

    return (
        <div className="fixed inset-0 z-[110] bg-white flex flex-col animate-slide-up">
            {/* Header */}
            <div className="px-6 py-4 border-b border-[#F3F4F6] flex items-center justify-between bg-white sticky top-0 z-10">
                <h2 className="text-xl font-bold text-[#1F2937]">{t('settings_privacy')}</h2>
                <button onClick={onClose} className="p-2 bg-[#F3F4F6] rounded-full hover:bg-[#E5E7EB]">
                    <X size={20} />
                </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6 bg-[#F9FAFB]">
                <div className="bg-white rounded-2xl p-6 shadow-sm border border-[#E5E7EB]">
                    <h3 className="text-lg font-bold text-[#1F2937] mb-4">
                        {t('settings_privacy')}
                    </h3>

                    <div className="space-y-4 text-[#4B5563]">
                        <section>
                            <h4 className="font-bold text-[#1F2937] mb-2">1. {t('privacy_section_1_title')}</h4>
                            <p className="text-sm">
                                {t('privacy_section_1_text')}
                            </p>
                        </section>

                        <section>
                            <h4 className="font-bold text-[#1F2937] mb-2">2. {t('privacy_section_2_title')}</h4>
                            <p className="text-sm">
                                {t('privacy_section_2_text')}
                            </p>
                        </section>

                        <section>
                            <h4 className="font-bold text-[#1F2937] mb-2">3. {t('privacy_section_3_title')}</h4>
                            <p className="text-sm">
                                {t('privacy_section_3_text')}
                            </p>
                        </section>

                        <section>
                            <h4 className="font-bold text-[#1F2937] mb-2">4. {t('privacy_section_4_title')}</h4>
                            <p className="text-sm">
                                {t('privacy_section_4_text')}
                            </p>
                        </section>

                        <section>
                            <h4 className="font-bold text-[#1F2937] mb-2">5. {t('privacy_section_5_title')}</h4>
                            <p className="text-sm">
                                {t('privacy_section_5_text')}
                            </p>
                        </section>
                    </div>
                </div>

                <p className="text-center text-xs text-[#9CA3AF] mt-8">
                    {t('privacy_last_updated')}
                </p>
            </div>
        </div>
    );
};

export default PrivacyModal;
