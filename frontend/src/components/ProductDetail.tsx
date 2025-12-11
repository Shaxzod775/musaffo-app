import React, { useEffect } from 'react';
import { X, ShoppingBag, Leaf, ShieldCheck } from 'lucide-react';
import { EcoProduct } from '../types';
import { useLanguage } from '../context/LanguageContext';
import { formatNumber } from '../utils/formatNumber';
import ImageWithSkeleton from './ImageWithSkeleton';

interface Props {
    product: EcoProduct;
    onClose: () => void;
    onBuy: () => void;
}

const ProductDetail: React.FC<Props> = ({ product, onClose, onBuy }) => {
    const { t } = useLanguage();

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
            <div className="relative h-[40vh] w-full shrink-0 bg-[#F3F4F6]">
                <ImageWithSkeleton
                    src={product.image}
                    className="w-full h-full object-cover"
                    alt={t(product.name as any)}
                />
                <button
                    onClick={onClose}
                    className="absolute top-4 right-4 bg-white/50 backdrop-blur p-2 rounded-full text-[#1F2937] hover:bg-white transition-colors"
                >
                    <X size={24} />
                </button>

                <div className="absolute bottom-4 left-4 right-4 sm:right-auto bg-gradient-to-r from-[#27AE60] to-[#219653] text-white px-4 py-2 rounded-xl text-sm font-bold flex items-center justify-center sm:justify-start gap-2 shadow-lg backdrop-blur-sm">
                    <Leaf size={16} /> {t('product_cashback', { percent: product.fundContributionPercent })}
                </div>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-6 -mt-6 bg-white rounded-t-[30px] relative z-10">
                <div className="w-12 h-1.5 bg-[#E5E7EB] rounded-full mx-auto mb-6" />

                <div className="flex justify-between items-start mb-2">
                    <div>
                        <span className="text-xs font-bold text-[#9CA3AF] uppercase tracking-wider">{product.category}</span>
                        <h1 className="text-2xl font-bold text-[#1F2937] leading-tight mt-1">{t(product.name as any)}</h1>
                    </div>
                    <div className="text-right">
                        <p className="text-xl font-bold text-[#40A7E3]">{formatNumber(product.price)}</p>
                        <p className="text-xs text-[#9CA3AF]">{t('currency_sum')}</p>
                    </div>
                </div>

                <div className="flex items-center gap-2 text-xs text-[#27AE60] font-bold mb-6 bg-[#27AE60]/10 p-3 rounded-xl">
                    <ShieldCheck size={16} />
                    <span>{t('product_verified')}</span>
                </div>

                <div className="prose prose-sm text-[#4B5563]">
                    <h3 className="text-[#1F2937] font-bold mb-2">{t('product_about_title')}</h3>
                    <p className="leading-relaxed">
                        {t(`${product.name}_detail` as any) || t('product_about_description')}
                    </p>
                    <ul className="mt-4 space-y-2">
                        <li>• {t('product_feature_original')}</li>
                        <li>• {t('product_feature_warranty')}</li>
                        <li>• {t('product_feature_delivery')}</li>
                    </ul>
                </div>
            </div>

            {/* Footer CTA */}
            <div className="p-4 border-t border-[#E5E7EB] bg-white pb-safe flex gap-4 items-center">
                <div className="flex-1">
                    <p className="text-xs text-[#9CA3AF]">{t('product_total_amount')}</p>
                    <p className="text-xl font-bold text-[#1F2937]">{formatNumber(product.price)} {t('currency_sum')}</p>
                </div>
                <button
                    onClick={onBuy}
                    className="flex-[2] bg-[#1F2937] text-white py-3.5 rounded-xl font-bold flex items-center justify-center gap-2 shadow-lg active:scale-95 transition-all"
                >
                    <ShoppingBag size={20} /> {t('btn_buy')}
                </button>
            </div>
        </div>
    );
};

export default ProductDetail;
