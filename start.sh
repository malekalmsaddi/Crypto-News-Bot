#!/bin/bash

echo "🔧 Starting CryptoNewsBot..."

# Activate virtual environment
source venv/bin/activate

# Check if .env exists (local development)
if [ -f .env ]; then
    echo "🧪 Local environment detected. Loading .env..."
    export $(grep -v '^#' .env | xargs)
    echo "🌐 Loaded WEBHOOK_URL from .env: $WEBHOOK_URL"
else
    echo "🚀 Production mode. No .env file found."
fi

# Debug: Show key environment variables
echo "✅ Using TELEGRAM_BOT_TOKEN (masked): ${TELEGRAM_BOT_TOKEN:0:5}...[HIDDEN]"
echo "✅ Webhook: $WEBHOOK_URL"

# Run the bot
python main.py
