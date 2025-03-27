from dotenv import load_dotenv
import os
import logging
from pathlib import Path

# ✅ Load .env from the current directory only
dotenv_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

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
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
if not WEBHOOK_URL:
    logging.warning("⚠️ WEBHOOK_URL is not set. Bot will use polling.")
else:
    logging.info(f"✅ Webhook URL loaded: {WEBHOOK_URL}")

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