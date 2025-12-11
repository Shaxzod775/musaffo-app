export type Tab = 'home' | 'fund' | 'market' | 'community' | 'chat';

export interface AppState {
  hasOnboarded: boolean;
  activeTab: Tab;
  showChat: boolean;
  user: UserState;
}

export interface UserState {
  isContributor: boolean; // "Skin in the game" check
  contributionAmount: number;
  totalDonated?: number;
  projectContributions?: { [projectId: string]: number };
  name: string;
  status: 'Newcomer' | 'Eco-Protector' | 'Guardian of the Sky';
  // Telegram Mini App fields
  telegramId?: number;
  telegramUsername?: string;
}

export interface AirQualityData {
  aqi: number;
  pm25: number;
  pm10?: number;
  no2?: number;
  status: string;
  advice: string;
  location: string;
  lastUpdated: string;
  healthWarning?: string;
  aqiLevel?: string;
}

export interface FundProject {
  id: string;
  title: string;
  description: string;
  titleKey?: string;
  descKey?: string;
  detailKey?: string;
  targetAmount: number;
  currentAmount: number;
  status: 'active' | 'completed' | 'voting';
  image: string;
  votesFor?: number;
  votesAgainst?: number;
}

export interface EcoProduct {
  id: string;
  name: string;
  price: number;
  image: string;
  fundContributionPercent: number;
  category: 'Purifier' | 'Mask' | 'Monitor' | 'Plants';
}

export interface NewsItem {
  id: string;
  title: string;
  summary: string; // AI Summarized text
  source: string;
  time: string;
  tag: 'Gov' | 'Global' | 'Tech';
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'model';
  text: string;
  isThinking?: boolean;
}