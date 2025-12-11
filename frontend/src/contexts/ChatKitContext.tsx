import React, { createContext, useContext, useState, ReactNode } from 'react';

/**
 * Context для управления состоянием ChatKit модального окна
 */

interface ChatKitContextType {
  isChatOpen: boolean;
  openChat: () => void;
  closeChat: () => void;
  toggleChat: () => void;
}

const ChatKitContext = createContext<ChatKitContextType | undefined>(undefined);

export const useChatKit = () => {
  const context = useContext(ChatKitContext);
  if (!context) {
    throw new Error('useChatKit must be used within a ChatKitProvider');
  }
  return context;
};

interface ChatKitProviderProps {
  children: ReactNode;
}

export const ChatKitProvider: React.FC<ChatKitProviderProps> = ({ children }) => {
  const [isChatOpen, setIsChatOpen] = useState(false);

  const openChat = () => setIsChatOpen(true);
  const closeChat = () => setIsChatOpen(false);
  const toggleChat = () => setIsChatOpen(prev => !prev);

  return (
    <ChatKitContext.Provider
      value={{
        isChatOpen,
        openChat,
        closeChat,
        toggleChat,
      }}
    >
      {children}
    </ChatKitContext.Provider>
  );
};
