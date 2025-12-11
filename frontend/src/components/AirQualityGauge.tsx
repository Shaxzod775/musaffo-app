import React, { useState, useEffect, useRef } from 'react';
import { AirQualityData } from '../types';
import { useLanguage } from '../context/LanguageContext';

// Компонент одного крутящегося слота (цифры)
const SlotDigit: React.FC<{
  digit: string;
  delay: number;
  color: string;
  isLoading: boolean;
}> = ({ digit, delay, color, isLoading }) => {
  const [displayDigit, setDisplayDigit] = useState<string>('0');
  const [isSpinning, setIsSpinning] = useState(true);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (isLoading) {
      setIsSpinning(true);
      intervalRef.current = setInterval(() => {
        setDisplayDigit(Math.floor(Math.random() * 10).toString());
      }, 80);
      return;
    }

    setIsSpinning(true);
    let spinCount = 0;
    const maxSpins = 15 + delay * 5;

    intervalRef.current = setInterval(() => {
      spinCount++;
      if (spinCount < maxSpins) {
        setDisplayDigit(Math.floor(Math.random() * 10).toString());
      } else {
        setDisplayDigit(digit);
        setIsSpinning(false);
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
        }
      }
    }, 60);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [digit, delay, isLoading]);

  return (
    <span
      className={`inline-block transition-all duration-150 ${isSpinning ? 'blur-[1px]' : ''}`}
      style={{
        color,
        transform: isSpinning ? 'translateY(-2px)' : 'translateY(0)',
      }}
    >
      {displayDigit}
    </span>
  );
};

// Компонент казино-счетчика
const CasinoCounter: React.FC<{
  value: number;
  color: string;
  isLoading: boolean;
  size?: 'small' | 'large';
}> = ({ value, color, isLoading, size = 'large' }) => {
  const digits = value.toString().split('');
  const textSize = size === 'large' ? 'text-[48px]' : 'text-[24px]';

  if (isLoading) {
    return (
      <div className={`flex justify-center items-center ${textSize} font-bold leading-none`}>
        {['0', '0', '0'].map((_, index) => (
          <SlotDigit key={index} digit="0" delay={index} color={color} isLoading={true} />
        ))}
      </div>
    );
  }

  return (
    <div className={`flex justify-center items-center ${textSize} font-bold leading-none`}>
      {digits.map((digit, index) => (
        <SlotDigit
          key={`${value}-${index}`}
          digit={digit}
          delay={index}
          color={color}
          isLoading={false}
        />
      ))}
    </div>
  );
};

// Маленький анимированный индикатор PM
const PollutantGauge: React.FC<{
  label: string;
  value: number;
  maxValue: number;
  color: string;
}> = ({ label, value, maxValue, color }) => {
  const [animatedValue, setAnimatedValue] = useState(0);
  const [animatedProgress, setAnimatedProgress] = useState(0);
  const targetProgress = Math.min(value / maxValue, 1);

  // Animate on mount
  useEffect(() => {
    // Animate the arc
    const arcAnimation = setTimeout(() => {
      setAnimatedProgress(targetProgress);
    }, 100);

    // Animate the number (casino style)
    let currentValue = 0;
    const increment = Math.ceil(value / 20);
    const interval = setInterval(() => {
      currentValue += increment;
      if (currentValue >= value) {
        setAnimatedValue(value);
        clearInterval(interval);
      } else {
        setAnimatedValue(currentValue);
      }
    }, 50);

    return () => {
      clearTimeout(arcAnimation);
      clearInterval(interval);
    };
  }, [value, targetProgress]);

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-[50px] h-[28px] mb-1">
        <svg width="50" height="28" viewBox="0 0 50 28">
          {/* Background arc */}
          <path
            d="M 5 25 A 20 20 0 0 1 45 25"
            fill="none"
            stroke="#E5E7EB"
            strokeWidth="5"
            strokeLinecap="round"
          />
          {/* Animated progress arc */}
          <path
            d="M 5 25 A 20 20 0 0 1 45 25"
            fill="none"
            stroke={color}
            strokeWidth="5"
            strokeLinecap="round"
            strokeDasharray={`${animatedProgress * 62.8} 62.8`}
            style={{ transition: 'stroke-dasharray 1s ease-out' }}
          />
        </svg>
        {/* Animated value at bottom center of arc */}
        <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2">
          <span className="text-[11px] font-bold transition-all duration-150" style={{ color }}>
            {animatedValue}
          </span>
        </div>
      </div>
      <span className="text-[11px] font-medium text-[#6B7280] mt-1">{label}</span>
    </div>
  );
};

interface GaugeProps {
  data: AirQualityData;
  isLoading?: boolean;
  onRecommendationsClick?: () => void;
}

