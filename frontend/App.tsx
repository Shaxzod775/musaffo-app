import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Tab, UserState, AirQualityData, FundProject, EcoProduct, NewsItem } from './src/types';
import Navigation from './src/components/Navigation';
import Onboarding from './src/components/Onboarding';
import HomeView from './src/views/HomeView';
import FundView from './src/views/FundView';
import MarketView from './src/views/MarketView';
import CommunityView from './src/views/CommunityView';
import NewsDetail from './src/components/NewsDetail';
import DonationModal from './src/components/DonationModal';
import ProjectDetail from './src/components/ProjectDetail';
import ProductDetail from './src/components/ProductDetail';
import InitiativeDetail from './src/components/InitiativeDetail';
import SettingsModal from './src/components/SettingsModal';
import { CheckCircle, Loader2 } from 'lucide-react';
import { useLanguage } from './src/context/LanguageContext';
import ChatKitModal from './src/components/ChatKitModal';
import { projectsApi, donationsApi, votingApi, statsApi, newsApi } from './src/services/api';
import HealthRecommendations from './src/components/HealthRecommendations';
import { useTelegram } from './src/hooks/useTelegram';

// MOCK_AQI will be created inside component to use translations

const INITIAL_USER: UserState = {
    isContributor: false,
    contributionAmount: 0,
    name: "Mehmon",
    status: 'Newcomer'
};

const MOCK_PRODUCTS: EcoProduct[] = [
    // Purifiers
    { id: '1', name: 'product_xiaomi_purifier', price: 2500000, image: '/images/xiaomi-air-purifier.jpg', fundContributionPercent: 5, category: 'Purifier' },
    { id: '4', name: 'product_dyson_cool', price: 8500000, image: '/images/dyson-pure-cool.jpg', fundContributionPercent: 7, category: 'Purifier' },
    { id: '7', name: 'product_philips_purifier', price: 3200000, image: '/images/philips-AC2887.jpg', fundContributionPercent: 6, category: 'Purifier' },
    // Masks
    { id: '2', name: 'product_mask_n95', price: 15000, image: '/images/mask-95.jpg', fundContributionPercent: 10, category: 'Mask' },
    { id: '5', name: 'product_ffp2_respirator', price: 95000, image: '/images/ffp2-respirator.png?v=2', fundContributionPercent: 12, category: 'Mask' },
    { id: '8', name: 'product_reusable_mask', price: 45000, image: '/images/mask-with-filter.jpg', fundContributionPercent: 15, category: 'Mask' },
    // Plants
    { id: '3', name: 'product_sansevieria', price: 85000, image: '/images/sansevirto.jpg', fundContributionPercent: 15, category: 'Plants' },
    { id: '6', name: 'product_aloe_vera', price: 65000, image: 'https://images.unsplash.com/photo-1509423350716-97f9360b4e09?auto=format&fit=crop&w=400&h=400&q=80', fundContributionPercent: 18, category: 'Plants' },
    { id: '9', name: 'product_spathiphyllum', price: 95000, image: '/images/спатифиллум.jpg', fundContributionPercent: 20, category: 'Plants' },
    { id: '10', name: 'product_ficus', price: 125000, image: 'https://images.unsplash.com/photo-1614594975525-e45190c55d0b?auto=format&fit=crop&w=400&h=400&q=80', fundContributionPercent: 15, category: 'Plants' },
];

// MOCK_NEWS will be created with translations inside the component

