import os
import logging
import asyncio
import threading
import signal

from flask import Flask, jsonify, render_template
from werkzeug.serving import make_server
from webhook import webhook_bp
from config import HOST, PORT, DEBUG, TELEGRAM_BOT_TOKEN, WEBHOOK_URL, WEBHOOK_SECRET
import database
import shared
from market import start_market_fetcher, stop_market_fetcher
from telegram.ext import ApplicationBuilder
from bot import get_bot_username, setup_handlers, send_hourly_price_update
from threading import Event as ThreadingEvent
from shared import (
    set_telegram_app,
    is_shutting_down,
    set_shutting_down,
    shutdown_lock,
    async_shutdown_lock,
    flask_app  # ✅ Using single shared instance
)

# ========== env logic ==========
if os.path.exists(".env"):
    from dotenv import load_dotenv
    load_dotenv()
    print(f"📦 WEBHOOK_URL from env: {os.getenv('WEBHOOK_URL')}")

# ========== Logging Setup ==========
class SensitiveFilter(logging.Filter):
    def filter(self, record):
        msg = record.getMessage()
        if "api.telegram.org/bot" in msg:
            record.msg = msg.replace(TELEGRAM_BOT_TOKEN, '[REDACTED]')
        return True

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger("telegram").addFilter(SensitiveFilter())
logging.getLogger().addFilter(SensitiveFilter())

# ========== Globals ==========
application = None
flask_thread = None
shutdown_async_event = None
shutdown_event = ThreadingEvent()
shared.shutdown_event = shutdown_event
flask_app.secret_key = os.environ.get("SESSION_SECRET", "SomeRandomSecret")
flask_app.register_blueprint(webhook_bp)

print("📍 Registered Flask routes:")
for rule in flask_app.url_map.iter_rules():
    print(f"{rule.methods} {rule.rule}")

database.init_db()

@flask_app.route("/test-html")
def test_html():
    print("📄 Serving HTML template")
    return render_template("index.html")

@flask_app.before_request
def reject_if_shutting_down():
    if is_shutting_down():
        return jsonify({"error": "Service is shutting down"}), 503

class FlaskServerThread(threading.Thread):
    def __init__(self, app):
        print("📡 FlaskServerThread initialized")
        super().__init__()
        self.server = make_server("0.0.0.0", PORT, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        logging.info("✅ Flask server starting...")
        self.server.serve_forever()

    def shutdown(self):
        logging.info("🛑 Flask server shutting down...")
        self.server.shutdown()
        self.server.server_close()

# ========== Shutdown Logic ==========
async def shutdown(shutdown_event):
    print('🛠️ [shutdown] Acquiring shutdown lock...')
    async with async_shutdown_lock:
        if is_shutting_down():
            print('🚫 [shutdown] Already shutting down. Aborting.')
            return

        set_shutting_down(True)
        print('🔒 [shutdown] Shutdown flag set - rejecting new requests')
        logging.info("🛑 Initiating clean shutdown sequence...")

        try:
            shutdown_async_event.set()
            print('✅ [shutdown] Async components notified')

            if flask_thread and flask_thread.is_alive():
                flask_thread.shutdown()
                flask_thread.join(timeout=5)
                if flask_thread.is_alive():
                    logging.warning("Flask server didn't terminate gracefully")
                print('✅ [shutdown] Flask server stopped')

            if application:
                try:
                    await application.stop()
                    await application.shutdown()
                    print('💤 [shutdown] Telegram application shutdown complete')
                except Exception as e:
                    logging.error(f"Telegram shutdown failed: {str(e)}")

            stop_market_fetcher()
            print('✅ [shutdown] Market fetcher stopped')

            current_task = asyncio.current_task()
            tasks = [t for t in asyncio.all_tasks() if t is not current_task]
            for task in tasks:
                task.cancel()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for task, result in zip(tasks, results):
                if isinstance(result, Exception):
                    logging.warning(f"Task {task.get_name()} failed during shutdown: {str(result)}")

            print('✅ [shutdown] Background tasks cleared')

        except Exception as e:
            logging.critical(f"🆘 Critical shutdown error: {str(e)}")
            raise
        finally:
            logging.info("🛑 Shutdown sequence completed")

# ========== Bot Logic ==========
async def run_bot(shutdown_event):
    global application
    print("🤖 [run_bot] Initializing...")
    logging.info("⚡ Initializing bot components...")

    start_market_fetcher()
    print("✅ Returned from start_market_fetcher()")

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    set_telegram_app(application)
    setup_handlers(application)

    application.job_queue.run_repeating(send_hourly_price_update, interval=20000, first=3600)

    await application.initialize()
    await application.start()

    try:
        await application.bot.delete_webhook(drop_pending_updates=True)
        logging.info("🧹 Old webhook deleted")
    except Exception as e:
        logging.warning(f"⚠️ Failed to delete old webhook: {e}")

    try:
        await application.bot.set_webhook(
            url=WEBHOOK_URL,
            secret_token=WEBHOOK_SECRET
        )
        logging.info(f"✅ Webhook successfully registered at: {WEBHOOK_URL}")
    except Exception as e:
        logging.exception(f"❌ Failed to set Telegram webhook: {e}")

    bot_username = await get_bot_username()
    logging.info(f"✅ Bot username: @{bot_username}")

    set_shutting_down(False)
    print("✅ Bot is now accepting requests")
    print("🟢 [run_bot] Bot fully initialized — waiting for shutdown...")

    try:
        webhook_info = await application.bot.get_webhook_info()
        print(f"🌐 Webhook Info: URL = {webhook_info.url}, Pending Updates = {webhook_info.pending_update_count}")
    except Exception as e:
        print(f"❌ Failed to fetch webhook info: {e}")

    try:
        me = await application.bot.get_me()
        print(f"🤖 Bot Identity: @{me.username}, ID = {me.id}")
    except Exception as e:
        print(f"❌ Failed to fetch bot identity: {e}")

    try:
        chat_count = len(database.get_all_chats())
        print(f"📊 Active chat records: {chat_count}")
    except Exception as e:
        print(f"❌ Could not read chat database: {e}")

    await shutdown_async_event.wait()

# ========== Main ==========
async def main():
    global flask_thread, shutdown_async_event
    shutdown_event.clear()

    print("🔧 [1] Starting Flask thread...")
    flask_thread = FlaskServerThread(flask_app)
    flask_thread.start()
    print("🔧 [2] Flask thread started ✅")

    shutdown_async_event = asyncio.Event()
    print("🔧 [3] Entering run_bot()...")

    try:
        await run_bot(shutdown_event)
        await shutdown(shutdown_event)

    except (asyncio.CancelledError, KeyboardInterrupt):
        print("🛑 [!] Shutdown triggered")
        await shutdown(shutdown_event)

# ========== Signal Handling ==========
def handle_signal(signum, frame):
    logging.info(f"🛑 Received signal {signum}, initiating shutdown...")
    shutdown_event.set()
    try:
        loop = asyncio.get_running_loop()
        loop.call_soon_threadsafe(shutdown_async_event.set)
    except RuntimeError:
        logging.warning("⚠️ No running loop, skipping async shutdown")

if __name__ == '__main__':
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 KeyboardInterrupt received")