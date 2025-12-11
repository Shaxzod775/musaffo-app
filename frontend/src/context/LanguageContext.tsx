import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { translations, Language } from '../translations';

interface LanguageContextType {
    language: Language;
    setLanguage: (lang: Language) => void;
    t: (key: keyof typeof translations['ru'], params?: Record<string, string | number>) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

const LANGUAGE_STORAGE_KEY = 'musaffo_language';

export const LanguageProvider = ({ children }: { children: ReactNode }) => {
    // Load language from localStorage or default to Uzbek
    const [language, setLanguageState] = useState<Language>(() => {
        const saved = localStorage.getItem(LANGUAGE_STORAGE_KEY);
        return (saved as Language) || 'uz';
    });

    // Save language to localStorage when it changes
    const setLanguage = (lang: Language) => {
        setLanguageState(lang);
        localStorage.setItem(LANGUAGE_STORAGE_KEY, lang);
    };

    const t = (key: keyof typeof translations['ru'], params?: Record<string, string | number>) => {
        let text = translations[language][key] || key;

        if (params) {
            Object.entries(params).forEach(([k, v]) => {
                text = text.replace(`{${k}}`, String(v));
            });
        }

        return text;
    };

    return (
        <LanguageContext.Provider value={{ language, setLanguage, t }}>
            {children}
        </LanguageContext.Provider>
    );
};

export const useLanguage = () => {
    const context = useContext(LanguageContext);
    if (!context) {
        throw new Error('useLanguage must be used within a LanguageProvider');
    }
    return context;
};
