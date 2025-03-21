
import os
import logging
from flask import Flask
from config import HOST, PORT, DEBUG
import database
from webhook import webhook_bp
from bot import setup_bot, get_bot_username

# Configure app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.register_blueprint(webhook_bp)

# Initialize database
database.init_db()

# Get the bot's username
bot_username = get_bot_username()

@app.before_request
def set_bot_info():
    """Set the bot's information for the template."""
    app.jinja_env.globals['bot_username'] = bot_username

def run_bot():
    """Initialize the bot in the background."""
    try:
        updater = setup_bot()
        updater.start_polling(drop_pending_updates=True)
        logging.info("Bot initialized successfully!")
        updater.idle()
    except Exception as e:
        logging.error(f"Failed to initialize bot: {e}")
        raise e

if __name__ == "__main__":
    run_bot()
