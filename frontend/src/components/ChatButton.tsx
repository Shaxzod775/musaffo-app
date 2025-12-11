import React from 'react';
import { MessageCircle } from 'lucide-react';

/**
 * ChatButton - Плавающая кнопка для открытия чата с AI
 */

interface ChatButtonProps {
  onClick: () => void;
  label?: string;
  theme?: 'dark' | 'light';
}

const ChatButton: React.FC<ChatButtonProps> = ({
  onClick,
  label = 'Musaffo AI',
  theme = 'dark'
}) => {
  const isDark = theme === 'dark';

  return (
    <button
      onClick={onClick}
      className="chat-button"
      style={{
        position: 'fixed',
        bottom: '90px', // Над нижней навигацией
        right: '20px',
        padding: '15px 25px',
        borderRadius: '30px',
        background: isDark
          ? 'linear-gradient(135deg, #10a37f, #0d8c6c)'
          : 'linear-gradient(135deg, #34c759, #30b350)',
        color: 'white',
        border: 'none',
        cursor: 'pointer',
        fontSize: '16px',
        fontWeight: 600,
        boxShadow: isDark
          ? '0 4px 15px rgba(16, 163, 127, 0.3)'
          : '0 4px 15px rgba(52, 199, 89, 0.3)',
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        zIndex: 1000,
        transition: 'all 0.3s ease',
        animation: 'pulse 2s infinite',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-2px) scale(1.05)';
        e.currentTarget.style.boxShadow = isDark
          ? '0 6px 20px rgba(16, 163, 127, 0.4)'
          : '0 6px 20px rgba(52, 199, 89, 0.4)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0) scale(1)';
        e.currentTarget.style.boxShadow = isDark
          ? '0 4px 15px rgba(16, 163, 127, 0.3)'
          : '0 4px 15px rgba(52, 199, 89, 0.3)';
      }}
      aria-label="Открыть чат с AI"
    >
      <MessageCircle size={20} />
      <span>{label}</span>

      <style>{`
        @keyframes pulse {
          0%, 100% {
            box-shadow: 0 4px 15px rgba(16, 163, 127, 0.3);
          }
          50% {
            box-shadow: 0 4px 25px rgba(16, 163, 127, 0.5);
          }
        }

        @media (max-width: 768px) {
          .chat-button {
            bottom: 80px !important;
            right: 15px !important;
            padding: 12px 20px !important;
            font-size: 14px !important;
          }
        }

        @media (max-width: 480px) {
          .chat-button span {
            display: none;
          }
          .chat-button {
            padding: 15px !important;
            border-radius: 50% !important;
          }
        }
      `}</style>
    </button>
  );
};

export default ChatButton;
