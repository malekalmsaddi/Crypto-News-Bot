import os
import logging
import asyncio
import threading
import signal
from flask import jsonify, render_template
from werkzeug.serving import make_server
from webhook import webhook_bp
from config import HOST, PORT, DEBUG, TELEGRAM_BOT_TOKEN, WEBHOOK_URL, WEBHOOK_SECRET
import database
import shared
from market import start_market_fetcher, stop_market_fetcher
from telegram.ext import ApplicationBuilder
from bot import get_bot_username, setup_handlers, send_hourly_price_update, setup_bot
from threading import Event as ThreadingEvent
from shared import (
    set_telegram_app,
    is_shutting_down,
    set_shutting_down,
    sync_shutdown_lock,
    shutdown_lock,
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
    """Graceful shutdown procedure with proper resource cleanup"""
    print('🛠️ [shutdown] Starting graceful shutdown sequence...')
    
    async with shutdown_lock:
        if is_shutting_down():
            print('🚫 [shutdown] Already shutting down - skipping')
            return

        set_shutting_down(True)
        print('🔒 [shutdown] Shutdown flag set')
        
        try:
            # 1. Notify async components
            if shutdown_async_event:
                shutdown_async_event.set()
                print('✅ [shutdown] Async components notified')

            # 2. Stop Flask server (sync operation)
            if flask_thread and flask_thread.is_alive():
                print('🛑 [shutdown] Stopping Flask server...')
                flask_thread.shutdown()
                flask_thread.join(timeout=5)
                print('✅ [shutdown] Flask server stopped')

            # 3. Shutdown Telegram application
            if application:
                print('🤖 [shutdown] Stopping Telegram application...')
                try:
                    # Stop receiving updates first
                    await application.stop()
                    # Then shutdown completely
                    await application.shutdown()
                    print('💤 [shutdown] Telegram application stopped')
                    
                    # Explicitly close the HTTP client
                    if hasattr(application.bot, '_client'):
                        await application.bot._client.aclose()
                except Exception as e:
                    logging.error(f"Telegram shutdown error: {str(e)}")

            # 4. Stop market fetcher
            print('📊 [shutdown] Stopping market fetcher...')
            stop_market_fetcher()
            print('✅ [shutdown] Market fetcher stopped')

            # 5. Cancel pending tasks with timeout
            print('🧹 [shutdown] Cleaning up background tasks...')
            current_task = asyncio.current_task()
            tasks = [t for t in asyncio.all_tasks() if t is not current_task]
            
            for task in tasks:
                task.cancel()
            
            try:
                await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), timeout=5.0)
                print('✅ [shutdown] Background tasks cleared')
            except asyncio.TimeoutError:
                logging.warning("⚠️ Some tasks didn't complete during shutdown timeout")

        except Exception as e:
            logging.critical(f"🆘 Critical shutdown error: {str(e)}", exc_info=True)
        finally:
            logging.info("🛑 Shutdown sequence completed")
            print('✅ [shutdown] Shutdown completed successfully')

# ========== Bot Logic ==========
async def run_bot(shutdown_event):
    global application
    print("🤖 [run_bot] Initializing...")
    logging.info("⚡ Initializing bot components...")

    try:
        # Initialize application with job queue support
        application = ApplicationBuilder() \
            .token(TELEGRAM_BOT_TOKEN) \
            .build()
            
        set_telegram_app(application)
        setup_handlers(application)

        # Only schedule jobs if job_queue is available
        if application.job_queue:
            application.job_queue.run_repeating(
                send_hourly_price_update, 
                interval=3600,  # 1 hour
                first=60        # 1 minute delay
            )
            logging.info("✅ Hourly price update job scheduled")
        else:
            logging.warning("⚠️ JobQueue not available")

        await application.initialize()
        await application.start()

        # Webhook setup
        try:
            await application.bot.delete_webhook(drop_pending_updates=True)
            await application.bot.set_webhook(
                url=WEBHOOK_URL,
                secret_token=WEBHOOK_SECRET
            )
            logging.info(f"✅ Webhook registered at: {WEBHOOK_URL}")
        except Exception as e:
            logging.error(f"❌ Webhook setup failed: {e}")
            raise

        # Diagnostic info
        bot_username = await get_bot_username()
        logging.info(f"🤖 Bot username: @{bot_username}")

        set_shutting_down(False)
        logging.info("🟢 Bot operational - waiting for shutdown...")
        await shutdown_event.wait()

    except Exception as e:
        logging.error(f"❌ Bot initialization failed: {e}")
        raise
# ========== Main ==========
async def main():
    print("🔧 main() is being called!")
    
    global flask_thread, shutdown_async_event
    shutdown_event.clear()

    try:
        # Start Flask thread
        flask_thread = FlaskServerThread(flask_app)
        flask_thread.start()
        
        # Initialize bot
        shutdown_async_event = asyncio.Event()
        await run_bot(shutdown_event)
        
    except (asyncio.CancelledError, KeyboardInterrupt):
        print("🛑 Shutdown triggered")
        await shutdown(shutdown_event)
    except Exception as e:
        logging.critical(f"Unexpected error: {e}")
        await shutdown(shutdown_event)
        raise

# ========== Signal Handling ==========
def handle_signal(signum, frame):
    """Enhanced signal handler that works with existing shutdown flow"""
    if is_shutting_down():
        logging.warning("🚨 Forceful termination (already shutting down)")
        os._exit(1)  # Only used as last resort
    
    logging.info(f"🛑 Received signal {signum}, initiating graceful shutdown...")
    shutdown_event.set()
    
    try:
        loop = asyncio.get_running_loop()
        if loop.is_running():
            # Schedule shutdown without disrupting existing event loop
            asyncio.create_task(shutdown(shutdown_event))
    except RuntimeError:
        logging.warning("⚠️ Signal handler: No running event loop")


if __name__ == '__main__':
    print("🔧 Script is being executed directly!")  # Debug print
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 KeyboardInterrupt received")