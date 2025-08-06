#!/bin/bash

# Setup script for DocExpert Bot deployment
# This script ensures proper directory permissions and setup

echo "🚀 Setting up DocExpert Bot environment..."

# Create required directories
echo "📁 Creating required directories..."
mkdir -p uploads logs

# Set proper permissions
echo "🔒 Setting directory permissions..."
chmod 755 uploads logs

# Set write permissions for logs
chmod 766 logs

# Create initial log file if it doesn't exist
touch logs/bot.log 2>/dev/null || echo "⚠️ Could not create initial log file (will use console logging)"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file template..."
    cat > .env << 'EOF'
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# AI API Keys
XAI_API_KEY=your_xai_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here

# MongoDB Atlas Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/database
MONGODB_DB_NAME=telegram_bot

# Service Configuration
EMBEDDING_SERVICE=huggingface
LOG_LEVEL=INFO

# Optional: YouTube API (for transcript features)
YOUTUBE_API_KEY=your_youtube_api_key_here
EOF
    echo "✅ .env template created! Please edit it with your API keys."
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run 'docker-compose up --build' to start the bot"
echo "3. Check logs with 'docker-compose logs -f telegram-bot'"
echo ""
echo "🔗 Useful commands:"
echo "   make run     - Start the bot"
echo "   make logs    - View logs"
echo "   make stop    - Stop the bot"
echo "   make health  - Check bot health"
echo ""
