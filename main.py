import os
import logging
import asyncio
import threading
import signal

from flask import Flask, jsonify
from werkzeug.serving import make_server

from config import HOST, PORT, DEBUG, TELEGRAM_BOT_TOKEN, WEBHOOK_URL, WEBHOOK_SECRET
import database
import webhook
from market import start_market_fetcher, stop_market_fetcher
from telegram.ext import ApplicationBuilder
from bot import get_bot_username, setup_handlers, send_hourly_price_update
from threading import Event as ThreadingEvent
from shared import shutdown_lock, webhook_bp, set_telegram_app, is_shutting_down, shutting_down_flag

# Link shutdown event globally
shutdown_event = ThreadingEvent()
import shared
shared.shutdown_event = shutdown_event
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
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "SomeRandomSecret")
app.register_blueprint(webhook_bp)
database.init_db()

@app.before_request
def reject_if_shutting_down():
    if is_shutting_down():  # 🛠️ Fix this line
        return jsonify({"error": "Service is shutting down"}), 503

class FlaskServerThread(threading.Thread):
    def __init__(self, app):
        super().__init__()
        self.server = make_server(HOST, PORT, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        logging.info("✅ Flask server starting...")
        self.server.serve_forever()

    def shutdown(self):
        logging.info("🛑 Flask server shutting down...")
        self.server.shutdown()
        self.server.server_close()

# ========== Shutdown Logic ==========
async def shutdown(shutdown_event):
    global shutting_down
    print('🛠️ [shutdown] Acquiring shutdown lock...')
    async with shutdown_lock:
        if is_shutting_down():
            print('🚫 [shutdown] Already shutting down. Aborting.')
            return
        shutting_down_flag.set()
        print('🔒 [shutdown] Shutdown flag set.')

        logging.info("🛑 Initiating clean shutdown...")

        print('🔔 [shutdown] Setting async shutdown event...')
        shutdown_async_event.set()
        print('✅ [shutdown] shutdown_async_event.set() complete')

        if flask_thread:
            print('📡 [shutdown] Flask thread detected. Calling shutdown...')
            flask_thread.shutdown()
            print('🕒 [shutdown] Waiting for Flask thread to terminate...')
            flask_thread.join(timeout=5)
            print('✅ [shutdown] Flask thread shutdown sequence complete')

        if application:
            try:
                print('🤖 [shutdown] Stopping Telegram application...')
                await application.stop()
                print('💤 [shutdown] Telegram application stopped.')
                await application.shutdown()
                print('💤 [shutdown] Telegram application shutdown complete.')
            except Exception as e:
                print(f'⚠️ [shutdown] Exception during Telegram shutdown: {e}')
                logging.warning(f"⚠️ Telegram shutdown issue: {e}")

        print('📉 [shutdown] Stopping market fetcher...')
        stop_market_fetcher()
        print('✅ [shutdown] Market fetcher stopped.')

        print('🚫 [shutdown] Cancelling remaining asyncio tasks...')
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        print('✅ [shutdown] All tasks cancelled and awaited.')

# ========== Bot Logic ==========
async def run_bot(shutdown_event):
    global application
    print("🤖 [run_bot] Initializing...")

    logging.info("⚡ Initializing bot components...")

    print("📞 Calling start_market_fetcher()")
    start_market_fetcher()
    print("✅ Returned from start_market_fetcher()")

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    set_telegram_app(application)
    setup_handlers(application)

    application.job_queue.run_repeating(send_hourly_price_update, interval=20000, first=3600)

    await application.initialize()
    await application.start()
    await asyncio.sleep(2)

    # === Remove old webhook first to avoid stuck state ===
    try:
        await application.bot.delete_webhook(drop_pending_updates=True)
        logging.info("🧹 Old webhook deleted")
    except Exception as e:
        logging.warning(f"⚠️ Failed to delete old webhook: {e}")

    # === Determine environment and set correct webhook URL ===
    default_fly_url = "https://cryptonewsbot.fly.dev/telegram-webhook"
    local_env_exists = os.path.exists(".env")
    webhook_url = os.getenv("WEBHOOK_URL") if local_env_exists else default_fly_url

    if local_env_exists:
        logging.info(f"💻 Detected local .env — using webhook from environment: {webhook_url}")
    else:
        logging.info(f"☁️ No .env found — using default Fly.io webhook: {webhook_url}")

    # === Set the Telegram webhook ===
    try:
        await application.bot.set_webhook(
            url=webhook_url,
            secret_token=WEBHOOK_SECRET
        )
        logging.info(f"✅ Webhook successfully registered at: {webhook_url}")
    except Exception as e:
        logging.exception(f"❌ Failed to set Telegram webhook: {e}")

    bot_username = await get_bot_username()
    logging.info(f"✅ Bot username: @{bot_username}")
    from shared import set_shutting_down

    print("✅ Setting shutting_down = False")
    await set_shutting_down(False)
    print("✅ Bot is now accepting requests")

    # ✅ Additional Post-Startup Debug Prints
    print("🟢 [run_bot] Bot fully initialized — waiting for shutdown...")

    # ✅ 1. Job Queue Check
    print(f"🗓️ Job queue active: {len(application.job_queue.jobs())} jobs scheduled")

    # ✅ 2. Webhook Info Check
    try:
        webhook_info = await application.bot.get_webhook_info()
        print(f"🌐 Webhook Info: URL = {webhook_info.url}, Pending Updates = {webhook_info.pending_update_count}")
    except Exception as e:
        print(f"❌ Failed to fetch webhook info: {e}")

    # ✅ 3. Bot Identity Confirmation
    try:
        me = await application.bot.get_me()
        print(f"🤖 Bot Identity: @{me.username}, ID = {me.id}")
    except Exception as e:
        print(f"❌ Failed to fetch bot identity: {e}")

    # ✅ 4. Chat DB Count
    try:
        import database
        chat_count = len(database.get_all_chats())
        print(f"📊 Active chat records: {chat_count}")
    except Exception as e:
        print(f"❌ Could not read chat database: {e}")

    # ✅ 5. Final confirmation
    print("✅ [run_bot] All systems go. Bot is fully operational.")

    await shutdown_async_event.wait()
# ========== Main ==========
async def main():
    global flask_thread, shutdown_async_event
    shutdown_event.clear()

    print("🔧 [1] Starting Flask thread...")
    flask_thread = FlaskServerThread(app)
    flask_thread.start()
    print("🔧 [2] Flask thread started ✅")

    shutdown_async_event = asyncio.Event()
    print("🔧 [3] Entering run_bot()...")

    try:
        await run_bot(shutdown_event)
        print("🔧 [4] run_bot() completed")

        # 🛠️ Trigger actual shutdown when run_bot exits
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
