import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the bot token
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

if TELEGRAM_BOT_TOKEN:
    print(f"Loaded TELEGRAM_BOT_TOKEN: {TELEGRAM_BOT_TOKEN[:4]}...{TELEGRAM_BOT_TOKEN[-4:]}")
else:
    print("Telegram bot token not found!")