const AirQualityGauge: React.FC<GaugeProps> = ({ data, isLoading = false, onRecommendationsClick }) => {
  const { t, language } = useLanguage();
  const [showContent, setShowContent] = useState(false);

  // UI Kit Colors
  const colors = {
    green: '#27AE60',
    yellow: '#F59E0B',
    orange: '#F97316',
    red: '#EB5757',
    purple: '#9333EA',
    maroon: '#7C2D12',
  };

  const getStatusStyles = (aqi: number) => {
    if (aqi <= 50) return { color: colors.green, label: t('aqi_status_good') };
    if (aqi <= 100) return { color: colors.yellow, label: t('aqi_status_moderate') };
    if (aqi <= 150) return { color: colors.orange, label: t('aqi_status_sensitive') };
    if (aqi <= 200) return { color: colors.red, label: t('aqi_status_unhealthy') };
    if (aqi <= 300) return { color: colors.purple, label: t('aqi_status_very_unhealthy') };
    return { color: colors.maroon, label: t('aqi_status_hazardous') };
  };

  // Recommendations based on AQI level
  const getRecommendations = (aqi: number) => {
    const recommendations = {
      ru: {
        close_windows: '🏠 Закройте окна',
        wear_mask: '😷 Носите маску (чувствительные)',
        avoid_outdoor: '🏃 Избегайте нагрузок на улице',
        air_purifier: '🌿 Включите очиститель воздуха',
        stay_home: '🏠 Оставайтесь дома',
        wear_n95: '😷 Носите маску N95/FFP2',
        no_outdoor: '⛔ Не выходите на улицу',
        emergency: '🚨 Вызов скорой при ухудшении'
      },
      uz: {
        close_windows: '🏠 Derazalarni yoping',
        wear_mask: '😷 Niqob taqing (sezgir odamlar)',
        avoid_outdoor: '🏃 Tashqarida jismoniy mashqlardan saqlaning',
        air_purifier: '🌿 Havo tozalagichni yoqing',
        stay_home: '🏠 Uyda qoling',
        wear_n95: '😷 N95/FFP2 niqob taqing',
        no_outdoor: "⛔ Ko'chaga chiqmang",
        emergency: '🚨 Ahvol yomonlashsa tez yordam'
      },
      en: {
        close_windows: '🏠 Close windows',
        wear_mask: '😷 Wear mask (sensitive groups)',
        avoid_outdoor: '🏃 Avoid outdoor exercise',
        air_purifier: '🌿 Turn on air purifier',
        stay_home: '🏠 Stay home',
        wear_n95: '😷 Wear N95/FFP2 mask',
        no_outdoor: '⛔ Do not go outside',
        emergency: '🚨 Call emergency if worsens'
      }
    };

    const lang = recommendations[language as keyof typeof recommendations] || recommendations.ru;

    if (aqi <= 50) {
      return [];
    } else if (aqi <= 100) {
      return [lang.wear_mask, lang.avoid_outdoor];
    } else if (aqi <= 150) {
      return [lang.close_windows, lang.wear_mask, lang.avoid_outdoor, lang.air_purifier];
    } else if (aqi <= 200) {
      return [lang.close_windows, lang.wear_n95, lang.no_outdoor, lang.air_purifier];
    } else {
      return [lang.stay_home, lang.wear_n95, lang.no_outdoor, lang.emergency];
    }
  };

  // Get mortality statistic based on AQI level
  const getMortalityStat = (aqi: number) => {
    const stats = {
      ru: {
        good: '',
        moderate: '',
        unhealthy_sensitive: '',
        unhealthy: '',
        very_unhealthy: '',
        hazardous: ''
      },
      uz: {
        good: '',
        moderate: '',
        unhealthy_sensitive: '',
        unhealthy: '',
        very_unhealthy: '',
        hazardous: ''
      },
      en: {
        good: '',
        moderate: '',
        unhealthy_sensitive: '',
        unhealthy: '',
        very_unhealthy: '',
        hazardous: ''
      }
    };

    const langStats = stats[language as keyof typeof stats] || stats.ru;

    if (aqi <= 50) return langStats.good;
    if (aqi <= 100) return langStats.moderate;
    if (aqi <= 150) return langStats.unhealthy_sensitive;
    if (aqi <= 200) return langStats.unhealthy;
    if (aqi <= 300) return langStats.very_unhealthy;
    return langStats.hazardous;
  };

  // What to do label
  const whatToDoLabel = {
    ru: 'Что делать?',
    uz: 'Nima qilish kerak?',
    en: 'What to do?'
  };

  const styles = isLoading ? { color: colors.purple, label: t('aqi_status_loading') } : getStatusStyles(data.aqi);
  const mortalityStat = getMortalityStat(data.aqi);
  const recommendations = getRecommendations(data.aqi);

  // Circle Math
  const radius = 70;
  const circumference = 2 * Math.PI * radius;
  const progress = isLoading ? 0.5 : Math.min(data.aqi / 300, 1);
  const strokeDashoffset = circumference - (progress * circumference);

  // PM values from API (already calculated by backend)
  const pm25 = data.pm25 || 0;
  const pm10 = data.pm10 || 0;
  const no2 = data.no2 || 0;

  // Показываем контент после загрузки
  useEffect(() => {
    if (!isLoading) {
      const timer = setTimeout(() => setShowContent(true), 800);
      return () => clearTimeout(timer);
    } else {
      setShowContent(false);
    }
  }, [isLoading, data.aqi]);

  return (
    <div className="bg-white card-radius p-4 sm:p-5 shadow-soft h-full flex flex-col justify-center">
      {/* Responsive layout - Vertical on mobile, Horizontal on larger screens */}
      <div className="flex flex-col sm:flex-row gap-4 sm:gap-6 items-center h-full">
        {/* Left side - Circular Gauge with status */}
        <div className="flex flex-col items-center flex-shrink-0 w-full sm:w-[180px]">
          <div className="relative w-[160px] h-[160px] mb-3">
            <svg width="160" height="160" viewBox="0 0 160 160" className="transform -rotate-90">
              {/* Background Circle */}
              <circle
                cx="80"
                cy="80"
                r={radius}
                fill="none"
                stroke="#E5E7EB"
                strokeWidth="12"
              />
              {/* Progress Circle */}
              <circle
                cx="80"
                cy="80"
                r={radius}
                fill="none"
                stroke={styles.color}
                strokeWidth="12"
                strokeLinecap="round"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                className={`transition-all duration-1000 ease-out ${isLoading ? 'animate-pulse' : ''}`}
              />
            </svg>

            {/* Centered Value */}
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center">
              <CasinoCounter
                value={data.aqi}
                color={styles.color}
                isLoading={isLoading}
                size="large"
              />
              <div className="text-[14px] text-[#6B7280] font-semibold mt-1">AQI</div>
            </div>
          </div>

          {/* Status label */}
          <div
            className={`text-[18px] font-bold mb-1 transition-opacity duration-500 text-center ${showContent && !isLoading ? 'opacity-100' : 'opacity-50'}`}
            style={{ color: styles.color }}
          >
            {styles.label}
          </div>

          {/* Health Warning */}
          <div
            className={`text-[12px] text-[#6B7280] text-center leading-snug transition-opacity duration-500 ${showContent && !isLoading ? 'opacity-100' : 'opacity-50'}`}
          >
            {data.healthWarning || data.advice}
          </div>
        </div>

        {/* Right side - Location, Recommendations, PM indicators */}
        <div className="flex-1 flex flex-col min-w-0 h-full justify-between">
          {/* Location badge - hidden on mobile as gauge is full width */}
          <div className="hidden sm:flex justify-end mb-3">
            <div className="bg-[#F3F4F6] px-3 py-1 rounded-full text-[10px] font-semibold text-[#4B5563]">
              {t('location_tashkent_city')}
            </div>
          </div>



          {/* PM indicators at bottom */}
          <div className="flex justify-around pt-3 mt-3 sm:mt-auto border-t border-[#E5E7EB] md:flex-col md:border-t-0 md:border-l md:pl-6 md:justify-center md:gap-6 md:h-full md:pt-0 md:mt-0">
            <PollutantGauge
              label="PM2.5"
              value={pm25}
              maxValue={150}
              color={styles.color}
            />
            <PollutantGauge
              label="PM10"
              value={pm10}
              maxValue={250}
              color={styles.color}
            />
            <PollutantGauge
              label="NO₂"
              value={no2}
              maxValue={100}
              color={styles.color}
            />
          </div>
        </div>
      </div>

      {/* Mortality Statistic - Full width below */}
      {mortalityStat && (
        <div
          className={`text-[11px] text-[#92400E] bg-[#FEF3C7] px-4 py-2 rounded-lg mt-4 text-center transition-opacity duration-500 ${showContent && !isLoading ? 'opacity-100' : 'opacity-0'}`}
        >
          {mortalityStat}
        </div>
      )}

      {/* Recommendations Link */}
      {onRecommendationsClick && data.aqi > 50 && (
        <div className="text-center mt-3">
          <button
            onClick={(e) => { e.stopPropagation(); onRecommendationsClick(); }}
            className="text-[13px] text-[#40A7E3] font-semibold hover:underline"
          >
            {t('recommendations_link')}
          </button>
        </div>
      )}
    </div>
  );
};

export default AirQualityGauge;