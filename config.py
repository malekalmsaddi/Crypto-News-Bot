import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Bot configuration
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '7542350946:AAHJD_P3Q2x42ScyWxDlq7KKcz4NdfuOCYk')
if not TELEGRAM_BOT_TOKEN:
    logging.error("Telegram bot token not found in environment variables!")

# Webhook configuration
WEBHOOK_URL = os.environ.get('WEBHOOK_URL', '')  # Empty default to enable polling mode
if not WEBHOOK_URL:
    logging.warning("Webhook URL not found in environment variables. The bot won't be able to receive webhooks.")

# Secret key for webhook authentication
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', 'crypto_news_webhook_secret_2025')
if WEBHOOK_SECRET == 'default_secret_key':
    logging.warning("Using default webhook secret key. This is not secure for production.")

# Flask configuration
PORT = int(os.environ.get('PORT', 5000))
HOST = '0.0.0.0'
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

# Database configuration
DATABASE_FILE = os.environ.get('DATABASE_FILE', 'bot_database.db')
