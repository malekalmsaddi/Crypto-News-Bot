import os
import logging
import asyncio
from flask import Flask
from hypercorn.asyncio import serve
from hypercorn.config import Config
from config import HOST, PORT, DEBUG
import database
from webhook import webhook_bp
from bot import run_bot, get_bot_username  # Fixed imports

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.register_blueprint(webhook_bp)

# Initialize the database
database.init_db()

# Global variable for bot username
bot_username = None

async def start_bot_and_set_username():
    """Initialize the Telegram bot and fetch username asynchronously."""
    global bot_username
    try:
        # Initialize bot first
        await run_bot()
        
        # Now get username after bot is running
        bot_username = await get_bot_username()
        logger.info(f"Bot username: @{bot_username}")
        
    except Exception as e:
        logger.error(f"Failed to initialize bot: {e}", exc_info=True)
        raise

@app.before_request
def set_bot_info():
    """Set the bot's information for templates."""
    app.jinja_env.globals['bot_username'] = bot_username

async def run_web_server():
    """Run Flask app using Hypercorn async server."""
    config = Config()
    config.bind = [f"{HOST}:{PORT}"]
    await serve(app, config)

async def main():
    """Main async entry point."""
    # Start bot and web server concurrently
    await asyncio.gather(
        start_bot_and_set_username(),
        run_web_server()
    )

if __name__ == "__main__":
    # Start the async event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        loop.close()