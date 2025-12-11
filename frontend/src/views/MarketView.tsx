import React, { useState } from 'react';
import { Leaf } from 'lucide-react';
import { EcoProduct } from '../types';
import { useLanguage } from '../context/LanguageContext';
import ImageWithSkeleton from '../components/ImageWithSkeleton';

interface Props {
    products: EcoProduct[];
    simulatePurchase: (amount: number) => void; // Keep for direct buy
    onProductClick: (product: EcoProduct) => void;
}

const MarketView: React.FC<Props> = ({ products, simulatePurchase, onProductClick }) => {
    const { t } = useLanguage();
    const [selectedCategory, setSelectedCategory] = useState<string>('all');

    const categories = [
        { key: 'all', label: t('market_cat_all') },
        { key: 'Purifier', label: t('market_cat_purifier') },
        { key: 'Mask', label: t('market_cat_mask') },
        { key: 'Plants', label: t('market_cat_plants') }
    ];

    // Filter products based on selected category
    const filteredProducts = selectedCategory === 'all'
        ? products
        : products.filter(p => p.category === selectedCategory);

    return (
        <div className="pb-32 animate-fade-in bg-[#F3F4F6] min-h-screen">
            <div className="sticky top-0 bg-white/90 backdrop-blur-xl z-30 pt-12 pb-4 px-5 border-b border-[#E5E7EB]">
                <div className="mb-4">
                    <h1 className="text-2xl font-bold text-[#1F2937]">{t('market_title')}</h1>
                    <p className="text-xs text-[#4B5563]">{t('market_subtitle')}</p>
                </div>
                {/* Categories */}
                <div className="flex gap-2 overflow-x-auto no-scrollbar pb-1">
                    {categories.map((cat) => (
                        <button
                            key={cat.key}
                            onClick={() => setSelectedCategory(cat.key)}
                            className={`px-4 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition-all ${selectedCategory === cat.key ? 'bg-[#1F2937] text-white shadow-lg' : 'bg-white text-[#4B5563] border border-[#E5E7EB] hover:border-[#1F2937]'}`}
                        >
                            {cat.label}
                        </button>
                    ))}
                </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 px-5 pt-6 pb-4">
                {filteredProducts.length === 0 ? (
                    <div className="col-span-2 text-center py-12 text-[#9CA3AF]">
                        <p className="text-sm font-medium">
                            {t('no_products_found') || 'Товары не найдены'}
                        </p>
                    </div>
                ) : (
                    filteredProducts.map(product => (
                        <div key={product.id} onClick={() => onProductClick(product)} className="bg-white p-3 card-radius shadow-soft border border-transparent active:border-[#40A7E3] active:scale-95 transition-all flex flex-col group cursor-pointer">
                            <div className="aspect-square bg-[#F3F4F6] rounded-[16px] mb-3 relative overflow-hidden">
                                <ImageWithSkeleton
                                    src={product.image}
                                    alt={t(product.name as any)}
                                    className="w-full h-full object-cover"
                                />
                                <div className="absolute top-2 left-2 bg-[#27AE60]/90 backdrop-blur text-white text-[10px] font-bold px-2 py-1 rounded-md shadow-sm flex items-center gap-1">
                                    <Leaf size={10} /> {product.fundContributionPercent}%
                                </div>
                            </div>
                            <div className="flex-1 flex flex-col">
                                <span className="text-[10px] text-[#9CA3AF] uppercase font-bold mb-1">{product.category}</span>
                                <h3 className="text-sm font-bold text-[#1F2937] leading-tight mb-2 line-clamp-2">{t(product.name as any)}</h3>
                                <div className="mt-auto">
                                    <p className="text-[#40A7E3] font-bold text-base">{product.price.toLocaleString()} {t('currency_sum')}</p>
                                    <button className="w-full mt-2 bg-[#F3F4F6] text-[#1F2937] text-[10px] font-bold py-2.5 rounded-xl group-hover:bg-[#40A7E3] group-hover:text-white transition-colors">
                                        {t('btn_buy')}
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default MarketView;
