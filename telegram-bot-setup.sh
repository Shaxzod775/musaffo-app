#!/bin/bash

# Telegram Bot Setup Script for Musaffo Mini App
# Bot Token: 8459996667:AAEc8-4FSauZcc5PpZvUT3LFuzn23zzpvaQ

BOT_TOKEN="8459996667:AAEc8-4FSauZcc5PpZvUT3LFuzn23zzpvaQ"
WEBAPP_URL="https://air-quality-eco-fund-2.vercel.app"

echo "🤖 Setting up Telegram Bot for Musaffo Mini App..."

# Set bot commands
echo "📝 Setting bot commands..."
curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/setMyCommands" \
  -H "Content-Type: application/json" \
  -d '{
    "commands": [
      {"command": "start", "description": "🚀 Запустить приложение"},
      {"command": "air", "description": "🌬️ Качество воздуха"},
      {"command": "donate", "description": "💚 Сделать пожертвование"},
      {"command": "help", "description": "❓ Помощь"}
    ]
  }'

echo ""

# Set Menu Button to open Web App
echo "🔘 Setting menu button..."
curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/setChatMenuButton" \
  -H "Content-Type: application/json" \
  -d "{
    \"menu_button\": {
      \"type\": \"web_app\",
      \"text\": \"🌿 Musaffo\",
      \"web_app\": {
        \"url\": \"${WEBAPP_URL}\"
      }
    }
  }"

echo ""

# Get bot info
echo "ℹ️ Bot info:"
curl -s "https://api.telegram.org/bot${BOT_TOKEN}/getMe" | python3 -m json.tool

echo ""
echo "✅ Setup complete!"
echo ""
echo "📱 Your Mini App URL: ${WEBAPP_URL}"
echo "🔗 Bot link: https://t.me/musaffo_bot"
