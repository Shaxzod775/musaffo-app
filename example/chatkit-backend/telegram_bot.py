"""
Telegram Bot for Nyro AI Mini App
This bot provides a WebApp button to launch the AI chat interface.

Token: 8459996667:AAEc8-4FSauZcc5PpZvUT3LFuzn23zzpvaQ
"""
import os
import logging
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup, MenuButtonWebApp
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8459996667:AAEc8-4FSauZcc5PpZvUT3LFuzn23zzpvaQ')

# WebApp URL - deployed to Vercel
WEBAPP_URL = os.environ.get('TELEGRAM_WEBAPP_URL', 'https://dist-telegram.vercel.app')

# Translations
MESSAGES = {
    'ru': {
        'welcome': '''👋 Привет, {name}!

Я **Nyro AI** — твой умный помощник на базе искусственного интеллекта.

🚀 Что я умею:
• Отвечать на любые вопросы
• Помогать с учёбой и работой
• Генерировать тексты и документы
• Показывать погоду и качество воздуха
• Анализировать файлы и изображения

Нажми кнопку ниже, чтобы начать чат! 👇''',
        'button_text': '💬 Открыть чат',
        'help': '''📚 **Помощь**

Используйте кнопку меню или команду /start чтобы открыть AI чат.

Доступные команды:
• /start - Запустить бота
• /help - Показать помощь
• /chat - Открыть чат''',
    },
    'en': {
        'welcome': '''👋 Hello, {name}!

I'm **Nyro AI** — your smart AI-powered assistant.

🚀 What I can do:
• Answer any questions
• Help with study and work
• Generate texts and documents
• Show weather and air quality
• Analyze files and images

Press the button below to start chatting! 👇''',
        'button_text': '💬 Open Chat',
        'help': '''📚 **Help**

Use the menu button or /start command to open AI chat.

Available commands:
• /start - Start the bot
• /help - Show help
• /chat - Open chat''',
    },
    'uz': {
        'welcome': '''👋 Salom, {name}!

Men **Nyro AI** — sun'iy intellektga asoslangan aqlli yordamchingizman.

🚀 Men nima qila olaman:
• Har qanday savollarga javob berish
• O'qish va ishda yordam berish
• Matn va hujjatlar yaratish
• Ob-havo va havo sifatini ko'rsatish
• Fayl va rasmlarni tahlil qilish

Chat boshlash uchun quyidagi tugmani bosing! 👇''',
        'button_text': '💬 Chatni ochish',
        'help': '''📚 **Yordam**

AI chatni ochish uchun menyu tugmasidan yoki /start buyrug'idan foydalaning.

Mavjud buyruqlar:
• /start - Botni ishga tushirish
• /help - Yordamni ko'rsatish
• /chat - Chatni ochish''',
    }
}


def get_language(user) -> str:
    """Get user language, default to Russian"""
    lang_code = user.language_code or 'ru'
    if lang_code.startswith('uz'):
        return 'uz'
    elif lang_code.startswith('en'):
        return 'en'
    return 'ru'


def get_message(user, key: str) -> str:
    """Get translated message for user"""
    lang = get_language(user)
    messages = MESSAGES.get(lang, MESSAGES['ru'])
    return messages.get(key, MESSAGES['ru'].get(key, ''))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send welcome message with WebApp button"""
    user = update.effective_user
    lang = get_language(user)

    welcome_text = get_message(user, 'welcome').format(name=user.first_name)
    button_text = get_message(user, 'button_text')

    # Create WebApp button
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text=button_text,
            web_app=WebAppInfo(url=WEBAPP_URL)
        )]
    ])

    await update.message.reply_text(
        welcome_text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

    logger.info(f"User {user.id} ({user.username}) started the bot")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show help message"""
    user = update.effective_user
    help_text = get_message(user, 'help')

    await update.message.reply_text(help_text, parse_mode='Markdown')


async def chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Open chat via WebApp button"""
    user = update.effective_user
    button_text = get_message(user, 'button_text')

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text=button_text,
            web_app=WebAppInfo(url=WEBAPP_URL)
        )]
    ])

    await update.message.reply_text(
        "👇 Нажмите кнопку чтобы открыть чат:",
        reply_markup=keyboard
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle regular messages - prompt to use WebApp"""
    user = update.effective_user
    button_text = get_message(user, 'button_text')

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            text=button_text,
            web_app=WebAppInfo(url=WEBAPP_URL)
        )]
    ])

    await update.message.reply_text(
        "💡 Для общения с AI используйте кнопку ниже:",
        reply_markup=keyboard
    )


async def post_init(application: Application) -> None:
    """Set up bot menu button after initialization"""
    try:
        # Set menu button to open WebApp
        await application.bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(
                text="💬 Nyro AI",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
        )
        logger.info("Menu button configured successfully")
    except Exception as e:
        logger.error(f"Failed to set menu button: {e}")


def main() -> None:
    """Start the bot"""
    # Create application
    application = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("chat", chat_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot
    logger.info("Starting Nyro AI Telegram Bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
