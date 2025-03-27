#!/bin/bash

echo "🔧 Starting CryptoNewsBot..."

# Activate virtual environment
source venv/bin/activate

# Unset any globally exported webhook override (just in case)
unset WEBHOOK_URL

# Optional: Print .env webhook for visual confirmation
echo "🌐 Webhook from .env:"
grep WEBHOOK_URL .env

# Run the bot
python main.py