const App: React.FC = () => {
    const navigate = useNavigate();
    const location = useLocation();

    // Get active tab from URL
    const getTabFromPath = (path: string): Tab => {
        if (path === '/fund') return 'fund';
        if (path === '/market') return 'market';
        if (path === '/community') return 'community';
        return 'home';
    };

    // Check localStorage for onboarding state
    const [hasOnboarded, setHasOnboarded] = useState(() => {
        const saved = localStorage.getItem('hasOnboarded');
        return saved === 'true';
    });
    const [activeTab, setActiveTab] = useState<Tab>(getTabFromPath(location.pathname));
    const [showChat, setShowChat] = useState(false);
    const [user, setUser] = useState<UserState>(INITIAL_USER);
    const [projects, setProjects] = useState<FundProject[]>([]);
    const [isLoadingProjects, setIsLoadingProjects] = useState(true);
    const [toast, setToast] = useState<{ msg: string, type: 'success' | 'info' } | null>(null);

    // Stats state
    const [stats, setStats] = useState<{ totalDonations: number; totalDonors: number; totalProjects: number; activeProjects: number } | null>(null);
    const [statsLoading, setStatsLoading] = useState(true);

    // Health Recommendations modal
    const [showHealthRecommendations, setShowHealthRecommendations] = useState(false);
    const { t, language } = useLanguage();

    // Telegram Mini App integration
    const { isTelegramWebApp, user: tgUser, ready, expand, hapticFeedback, colorScheme, setHeaderColor, setBackgroundColor } = useTelegram();

    // Initialize Telegram Web App
    useEffect(() => {
        if (isTelegramWebApp) {
            // Mark app as ready
            ready();
            // Expand to full height
            expand();
            // Set theme colors
            setHeaderColor('#40A7E3');
            setBackgroundColor('#F3F4F6');

            // Update user info from Telegram
            if (tgUser) {
                setUser(prev => ({
                    ...prev,
                    name: tgUser.first_name + (tgUser.last_name ? ' ' + tgUser.last_name : ''),
                    telegramId: tgUser.id,
                    telegramUsername: tgUser.username,
                }));
            }

            console.log('[Telegram] Mini App initialized', { user: tgUser, colorScheme });
        }
    }, [isTelegramWebApp, tgUser]);

    // News state
    const [news, setNews] = useState<NewsItem[]>([]);
    const [isLoadingNews, setIsLoadingNews] = useState(true);

    // Helper function to calculate time ago
    const getTimeAgo = (timestamp: any): string => {
        const now = new Date();
        let then: Date;

        // Handle Firebase Timestamp object format
        if (timestamp && typeof timestamp === 'object' && timestamp._seconds) {
            then = new Date(timestamp._seconds * 1000);
        } else if (timestamp && typeof timestamp === 'object' && timestamp.seconds) {
            then = new Date(timestamp.seconds * 1000);
        } else {
            then = new Date(timestamp);
        }

        const diffMs = now.getTime() - then.getTime();

        // Handle invalid or future dates
        if (isNaN(diffMs) || diffMs < 0) {
            return `1 ${t('news_time_hours_ago')}`;
        }

        const diffMinutes = Math.floor(diffMs / (1000 * 60));
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
        const diffDays = Math.floor(diffHours / 24);

        if (diffDays > 0) {
            return `${diffDays} ${t('news_time_days_ago')}`;
        } else if (diffHours > 0) {
            return `${diffHours} ${t('news_time_hours_ago')}`;
        } else {
            return `${Math.max(1, diffMinutes)} ${t('news_time_minutes_ago')}`;
        }
    };

    // Transform news with current language
    const transformedNews: NewsItem[] = news.map(item => ({
        ...item,
        title: item.translations?.[language]?.title || item.translations?.ru?.title || '',
        summary: item.translations?.[language]?.summary || item.translations?.ru?.summary || '',
        time: getTimeAgo(item.timestamp)
    }));

    // Load donation status and project contributions from API on mount
    useEffect(() => {
        const loadDonorInfo = async () => {
            const userName = user.name || 'guest';

            try {
                const donorInfo = await donationsApi.getDonorInfo(userName);

                if (donorInfo.isContributor && donorInfo.totalDonated > 0) {
                    setUser(prev => ({
                        ...prev,
                        isContributor: true,
                        contributionAmount: donorInfo.totalDonated,
                        totalDonated: donorInfo.totalDonated,
                        status: 'Eco-Protector',
                        projectContributions: donorInfo.projectContributions || {}
                    }));

                    localStorage.setItem('hasDonated', 'true');
                    localStorage.setItem('donationAmount', String(donorInfo.totalDonated));
                }
            } catch (error) {
                console.error('Failed to load donor info:', error);
            }
        };

        loadDonorInfo();
    }, []);

    // Real AQI data from IQAir API
    const [aqiData, setAqiData] = useState<AirQualityData>({
        aqi: 0,
        pm25: 0,
        status: t('aqi_status_loading'),
        advice: t('aqi_advice_loading'),
        location: 'Toshkent',
        lastUpdated: 'Loading...'
    });
    const [aqiLoading, setAqiLoading] = useState(true);

    // Detail View State
    const [activeNews, setActiveNews] = useState<NewsItem | null>(null);
    const [activeProject, setActiveProject] = useState<FundProject | null>(null);
    const [activeProduct, setActiveProduct] = useState<EcoProduct | null>(null);
    const [activeInitiative, setActiveInitiative] = useState<FundProject | null>(null);
    const [showDonation, setShowDonation] = useState(false);
    const [showSettings, setShowSettings] = useState(false);

    // Chat State (now using ChatKit)
    // Old Gemini chat state removed - using ChatKit modal instead

    // Fetch AQI data function
    const fetchAQI = async () => {
        try {
            const response = await fetch('https://iqair-service-242593050011.us-central1.run.app/api/air-quality?city=Tashkent&country=Uzbekistan');
            const result = await response.json();

            if (result.status === 'success' && result.data) {
                const data = result.data;
                const pollution = data.current?.pollution || {};
                const aqi = pollution.aqius || 0;

                // Get pollutants from API response
                const pollutants = result.pollutants || {};
                const pm25 = pollutants.pm25 || 0;
                const pm10 = pollutants.pm10 || 0;
                const no2 = pollutants.no2 || 0;

                // Determine status and advice based on AQI
                let status = '';
                let advice = '';
                let level = 'moderate';

                if (aqi <= 50) {
                    status = t('aqi_status_good');
                    advice = t('aqi_advice_good');
                    level = 'good';
                } else if (aqi <= 100) {
                    status = t('aqi_status_moderate');
                    advice = t('aqi_advice_moderate');
                    level = 'moderate';
                } else if (aqi <= 150) {
                    status = t('aqi_status_sensitive');
                    advice = t('aqi_advice_sensitive');
                    level = 'unhealthy_sensitive';
                } else if (aqi <= 200) {
                    status = t('aqi_status_unhealthy');
                    advice = t('aqi_advice_unhealthy');
                    level = 'unhealthy';
                } else if (aqi <= 300) {
                    status = t('aqi_status_very_unhealthy');
                    advice = t('aqi_advice_very_unhealthy');
                    level = 'very_unhealthy';
                } else {
                    status = t('aqi_status_hazardous');
                    advice = t('aqi_advice_hazardous');
                    level = 'hazardous';
                }

                // Get health warning from API response
                const healthRisks = result.healthRisks || {};
                const warningKey = `warning_${language}` as keyof typeof healthRisks;
                const healthWarning = healthRisks[warningKey] || '';

                setAqiData({
                    aqi,
                    pm25,
                    pm10,
                    no2,
                    status,
                    advice,
                    location: `${data.city || 'Toshkent'}, ${data.state || 'Toshkent'}`,
                    lastUpdated: new Date().toLocaleTimeString('uz-UZ', { hour: '2-digit', minute: '2-digit' }),
                    healthWarning,
                    aqiLevel: level
                });
            }
        } catch (error) {
            console.error('Error fetching AQI data:', error);
            // Fallback to default values
            setAqiData({
                aqi: 165,
                pm25: 62.4,
                status: t('aqi_status_unhealthy'),
                advice: t('aqi_advice_unhealthy'),
                location: 'Toshkent',
                lastUpdated: 'Hozir',
                healthWarning: t('aqi_advice_unhealthy'),
                aqiLevel: 'unhealthy'
            });
        }
    };

    // Fetch stats function
    const fetchStats = async () => {
        try {
            const response = await statsApi.getAll();
            if (response.status === 'success') {
                setStats(response.data);
            }
        } catch (error) {
            console.error('Failed to load stats:', error);
        }
    };

    // Fetch projects function
    const fetchProjects = async () => {
        try {
            const data = await projectsApi.getAll();
            // Add detailKey based on titleKey
            const projectsWithDetails = data.map(p => ({
                ...p,
                detailKey: p.titleKey ? p.titleKey.replace('_title', '_detail') : undefined
            }));
            setProjects(projectsWithDetails);
        } catch (error) {
            console.error('Failed to load projects:', error);
            setToast({ msg: t('error_loading_projects') || 'Failed to load projects', type: 'info' });
        }
    };

    // Fetch news function
    const fetchNews = async () => {
        try {
            const data = await newsApi.getAll();
            setNews(data);
        } catch (error) {
            console.error('Failed to load news:', error);
        }
    };

    // Load all data in parallel on mount - ONLY ONCE
    const dataLoadedRef = React.useRef(false);

    useEffect(() => {
        if (dataLoadedRef.current) return;
        dataLoadedRef.current = true;

        const loadAllData = async () => {
            // Start all loading states
            setAqiLoading(true);
            setStatsLoading(true);
            setIsLoadingProjects(true);
            setIsLoadingNews(true);

            // Fetch all data in parallel
            await Promise.all([
                fetchAQI(),
                fetchStats(),
                fetchProjects(),
                fetchNews()
            ]);

            // End all loading states
            setAqiLoading(false);
            setStatsLoading(false);
            setIsLoadingProjects(false);
            setIsLoadingNews(false);
        };

        loadAllData();
    }, []); // Empty deps - only run once on mount

    useEffect(() => {
        if (toast) {
            const timer = setTimeout(() => setToast(null), 3000);
            return () => clearTimeout(timer);
        }
    }, [toast]);

    // Refetch stats (called after donation)
    const refetchStats = async () => {
        try {
            const response = await statsApi.getAll();
            if (response.status === 'success') {
                setStats(response.data);
            }
        } catch (error) {
            console.error('Failed to refetch stats:', error);
        }
    };

    // Actions
    const simulateDonation = async (amount: number = 10000) => {
        try {
            setToast({ msg: t('toast_processing_payment'), type: 'info' });

            // Create donation via API
            const userId = user.name || 'guest';
            await donationsApi.create({
                userId,
                amount,
                currency: 'UZS',
                status: 'completed'
            });

            // Get active projects to distribute donation
            const activeProjects = projects.filter(p => p.status === 'active');
            const activeProjectIds = activeProjects.map(p => p.id);

            // Distribute donation to projects via API
            if (activeProjectIds.length > 0) {
                await donationsApi.distributeToProjects(userId, amount, activeProjectIds);

                // Update each active project's currentAmount locally
                const amountPerProject = Math.floor(amount / activeProjectIds.length);
                for (const project of activeProjects) {
                    try {
                        await projectsApi.update(project.id, {
                            currentAmount: project.currentAmount + amountPerProject
                        });
                    } catch (error) {
                        console.error(`Failed to update project ${project.id}:`, error);
                    }
                }
            }

            // Get updated donor info with project contributions
            const donorInfo = await donationsApi.getDonorInfo(userId);

            setUser(prev => ({
                ...prev,
                isContributor: true,
                contributionAmount: donorInfo.totalDonated || amount,
                totalDonated: donorInfo.totalDonated || amount,
                status: 'Eco-Protector',
                projectContributions: donorInfo.projectContributions || {}
            }));

            // Store donation status in localStorage
            localStorage.setItem('hasDonated', 'true');
            localStorage.setItem('donationAmount', String(donorInfo.totalDonated || amount));

            // Refetch stats and projects to update UI
            await Promise.all([
                refetchStats(),
                fetchProjects()
            ]);

            setToast({ msg: t('toast_thank_you', { amount: amount.toLocaleString() }), type: 'success' });
            setShowDonation(false);
        } catch (error) {
            console.error('Donation failed:', error);
            setToast({ msg: t('error_donation_failed') || 'Donation failed', type: 'info' });
        }
    };

    const simulatePurchase = (amount: number) => {
        setToast({ msg: t('toast_purchase_complete'), type: 'success' });
    };

    // Handle tab change with URL navigation
    const handleTabChange = (tab: Tab) => {
        const paths: Record<Tab, string> = {
            home: '/',
            fund: '/fund',
            market: '/market',
            community: '/community',
            chat: '/'  // Chat is handled via modal, not URL
        };

        navigate(paths[tab]);
        setActiveTab(tab);

        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    // Sync activeTab with URL changes
    useEffect(() => {
        const tab = getTabFromPath(location.pathname);
        setActiveTab(tab);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }, [location.pathname]);

    // Toast Component
    const Toast = () => {
        if (!toast) return null;
        return (
            <div className="fixed top-4 left-4 right-4 z-[100] animate-fade-in-down">
                <div className={`bg-white/90 backdrop-blur border-l-4 ${toast.type === 'success' ? 'border-[#27AE60]' : 'border-[#40A7E3]'} shadow-2xl p-4 rounded-r-xl flex items-center gap-3`}>
                    {toast.type === 'success' ? <CheckCircle className="text-[#27AE60]" /> : <Loader2 className="animate-spin text-[#40A7E3]" />}
                    <span className="text-sm font-bold text-[#1F2937]">{toast.msg}</span>
                </div>
            </div>
        );
    }

    // Handle onboarding completion
    const handleOnboardingFinish = () => {
        localStorage.setItem('hasOnboarded', 'true');
        setHasOnboarded(true);
    };

    // 1. Onboarding Screen
    if (!hasOnboarded) {
        return (
            <Onboarding onFinish={handleOnboardingFinish} />
        );
    }

    // --- APP STRUCTURE ---
    return (
        <div className="min-h-screen bg-[#F3F4F6] font-sans text-[#1F2937] relative">
            <Toast />

            <main className="w-full max-w-4xl mx-auto min-h-screen bg-[#F3F4F6] relative lg:shadow-2xl overflow-y-auto no-scrollbar">
                {activeTab === 'home' && (
                    <HomeView
                        aqiData={aqiData}
                        aqiLoading={aqiLoading}
                        news={transformedNews}
                        newsLoading={isLoadingNews}
                        stats={stats || undefined}
                        statsLoading={statsLoading}
                        setActiveTab={handleTabChange}
                        onNewsClick={setActiveNews}
                        onDonateClick={() => setShowDonation(true)}
                        onSettingsClick={() => setShowSettings(true)}
                        onHealthRecommendationsClick={() => setShowHealthRecommendations(true)}
                    />
                )}
                {activeTab === 'fund' && (
                    <FundView
                        user={user}
                        projects={projects}
                        isLoadingProjects={isLoadingProjects}
                        simulateDonation={() => setShowDonation(true)}
                        onProjectClick={setActiveProject}
                    />
                )}
                {activeTab === 'market' && (
                    <MarketView
                        products={MOCK_PRODUCTS}
                        simulatePurchase={simulatePurchase}
                        onProductClick={setActiveProduct}
                    />
                )}
                {activeTab === 'community' && (
                    <CommunityView
                        user={user}
                        projects={projects}
                        setActiveTab={handleTabChange}
                        onInitiativeClick={setActiveInitiative}
                        onVote={(projectId, voteType) => {
                            setProjects(prev => prev.map(p => {
                                if (p.id === projectId) {
                                    return {
                                        ...p,
                                        votesFor: voteType === 'for' ? (p.votesFor || 0) + 1 : p.votesFor,
                                        votesAgainst: voteType === 'against' ? (p.votesAgainst || 0) + 1 : p.votesAgainst
                                    };
                                }
                                return p;
                            }));
                            setToast({ msg: voteType === 'for' ? t('toast_vote_accepted_yes') : t('toast_vote_accepted_no'), type: 'success' });
                        }}
                    />
                )}
            </main>

            {/* DETAIL MODALS */}
            {activeNews && (
                <NewsDetail news={activeNews} onClose={() => setActiveNews(null)} />
            )}

            {showDonation && (
                <DonationModal
                    onClose={() => {
                        setShowDonation(false);
                    }}
                    onDonate={simulateDonation}
                    isRepeatDonor={user.isContributor}
                    previousAmount={user.contributionAmount}
                />
            )}

            {showSettings && (
                <SettingsModal onClose={() => setShowSettings(false)} />
            )}

            {showHealthRecommendations && (
                <div className="fixed inset-0 z-50 bg-white overflow-y-auto">
                    <HealthRecommendations
                        onBack={() => setShowHealthRecommendations(false)}
                        aqiLevel={aqiData.aqiLevel || 'moderate'}
                        aqi={aqiData.aqi}
                    />
                </div>
            )}

            {activeProject && (
                <ProjectDetail
                    project={activeProject}
                    onClose={() => setActiveProject(null)}
                    onDonate={() => { setActiveProject(null); setShowDonation(true); }}
                />
            )}

            {activeProduct && (
                <ProductDetail
                    product={activeProduct}
                    onClose={() => setActiveProduct(null)}
                    onBuy={() => { simulatePurchase(activeProduct.price); setActiveProduct(null); }}
                />
            )}

            {activeInitiative && (
                <InitiativeDetail
                    initiative={activeInitiative}
                    user={user}
                    onClose={() => setActiveInitiative(null)}
                    onVote={(id, type) => {
                        // Update project votes
                        setProjects(prevProjects => {
                            const updatedProjects = prevProjects.map(project => {
                                if (project.id === id) {
                                    const updatedProject = {
                                        ...project,
                                        votesFor: type === 'up' ? (project.votesFor || 0) + 1 : project.votesFor,
                                        votesAgainst: type === 'down' ? (project.votesAgainst || 0) + 1 : project.votesAgainst
                                    };
                                    // Update activeInitiative with new vote counts
                                    setActiveInitiative(updatedProject);
                                    return updatedProject;
                                }
                                return project;
                            });
                            return updatedProjects;
                        });
                        setToast({ msg: t('toast_vote_accepted'), type: 'success' });
                    }}
                />
            )}

            {/* CHATKIT MODAL */}
            <ChatKitModal
                isOpen={showChat}
                onClose={() => setShowChat(false)}
                backendUrl='https://musaffo-api-242593050011.europe-west1.run.app'
                theme="light"
            />

            <Navigation
                activeTab={activeTab}
                setTab={handleTabChange}
                onAiClick={() => setShowChat(true)}
            />
        </div>
    );
};

export default App;