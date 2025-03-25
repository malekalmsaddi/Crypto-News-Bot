import os
import logging
import asyncio
<<<<<<< HEAD
import threading
import signal
from flask import Flask, jsonify
from config import HOST, PORT, DEBUG
import database
from webhook import webhook_bp
from bot import setup_bot, get_bot_username
from werkzeug.serving import make_server
from market import start_market_fetcher

# ✅ Configure Flask App
=======
import signal
from flask import Flask
from hypercorn.asyncio import serve
from hypercorn.config import Config
from config import HOST, PORT, DEBUG
import database
from webhook import webhook_bp
from bot import run_bot, get_bot_username, application

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Flask app
>>>>>>> upstream/main
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.register_blueprint(webhook_bp)

# ✅ Initialize Database
database.init_db()

<<<<<<< HEAD
# ✅ Global State
application = None
flask_thread = None
shutting_down = False
=======
# Global variable for bot username
bot_username = None
>>>>>>> upstream/main

# ✅ Configure Logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# ✅ Flask Server Thread Class
class FlaskServerThread(threading.Thread):
    def __init__(self, app):
        super().__init__()
        self.server = make_server(HOST, PORT, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        logging.info("✅ Flask server starting...")
        self.server.serve_forever()

    def shutdown(self):
        logging.info("🛑 Flask server shutting down...")
        self.server.shutdown()

# ✅ Optional: Block requests during shutdown
@app.before_request
<<<<<<< HEAD
def reject_during_shutdown():
    if shutting_down:
        return jsonify({"error": "Service is shutting down"}), 503

async def run_bot():
    global application
    try:
        # ✅ Get bot username
        bot_username = await get_bot_username()
        app.jinja_env.globals['bot_username'] = bot_username

        # ✅ Setup the bot
        application = await setup_bot()

        # ✅ Inject the bot application into webhook
        from webhook import set_bot_application
        set_bot_application(application)

        # ✅ Start the bot lifecycle
        await application.initialize()
        await application.start()
        logging.info("✅ Bot started successfully.")

        # ✅ Keep the bot running
        while True:
            await asyncio.sleep(1)

    except asyncio.CancelledError:
        logging.info("✅ Bot task cancelled. Shutting down...")
    except Exception as e:
        logging.error(f"❌ Failed to initialize bot: {e}")
        raise e
    finally:
        if application:
            try:
                await application.stop()
                await application.shutdown()
            except RuntimeError as e:
                logging.warning(f"Bot shutdown warning: {e}")

async def shutdown():
    global shutting_down
    shutting_down = True
    logging.info("🛑 Graceful shutdown initiated...")

    if application:
        try:
            await application.stop()
            await application.shutdown()
        except RuntimeError as e:
            logging.warning(f"Bot shutdown warning: {e}")

    if flask_thread:
        flask_thread.shutdown()

    logging.info("✅ Application shutdown complete.")

async def main():
    global flask_thread

    # ✅ Signal handling for graceful shutdown
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown()))

    # ✅ Start market fetcher (AFTER loop is ready)
    start_market_fetcher()

    # ✅ Start Flask in a background thread
    flask_thread = FlaskServerThread(app)
    flask_thread.start()

    # ✅ Start the bot
    bot_task = asyncio.create_task(run_bot())

    try:
        while flask_thread.is_alive():
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        logging.info("Main async task cancelled.")
    finally:
        bot_task.cancel()
        await bot_task

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("🛑 Application interrupted by user (CTRL+C). Shutting down...")
=======
def set_bot_info():
    """Set bot info for templates (sync context)."""
    app.jinja_env.globals['bot_username'] = bot_username

async def start_bot():
    """Run the Telegram bot and set the webhook."""
    try:
        global bot_username
        bot_username = await get_bot_username()
        logger.info(f"Bot username: @{bot_username}")

        # ✅ Set the webhook URL dynamically (replace this with your deployed URL)
        webhook_url = "https://cryptonewsbot.fly.dev/telegram-webhook"
        await application.bot.set_webhook(webhook_url)
        logger.info(f"Webhook set to: {webhook_url}")

        # Run the bot (scheduler starts inside)
        await run_bot()
    except Exception as e:
        logger.error(f"Failed to initialize bot: {e}", exc_info=True)
        raise

async def run_web_server():
    """Run the Flask web server."""
    config = Config()
    config.bind = [f"{HOST}:{PORT}"]
    config.debug = DEBUG
    await serve(app, config)

async def main():
    """Main entry point."""
    try:
        # Run both Flask and Bot concurrently
        await asyncio.gather(
            run_web_server(),
            start_bot()
        )
    except asyncio.CancelledError:
        logger.info("Main task cancelled. Shutting down...")
    finally:
        # Properly stop the bot to avoid loop issues
        if application:
            await application.stop()
            await application.shutdown()

def handle_shutdown(signum, frame):
    """Handle shutdown signals."""
    logger.info("Received shutdown signal. Stopping bot...")
    loop = asyncio.get_event_loop()
    loop.create_task(application.stop())
    loop.create_task(application.shutdown())

if __name__ == '__main__':
    import asyncio
    from bot import run_bot
    from webhook import webhook_bp

    app = Flask(__name__)
    app.register_blueprint(webhook_bp)

    loop = asyncio.get_event_loop()
    loop.create_task(run_bot())  # Keeps PTB running in the background
    app.run(host='0.0.0.0', port=8080)
>>>>>>> upstream/main
