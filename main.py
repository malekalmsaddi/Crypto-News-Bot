import os
import logging
import asyncio
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
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.register_blueprint(webhook_bp)

# ✅ Initialize Database
database.init_db()

# ✅ Global State
application = None
flask_thread = None
shutting_down = False

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