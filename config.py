import os
import logging
<<<<<<< HEAD
from dotenv import load_dotenv
from pathlib import Path
=======
import sys
>>>>>>> upstream/main

# ✅ Load environment variables from .env file (explicit path)
load_dotenv(dotenv_path=Path('.') / '.env')

# ✅ Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

<<<<<<< HEAD
# =========================
# 🔑 Bot Configuration
# =========================
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TELEGRAM_BOT_TOKEN:
    logging.critical("❌ TELEGRAM_BOT_TOKEN is missing in environment variables!")
    raise ValueError("TELEGRAM_BOT_TOKEN is required in .env or environment variables")
=======
# Bot configuration (No hardcoded token fallback)
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
if not TELEGRAM_BOT_TOKEN:
    logging.critical("❌ TELEGRAM_BOT_TOKEN not set! Exiting for security reasons.")
    sys.exit(1)
>>>>>>> upstream/main

# =========================
# 🌐 Webhook Configuration
# =========================
WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')  # Optional: fallback to polling
if not WEBHOOK_URL:
<<<<<<< HEAD
    logging.warning("⚠️ WEBHOOK_URL is not set. Webhook mode disabled, bot will fallback to polling.")

WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET')
if not WEBHOOK_SECRET:
    logging.critical("❌ WEBHOOK_SECRET is missing! Required for secure webhook communication.")
    raise ValueError("WEBHOOK_SECRET is required in .env or environment variables")

# =========================
# ⚙️ Flask Configuration
# =========================
PORT = int(os.getenv('PORT', 5000))
HOST = os.getenv('HOST', '0.0.0.0')
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
=======
    logging.warning("Webhook URL not set. Bot will default to polling mode if used.")

# Secret key for webhook authentication (Use env for production)
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', 'crypto_news_webhook_secret_2025')
if WEBHOOK_SECRET == 'crypto_news_webhook_secret_2025':
    logging.warning("Using default WEBHOOK_SECRET. Set a secure one in production!")

# Flask configuration
PORT = int(os.environ.get('PORT', 8080))
HOST = '0.0.0.0'
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
>>>>>>> upstream/main

logging.info(f"✅ Flask configuration - HOST: {HOST}, PORT: {PORT}, DEBUG: {DEBUG}")

# =========================
# 🗄 Database Configuration
# =========================
DATABASE_FILE = os.getenv('DATABASE_FILE', 'bot_database.db')
logging.info(f"✅ Database file: {DATABASE_FILE}")