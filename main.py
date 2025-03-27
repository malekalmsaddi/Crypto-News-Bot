# main.py
import os
import logging
import asyncio
import threading
import signal
from flask import Flask, jsonify
from werkzeug.serving import make_server
from config import HOST, PORT, DEBUG, TELEGRAM_BOT_TOKEN, WEBHOOK_URL, WEBHOOK_SECRET
import database
from webhook import webhook_bp, set_bot_application
from market import start_market_fetcher, stop_market_fetcher
from telegram.ext import ApplicationBuilder
from bot import get_bot_username, setup_handlers, send_hourly_price_update

# ========== Logging Setup ==========
class SensitiveFilter(logging.Filter):
    def filter(self, record):
        msg = record.getMessage()
        # Hide your Bot token in logs
        if "api.telegram.org/bot" in msg:
            record.msg = msg.replace(TELEGRAM_BOT_TOKEN, '[REDACTED]')
        return True

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger("telegram").addFilter(SensitiveFilter())
logging.getLogger().addFilter(SensitiveFilter())

# ========== Globals ==========
application = None        # The telegram.ext.Application
flask_thread = None
shutting_down = False
shutdown_lock = asyncio.Lock()

# ========== Flask Setup ==========
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "SomeRandomSecret")
app.register_blueprint(webhook_bp)
database.init_db()

@app.before_request
def reject_if_shutting_down():
    if shutting_down:
        return jsonify({"error": "Service is shutting down"}), 503

class FlaskServerThread(threading.Thread):
    """
    Runs the Flask server in a separate thread so we don’t block the main event loop.
    """
    def __init__(self, app):
        super().__init__()
        self.server = make_server(HOST, PORT, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        import asyncio
        asyncio.set_event_loop(asyncio.new_event_loop())  # ✅ Ensure this thread has its own event loop
        logging.info("✅ Flask server starting...")
        self.server.serve_forever()


    def shutdown(self):
        logging.info("🛑 Flask server shutting down...")
        self.server.shutdown()
        self.server.server_close()

# ========== Shutdown Logic ==========
async def shutdown():
    """
    Perform a clean shutdown of Flask + the telegram bot + background tasks.
    """
    global shutting_down
    async with shutdown_lock:
        if shutting_down:
            return
        shutting_down = True
        logging.info("🛑 Initiating clean shutdown...")

        # 1. Stop Flask thread
        if flask_thread:
            flask_thread.shutdown()
            flask_thread.join(timeout=5)

        # 2. Stop the bot application
        if application:
            try:
                await application.stop()
                await application.shutdown()
            except Exception as e:
                logging.warning(f"⚠️ Telegram shutdown issue: {e}")

        # 3. Stop market fetcher
        stop_market_fetcher()

        # 4. Cancel remaining tasks
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

# ========== Bot Initialization & Main Logic ==========
async def run_bot():
    """
    Starts the bot *without* automatic polling or integrated webhook server.
    We rely on our own Flask route to deliver updates to application.process_update().
    """
    global application

    logging.info("⚡ Initializing bot components...")

    # Start any background tasks (market fetching, etc.)
    start_market_fetcher()

    # 1. Build the PTB application
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # 2. Make the bot available to the webhook blueprint
    set_bot_application(application)

    # 3. Register all handlers
    setup_handlers(application)

    # 4. Optionally schedule background jobs
    application.job_queue.run_repeating(send_hourly_price_update, interval=20000, first=3600)

    # 5. Actually initialize & start the bot in the background
    await application.initialize()
    await application.start()
    await asyncio.sleep(2)

    # 6. Set the webhook once, so Telegram pushes updates to /telegram-webhook
    fallback_url = "https://cryptonewsbot.fly.dev/telegram-webhook"
    webhook_url = os.getenv("WEBHOOK_URL", fallback_url)

    if webhook_url == fallback_url:
        logging.warning(f"⚠️ WEBHOOK_URL not set. Using default Fly.io webhook: {webhook_url}")
    else:
        logging.info(f"✅ WEBHOOK_URL loaded: {webhook_url}")

    try:
        await application.bot.set_webhook(url=webhook_url)
        logging.info(f"✅ Telegram webhook set to: {webhook_url}")
    except Exception as e:
        logging.exception(f"❌ Failed to set Telegram webhook: {e}")

    # 7. Keep this task alive until we’re shutting down
    bot_username = await get_bot_username()
    logging.info(f"✅ Bot username set: @{bot_username}")

    while not shutting_down:
        await asyncio.sleep(1)

async def main():
    """
    Main entrypoint: start Flask in one thread, then run the bot in the current event loop.
    """
    global flask_thread

    # Start Flask server in a separate thread so it can handle webhooks & other routes
    flask_thread = FlaskServerThread(app)
    flask_thread.start()

    try:
        # Start the Telegram bot in the current event loop
        await run_bot()
    except (asyncio.CancelledError, KeyboardInterrupt):
        logging.info("🛑 Shutdown triggered by interrupt")
        await shutdown()

# ========== Signal Handling ==========
def handle_signal(signum, frame):
    """
    Called by Python’s signal module on SIGINT/SIGTERM to do graceful shutdown.
    """
    logging.info(f"🛑 Received signal {signum}, initiating shutdown...")
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(shutdown())
    except RuntimeError:
        logging.warning("⚠️ No running event loop, skipping async shutdown")

if __name__ == '__main__':
    # Register signal handlers so we can gracefully stop on Ctrl+C or kill
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    # Finally, run everything
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("🛑 Keyboard interrupt received")
