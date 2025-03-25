import os
import logging
from dotenv import load_dotenv
from pathlib import Path

# ✅ Load environment variables from .env file (explicit path)
load_dotenv(dotenv_path=Path('.') / '.env')

# ✅ Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# =========================
# 🔑 Bot Configuration
# =========================
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TELEGRAM_BOT_TOKEN:
    logging.critical("❌ TELEGRAM_BOT_TOKEN is missing in environment variables!")
    raise ValueError("TELEGRAM_BOT_TOKEN is required in .env or environment variables")

# =========================
# 🌐 Webhook Configuration
# =========================
WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')  # Optional: fallback to polling
if not WEBHOOK_URL:
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

logging.info(f"✅ Flask configuration - HOST: {HOST}, PORT: {PORT}, DEBUG: {DEBUG}")

# =========================
# 🗄 Database Configuration
# =========================
DATABASE_FILE = os.getenv('DATABASE_FILE', 'bot_database.db')
logging.info(f"✅ Database file: {DATABASE_FILE}")