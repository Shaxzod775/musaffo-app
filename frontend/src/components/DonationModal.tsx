import React, { useState } from 'react';
import { X, Wallet, CheckCircle, Loader2, Heart } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';
import { formatNumber } from '../utils/formatNumber';

interface Props {
    onClose: () => void;
    onDonate: (amount: number) => void;
    isRepeatDonor?: boolean;
    previousAmount?: number;
}

const DonationModal: React.FC<Props> = ({ onClose, onDonate, isRepeatDonor = false, previousAmount = 0 }) => {
    const { t } = useLanguage();
    const [amount, setAmount] = useState<string>('');
    const [isProcessing, setIsProcessing] = useState(false);
    const [isSuccess, setIsSuccess] = useState(false);

    const presets = [5000, 10000, 50000, 100000];

    const handleDonate = () => {
        if (!amount) return;
        setIsProcessing(true);
        setTimeout(() => {
            setIsProcessing(false);
            setIsSuccess(true);
            onDonate(Number(amount));
            setTimeout(() => {
                onClose();
            }, 2000);  // Show success for 2 seconds
        }, 1500);
    };

    return (
        <div className="fixed inset-0 z-[100] flex items-end sm:items-center justify-center bg-black/50 backdrop-blur-sm animate-fade-in">
            <div className="bg-white w-full max-w-md rounded-t-[30px] sm:rounded-[30px] p-6 animate-slide-up">

                {/* Header */}
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-xl font-bold text-[#1F2937]">
                        {isRepeatDonor ? t('donation_repeat_title') : t('fund_cta_title')}
                    </h2>
                    <button onClick={onClose} className="p-2 bg-[#F3F4F6] rounded-full hover:bg-[#E5E7EB]">
                        <X size={20} />
                    </button>
                </div>

                {/* Repeat Donor Message */}
                {isRepeatDonor && (
                    <div className="mb-6 p-4 bg-gradient-to-r from-[#27AE60]/10 to-[#40A7E3]/10 rounded-xl border border-[#27AE60]/20 animate-fade-in">
                        <div className="flex items-start gap-3">
                            <div className="w-10 h-10 bg-[#27AE60]/20 rounded-full flex items-center justify-center flex-shrink-0">
                                <Heart
                                    size={20}
                                    className="text-[#27AE60] animate-heartbeat"
                                    fill="#27AE60"
                                />
                            </div>
                            <div>
                                <p className="text-sm text-[#1F2937] font-semibold mb-1">
                                    {t('donation_repeat_message', { amount: formatNumber(previousAmount) })}
                                </p>
                                <p className="text-xs text-[#4B5563]">
                                    {t('donation_repeat_question')}
                                </p>
                            </div>
                        </div>
                    </div>
                )}

                {isSuccess ? (
                    <div className="flex flex-col items-center py-10 text-center animate-fade-in">
                        <div className="w-20 h-20 bg-[#27AE60]/10 rounded-full flex items-center justify-center text-[#27AE60] mb-4">
                            <CheckCircle size={40} />
                        </div>
                        <h3 className="text-2xl font-bold text-[#1F2937] mb-2">{t('donation_success_title')}</h3>
                        <p className="text-[#4B5563]">{t('donation_success_message')}</p>
                    </div>
                ) : (
                    <>
                        {/* Presets */}
                        <div className="grid grid-cols-2 gap-3 mb-6">
                            {presets.map(preset => (
                                <button
                                    key={preset}
                                    onClick={() => setAmount(preset)}
                                    className={`py-3 rounded-xl font-bold text-sm transition-all ${amount === preset
                                        ? 'bg-[#27AE60] text-white shadow-lg shadow-[#27AE60]/30'
                                        : 'bg-[#F3F4F6] text-[#4B5563] hover:bg-[#E5E7EB]'
                                        }`}
                                >
                                    {formatNumber(preset)} UZS
                                </button>
                            ))}
                        </div>

                        {/* Custom Amount */}
                        <div className="mb-6">
                            <label className="text-xs font-bold text-[#9CA3AF] uppercase mb-2 block">{t('donation_custom_amount')}</label>
                            <div className="relative">
                                <input
                                    type="number"
                                    value={amount}
                                    onChange={(e) => setAmount(Number(e.target.value))}
                                    placeholder="0"
                                    className="w-full bg-[#F3F4F6] rounded-xl py-4 pl-4 pr-16 text-lg font-bold text-[#1F2937] outline-none focus:ring-2 focus:ring-[#27AE60]/20 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                                />
                                <span className="absolute right-4 top-1/2 -translate-y-1/2 text-[#9CA3AF] font-bold">UZS</span>
                            </div>
                        </div>

                        {/* Pay Button */}
                        <button
                            onClick={handleDonate}
                            disabled={!amount || isProcessing}
                            className="w-full bg-[#27AE60] text-white py-4 rounded-xl font-bold text-lg shadow-button active:scale-95 transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:shadow-none"
                        >
                            {isProcessing ? <Loader2 className="animate-spin" /> : <Wallet size={20} />}
                            {isProcessing ? t('toast_processing_payment') : t('donation_pay_button')}
                        </button>
                    </>
                )}
            </div>
        </div>
    );
};

export default DonationModal;
