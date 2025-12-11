import React, { useState, useEffect } from 'react';
import { Tab } from '../types';
import { CloudSun, Wallet, Store, Users, Sparkles } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

interface Props {
  activeTab: Tab;
  setTab: (tab: Tab) => void;
  onAiClick: () => void;
}

const Navigation: React.FC<Props> = ({ activeTab, setTab, onAiClick }) => {
  const { t } = useLanguage();
  const [isSparkle, setIsSparkle] = useState(false);

  // Sparkle animation every 10 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setIsSparkle(true);
      setTimeout(() => setIsSparkle(false), 1000);
    }, 10000);

    return () => {
      clearInterval(interval);
    };
  }, []);

  const navItems = [
    { id: 'home', icon: CloudSun, label: t('nav_home') },
    { id: 'fund', icon: Wallet, label: t('nav_fund') },
    { id: 'market', icon: Store, label: t('nav_market') },
    { id: 'community', icon: Users, label: t('nav_community') },
  ];

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white/90 backdrop-blur-xl border-t border-[#E5E7EB] pb-safe pt-2 px-2 shadow-[0_-8px_30px_rgba(0,0,0,0.04)] z-50">
      <div className="flex justify-between items-end pb-4 md:pb-2 max-w-4xl mx-auto relative">

        {/* Left Side */}
        <div className="flex gap-1 w-2/5 justify-around">
          <NavButton item={navItems[0]} activeTab={activeTab} setTab={setTab} />
          <NavButton item={navItems[1]} activeTab={activeTab} setTab={setTab} />
        </div>

        {/* Floating AI Button (Center) */}
        <div className="absolute left-1/2 -translate-x-1/2 -top-8 group">
          <button
            onClick={onAiClick}
            className="btn-fab w-16 h-16 bg-main-gradient rounded-full shadow-button flex items-center justify-center border-4 border-[#F3F4F6] transition-all active:scale-95 relative z-10 overflow-hidden"
          >
            <Sparkles
              size={28}
              className={`text-white fill-white transition-transform duration-300 relative z-10 ${isSparkle ? 'scale-110' : ''
                }`}
            />
            {/* Shine sweep effect - like polished surface */}
            {isSparkle && (
              <div
                className="absolute inset-0 animate-shine-sweep"
                style={{
                  background: 'linear-gradient(120deg, transparent 30%, rgba(255,255,255,0.8) 50%, transparent 70%)',
                }}
              />
            )}
          </button>
          <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-[10px] font-bold text-[#4B5563] whitespace-nowrap bg-white/80 px-2 py-0.5 rounded-full backdrop-blur-sm">
            Musaffo AI
          </div>
        </div>

        {/* Right Side */}
        <div className="flex gap-1 w-2/5 justify-around">
          <NavButton item={navItems[2]} activeTab={activeTab} setTab={setTab} />
          <NavButton item={navItems[3]} activeTab={activeTab} setTab={setTab} />
        </div>
      </div>

      {/* Shine animation styles */}
      <style>{`
        @keyframes shine-sweep {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        .animate-shine-sweep {
          animation: shine-sweep 0.5s ease-in-out 2;
        }
      `}</style>
    </div>
  );
};

const NavButton = ({ item, activeTab, setTab }: { item: any, activeTab: Tab, setTab: (t: Tab) => void }) => {
  const isActive = activeTab === item.id;
  const Icon = item.icon;

  // Brand Colors: Active = Sky Blue #40A7E3
  const activeColorClass = 'text-[#40A7E3]';
  const inactiveColorClass = 'text-[#9CA3AF]';

  return (
    <button
      onClick={() => setTab(item.id as Tab)}
      className={`flex flex-col items-center gap-1 flex-1 min-w-[60px] group active:scale-95 transition-transform`}
    >
      <div className={`p-1.5 rounded-2xl transition-all duration-300 ${isActive ? '-translate-y-1' : ''
        } ${isActive ? activeColorClass : inactiveColorClass}`}>
        <Icon size={26} strokeWidth={isActive ? 2.5 : 2} />
      </div>
      <span className={`text-[10px] font-semibold transition-colors ${isActive ? activeColorClass : inactiveColorClass}`}>
        {item.label}
      </span>
    </button>
  );
}

export default Navigation;