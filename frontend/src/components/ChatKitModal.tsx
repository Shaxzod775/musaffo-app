import React, { useEffect, useRef, useState } from 'react';
import { ChatKit, useChatKit } from '@openai/chatkit-react';
import { useLanguage } from '../context/LanguageContext';
import '../styles/chatkit-custom.css';

/**
 * ChatKitModal - Модальное окно для отображения официального ChatKit UI от OpenAI
 *
 * Использует официальный @openai/chatkit-react компонент
 */

interface ChatKitModalProps {
  isOpen: boolean;
  onClose: () => void;
  clientId?: string;
  chatId?: string;
  backendUrl: string;
  theme?: 'dark' | 'light';
}

const ChatKitModal: React.FC<ChatKitModalProps> = ({
  isOpen,
  onClose,
  clientId,
  chatId,
  backendUrl,
  theme = 'light'  // Default to light theme
}) => {
  const modalRef = useRef<HTMLDivElement>(null);
  const [hasMessages, setHasMessages] = useState(false);
  const [aqiAutoLoaded, setAqiAutoLoaded] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);
  const { t } = useLanguage();

  // Определяем цвета в зависимости от темы
  const backgroundColor = theme === 'light' ? '#ffffff' : '#1a1a1a';
  const foregroundColor = theme === 'light' ? '#1a1a1a' : '#ffffff';

  // Конфигурация ChatKit
  const chatkit = useChatKit({
    api: {
      // url: `https://musaffo-api-242593050011.europe-west1.run.app/api/chatkit`,
      url: `http://localhost:8000/api/chatkit`,
      // domainKey используется только для production
      // В локальной разработке можно оставить пустым или использовать placeholder
      domainKey: 'domain_pk_6930214f612081939acaa38d1a5e82cb03e55b5a21a28b95',
      // Стратегия загрузки файлов - two_phase (upload_url приходит от backend)
      uploadStrategy: {
        type: 'two_phase',
      },
    },
    theme: {
      colorScheme: theme,
      radius: 'round',
    },
    startScreen: {
      greeting: t('chatkit_greeting'),
      prompts: [
        {
          label: t('chatkit_prompt_air'),
          prompt: t('chatkit_prompt_air_text'),
          icon: "lab",
        },
        {
          label: t('chatkit_prompt_eco'),
          prompt: t('chatkit_prompt_eco_text'),
          icon: "document",
        },
        {
          label: t('chatkit_prompt_health'),
          prompt: t('chatkit_prompt_health_text'),
          icon: "sparkle",
        },
      ],
    },
    composer: {
      placeholder: t('chatkit_placeholder'),
      attachments: {
        enabled: false,
      },
    },
    threadItemActions: {
      feedback: false, // Отключаем кнопки feedback
    },
    onResponseEnd: () => {
      console.log('[ChatKit] Response completed');
      setHasMessages(true);
    },
    onThreadChange: ({ threadId }) => {
      console.log('[ChatKit] Thread changed:', threadId);
    },
    onError: ({ error }) => {
      console.error('[ChatKit] Error:', error);
    },
  });

  // Управление анимацией при открытии/закрытии
  useEffect(() => {
    if (isOpen) {
      setIsAnimating(true);
      setHasMessages(false);
      setAqiAutoLoaded(false);
    } else {
      // Небольшая задержка перед полным скрытием для плавного закрытия
      const timer = setTimeout(() => {
        setIsAnimating(false);
      }, 300); // Длительность анимации
      return () => clearTimeout(timer);
    }
  }, [isOpen]);

  // Автоматическая загрузка AQI виджета при открытии
  useEffect(() => {
    if (isOpen && !aqiAutoLoaded && chatkit.control) {
      const timer = setTimeout(() => {
        try {
          if (chatkit.control && typeof chatkit.control.submitMessage === 'function') {
            chatkit.control.submitMessage('Покажи качество воздуха в Ташкенте');
            setAqiAutoLoaded(true);
          }
        } catch (error) {
          console.error('[ChatKit] Error auto-loading AQI:', error);
        }
      }, 1000);

      return () => clearTimeout(timer);
    }
  }, [isOpen, aqiAutoLoaded, chatkit.control]);

  // Блокируем скролл body когда ChatKit открыт (включая iOS)
  useEffect(() => {
    if (isOpen) {
      // Сохраняем текущую позицию скролла
      const scrollY = window.scrollY;
      document.body.style.overflow = 'hidden';
      document.body.style.position = 'fixed';
      document.body.style.top = `-${scrollY}px`;
      document.body.style.left = '0';
      document.body.style.right = '0';
      document.body.style.touchAction = 'none';
    }

    return () => {
      // Восстанавливаем скролл
      const scrollY = document.body.style.top;
      document.body.style.overflow = '';
      document.body.style.position = '';
      document.body.style.top = '';
      document.body.style.left = '';
      document.body.style.right = '';
      document.body.style.touchAction = '';
      window.scrollTo(0, parseInt(scrollY || '0') * -1);
    };
  }, [isOpen]);

  // Закрытие по клавише Escape
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, onClose]);

  if (!isOpen && !isAnimating) {
    return null;
  }

  return (
    <>
      {/* Overlay с плавным появлением */}
      <div
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          zIndex: 39,  // Ниже модального окна и footer'а
          opacity: isOpen ? 1 : 0,
          transition: 'opacity 0.3s ease-in-out',
          pointerEvents: isOpen ? 'auto' : 'none',
        }}
        onClick={onClose}
      />

      {/* Модальное окно с анимацией из-под footer */}
      <div
        ref={modalRef}
        className="chatkit-modal-container"
        style={{
          position: 'fixed',
          top: '5%',
          left: '50%',
          transform: isOpen
            ? 'translateX(-50%) translateY(0)'
            : 'translateX(-50%) translateY(calc(100% + 100px))',  // Уходит под footer
          width: 'min(800px, calc(100% - 40px))',  // Максимум 800px или 100% минус отступы
          bottom: '100px',  // Над footer'ом (высота footer ~80px + отступ)
          backgroundColor: backgroundColor,
          zIndex: 40,  // Ниже footer'а (footer z-50)
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          transition: 'transform 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.15)',
          borderRadius: '20px',
        }}
        role="dialog"
        aria-modal="true"
        aria-labelledby="chatkit-modal-title"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Заголовок модального окна */}
        <div
          style={{
            padding: '16px 20px',
            borderBottom: `1px solid ${theme === 'light' ? '#e5e5e5' : '#333'}`,
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            backgroundColor: theme === 'light' ? '#ffffff' : '#252525',
          }}
        >
          <h2
            id="chatkit-modal-title"
            style={{
              margin: 0,
              fontSize: '18px',
              fontWeight: 600,
              color: theme === 'light' ? '#1a1a1a' : '#ffffff',
            }}
          >
            Musaffo AI
          </h2>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '24px',
              cursor: 'pointer',
              color: theme === 'light' ? '#666' : '#aaa',
              padding: '4px 8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'color 0.2s',
            }}
            aria-label="Закрыть"
            onMouseEnter={(e) => {
              e.currentTarget.style.color = theme === 'light' ? '#000' : '#fff';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.color = theme === 'light' ? '#666' : '#aaa';
            }}
          >
            ×
          </button>
        </div>

        {/* ChatKit UI компонент */}
        <div
          style={{
            flex: 1,
            width: '100%',
            height: '100%',
            overflow: 'hidden',
            backgroundColor: backgroundColor,
          }}
        >
          <ChatKit
            control={chatkit.control}
            style={{
              height: '100%',
              width: '100%',
            }}
          />
        </div>
      </div>
    </>
  );
};

export default ChatKitModal;
