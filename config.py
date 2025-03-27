import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# ✅ Load .env only if it exists (useful for local development)
dotenv_path = Path(__file__).resolve().parent / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path)
    logging.info("✅ .env loaded from local file")
else:
    logging.info("🌐 Running in production mode (Fly.io env vars expected)")

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
# Default webhook fallback for Fly.io (change as needed)
DEFAULT_FLY_WEBHOOK = "https://cryptonewsbot.fly.dev/telegram-webhook"

# ✅ Webhook URL: load from env or fallback to Fly.io URL
WEBHOOK_URL = os.getenv('WEBHOOK_URL', DEFAULT_FLY_WEBHOOK)
if WEBHOOK_URL == DEFAULT_FLY_WEBHOOK:
    logging.warning(f"⚠️ WEBHOOK_URL not set. Using default Fly.io webhook: {WEBHOOK_URL}")
else:
    logging.info(f"✅ Webhook URL loaded: {WEBHOOK_URL}")

# ✅ Webhook Secret is mandatory
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET')
if not WEBHOOK_SECRET:
    logging.critical("❌ WEBHOOK_SECRET is missing! Required for secure webhook communication.")
    raise RuntimeError("WEBHOOK_SECRET is required in .env o")
# =========================
# ⚙️ Flask Configuration
# =========================
# =========================
PORT = int(os.getenv('PORT', 8080))  # 8080 for Fly.io
HOST = os.getenv('HOST', '0.0.0.0')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Log Flask configuration
logging.info(f"✅ Flask configuration - HOST: {HOST}, PORT: {PORT}, DEBUG: {DEBUG}")

# =========================
# 🗄 Database Configuration
# =========================
DATABASE_FILE = os.getenv('DATABASE_FILE', 'bot_database.db')

# Log database configuration
logging.info(f"✅ Database file: {DATABASE_FILE}")