/**
 * Telegram Web App Hook
 * Provides access to Telegram Mini App functionality
 */

// Telegram Web App types
declare global {
    interface Window {
        Telegram?: {
            WebApp: TelegramWebApp;
        };
    }
}

interface TelegramWebApp {
    initData: string;
    initDataUnsafe: {
        query_id?: string;
        user?: TelegramUser;
        auth_date?: number;
        hash?: string;
        start_param?: string;
    };
    version: string;
    platform: string;
    colorScheme: 'light' | 'dark';
    themeParams: ThemeParams;
    isExpanded: boolean;
    viewportHeight: number;
    viewportStableHeight: number;
    headerColor: string;
    backgroundColor: string;
    isClosingConfirmationEnabled: boolean;
    BackButton: BackButton;
    MainButton: MainButton;
    HapticFeedback: HapticFeedback;

    ready(): void;
    expand(): void;
    close(): void;
    sendData(data: string): void;
    openLink(url: string, options?: { try_instant_view?: boolean }): void;
    openTelegramLink(url: string): void;
    openInvoice(url: string, callback?: (status: string) => void): void;
    showPopup(params: PopupParams, callback?: (button_id: string) => void): void;
    showAlert(message: string, callback?: () => void): void;
    showConfirm(message: string, callback?: (confirmed: boolean) => void): void;
    enableClosingConfirmation(): void;
    disableClosingConfirmation(): void;
    setHeaderColor(color: string): void;
    setBackgroundColor(color: string): void;
    onEvent(eventType: string, eventHandler: () => void): void;
    offEvent(eventType: string, eventHandler: () => void): void;
}

interface TelegramUser {
    id: number;
    is_bot?: boolean;
    first_name: string;
    last_name?: string;
    username?: string;
    language_code?: string;
    is_premium?: boolean;
    photo_url?: string;
}

interface ThemeParams {
    bg_color?: string;
    text_color?: string;
    hint_color?: string;
    link_color?: string;
    button_color?: string;
    button_text_color?: string;
    secondary_bg_color?: string;
}

interface BackButton {
    isVisible: boolean;
    onClick(callback: () => void): void;
    offClick(callback: () => void): void;
    show(): void;
    hide(): void;
}

interface MainButton {
    text: string;
    color: string;
    textColor: string;
    isVisible: boolean;
    isActive: boolean;
    isProgressVisible: boolean;
    setText(text: string): void;
    onClick(callback: () => void): void;
    offClick(callback: () => void): void;
    show(): void;
    hide(): void;
    enable(): void;
    disable(): void;
    showProgress(leaveActive?: boolean): void;
    hideProgress(): void;
    setParams(params: { text?: string; color?: string; text_color?: string; is_active?: boolean; is_visible?: boolean }): void;
}

interface HapticFeedback {
    impactOccurred(style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft'): void;
    notificationOccurred(type: 'error' | 'success' | 'warning'): void;
    selectionChanged(): void;
}

interface PopupParams {
    title?: string;
    message: string;
    buttons?: Array<{
        id?: string;
        type?: 'default' | 'ok' | 'close' | 'cancel' | 'destructive';
        text?: string;
    }>;
}

export function useTelegram() {
    const tg = window.Telegram?.WebApp;

    const isTelegramWebApp = !!tg?.initData;

    const user = tg?.initDataUnsafe?.user;

    const colorScheme = tg?.colorScheme || 'light';

    const ready = () => {
        tg?.ready();
    };

    const expand = () => {
        tg?.expand();
    };

    const close = () => {
        tg?.close();
    };

    const showAlert = (message: string, callback?: () => void) => {
        if (tg) {
            tg.showAlert(message, callback);
        } else {
            alert(message);
            callback?.();
        }
    };

    const showConfirm = (message: string, callback?: (confirmed: boolean) => void) => {
        if (tg) {
            tg.showConfirm(message, callback);
        } else {
            const result = confirm(message);
            callback?.(result);
        }
    };

    const hapticFeedback = {
        impact: (style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft' = 'medium') => {
            tg?.HapticFeedback?.impactOccurred(style);
        },
        notification: (type: 'error' | 'success' | 'warning') => {
            tg?.HapticFeedback?.notificationOccurred(type);
        },
        selection: () => {
            tg?.HapticFeedback?.selectionChanged();
        },
    };

    const mainButton = {
        show: (text: string, onClick: () => void) => {
            if (tg?.MainButton) {
                tg.MainButton.setText(text);
                tg.MainButton.onClick(onClick);
                tg.MainButton.show();
            }
        },
        hide: () => {
            tg?.MainButton?.hide();
        },
        showProgress: () => {
            tg?.MainButton?.showProgress();
        },
        hideProgress: () => {
            tg?.MainButton?.hideProgress();
        },
    };

    const backButton = {
        show: (onClick: () => void) => {
            if (tg?.BackButton) {
                tg.BackButton.onClick(onClick);
                tg.BackButton.show();
            }
        },
        hide: () => {
            tg?.BackButton?.hide();
        },
    };

    const openLink = (url: string) => {
        if (tg) {
            tg.openLink(url);
        } else {
            window.open(url, '_blank');
        }
    };

    const openTelegramLink = (url: string) => {
        if (tg) {
            tg.openTelegramLink(url);
        } else {
            window.open(url, '_blank');
        }
    };

    const setHeaderColor = (color: string) => {
        tg?.setHeaderColor(color);
    };

    const setBackgroundColor = (color: string) => {
        tg?.setBackgroundColor(color);
    };

    return {
        tg,
        isTelegramWebApp,
        user,
        colorScheme,
        ready,
        expand,
        close,
        showAlert,
        showConfirm,
        hapticFeedback,
        mainButton,
        backButton,
        openLink,
        openTelegramLink,
        setHeaderColor,
        setBackgroundColor,
        themeParams: tg?.themeParams,
        viewportHeight: tg?.viewportHeight,
        platform: tg?.platform,
    };
}

export type { TelegramWebApp, TelegramUser, ThemeParams };
