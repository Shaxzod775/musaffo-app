import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Wind, Calendar, Globe } from 'lucide-react';

interface NewsPreviewData {
  id: string;
  channel: string;
  date: string;
  text: string;
  translations: {
    ru: string;
    uz: string;
    en: string;
  };
  link: string;
  photo?: string;
}

const NewsPreview: React.FC = () => {
  const { newsId } = useParams<{ newsId: string }>();
  const [newsData, setNewsData] = useState<NewsPreviewData | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeLanguage, setActiveLanguage] = useState<'ru' | 'uz' | 'en'>('ru');

  useEffect(() => {
    const fetchNewsData = async () => {
      try {
        const response = await fetch(`/news-preview/${newsId}.json`);
        const data = await response.json();
        setNewsData(data);
      } catch (error) {
        console.error('Failed to load news:', error);
      } finally {
        setLoading(false);
      }
    };

    if (newsId) {
      fetchNewsData();
    }
  }, [newsId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-blue-500"></div>
      </div>
    );
  }

  if (!newsData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-800 mb-2">Новость не найдена</h1>
          <p className="text-gray-600">Попробуйте позже</p>
        </div>
      </div>
    );
  }

  const languageNames = {
    ru: '🇷🇺 Русский',
    uz: '🇺🇿 O\'zbekcha',
    en: '🇬🇧 English'
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-3xl shadow-2xl overflow-hidden mb-6">
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-3 bg-white/20 rounded-full backdrop-blur">
                <Wind size={28} />
              </div>
              <div>
                <h1 className="text-2xl font-bold">Новость о качестве воздуха</h1>
                <p className="text-blue-100 text-sm">Air Quality News</p>
              </div>
            </div>

            {/* Meta info */}
            <div className="flex flex-wrap gap-4 text-sm">
              <div className="flex items-center gap-2 bg-white/10 px-3 py-1.5 rounded-full">
                <Globe size={16} />
                <span>{newsData.channel}</span>
              </div>
              <div className="flex items-center gap-2 bg-white/10 px-3 py-1.5 rounded-full">
                <Calendar size={16} />
                <span>{new Date(newsData.date).toLocaleDateString('ru-RU')}</span>
              </div>
            </div>
          </div>

          {/* Language selector */}
          <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
            <div className="flex gap-2">
              {(['ru', 'uz', 'en'] as const).map((lang) => (
                <button
                  key={lang}
                  onClick={() => setActiveLanguage(lang)}
                  className={`px-4 py-2 rounded-xl font-semibold text-sm transition-all ${
                    activeLanguage === lang
                      ? 'bg-blue-600 text-white shadow-lg scale-105'
                      : 'bg-white text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  {languageNames[lang]}
                </button>
              ))}
            </div>
          </div>

          {/* Content */}
          <div className="p-8">
            <div className="prose prose-lg max-w-none">
              <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">
                {newsData.translations[activeLanguage]}
              </p>
            </div>

            {/* Original link */}
            <div className="mt-8 pt-6 border-t border-gray-200">
              <a
                href={newsData.link}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 font-semibold"
              >
                <Globe size={20} />
                Открыть оригинал в Telegram
              </a>
            </div>
          </div>
        </div>

        {/* Powered by */}
        <div className="text-center text-gray-500 text-sm">
          <p>🤖 Автоматически обработано системой мониторинга качества воздуха</p>
          <p className="mt-1">Musaffo Air Quality Monitoring System</p>
        </div>
      </div>
    </div>
  );
};

export default NewsPreview;
