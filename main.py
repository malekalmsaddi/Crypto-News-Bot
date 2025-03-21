import os
import asyncio
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
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        bot_app = loop.run_until_complete(setup_bot())
        logging.info("Bot initialized successfully!")
    except Exception as e:
        logging.error(f"Failed to initialize bot: {e}")

if __name__ == "__main__":
    # Start the bot in a separate thread
    import threading
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Start the Flask web server
    app.run(host=HOST, port=PORT, debug=DEBUG)
