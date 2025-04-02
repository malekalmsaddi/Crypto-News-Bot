# shared.py

import os
import asyncio
import logging
from threading import Lock, Event
from typing import Optional, Dict, Any, Tuple
from flask import Flask, request, jsonify
from telegram.ext import Application

# ---- Logging Config ----
logger = logging.getLogger(__name__)

# ---- Shutdown Flag ----
_shutdown_lock = Lock()
_shutdown_async_lock = asyncio.Lock()
_shutting_down = False

# ---- Environment Variables ----
TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
WEBHOOK_SECRET = os.environ['WEBHOOK_SECRET']
WEBHOOK_URL = os.getenv('WEBHOOK_URL', 'https://default.fly.dev/telegram-webhook')
SESSION_SECRET = os.getenv("SESSION_SECRET", "fallback-secret")

# ---- Type Aliases ----
PriceData = Dict[str, Dict[str, float]]
ChatData = Dict[str, Any]

# ---- Shared Flask App ----
flask_app = Flask(__name__, template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), './templates')))
flask_app.secret_key = SESSION_SECRET

# ---- Telegram App Management ----
_telegram_app: Optional[Application] = None
_telegram_app_lock = Lock()

def set_telegram_app(app: Application) -> None:
    global _telegram_app
    with _telegram_app_lock:
        _telegram_app = app
        logger.info("Telegram app initialized")

def get_telegram_app() -> Application:
    with _telegram_app_lock:
        if _telegram_app is None:
            raise RuntimeError("Telegram app not initialized")
        return _telegram_app

# ---- Shutdown Control ----
def is_shutting_down() -> bool:
    with _shutdown_lock:
        print(f"🔍 is_shutting_down() called, _shutting_down: {_shutting_down}")
        return _shutting_down

def set_shutting_down(state: bool) -> None:
    global _shutting_down
    with _shutdown_lock:
        print(f"🔄 Setting shutdown state to: {state}")  # Debug print
        _shutting_down = state

sync_shutdown_lock = _shutdown_lock  # For synchronous code
shutdown_lock = _shutdown_async_lock  # For async code (primary interface)

# ---- Async Utility ----
async def safe_async_exec(coroutine) -> None:
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return await coroutine
        else:
            return asyncio.run(coroutine)
    except RuntimeError as e:
        logger.error(f"Async exec failed: {e}")
        try:
            return asyncio.run(coroutine)
        except Exception as ex:
            logger.error(f"Fallback async run failed: {ex}")

# ---- Error Logging ----
def log_error(error: Exception, context: str = ""):
    logger.error(f"\ud83d\udea8 {context} - {type(error).__name__}: {error}")

# ---- Webhook Validator ----
def validate_webhook() -> Tuple[bool, str]:
    if is_shutting_down():
        return False, "Service shutting down"
    if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != WEBHOOK_SECRET:
        return False, "Invalid secret"
    return True, ""
# ---- Reject Requests During Shutdown ----
@flask_app.before_request
def reject_if_shutting_down():
    shutting_down = is_shutting_down()
    print(f"🔍 reject_if_shutting_down() called, is_shutting_down: {shutting_down}")
    if shutting_down:
        return jsonify({"error": "Service is shutting down"}), 503
    
async def check_shutdown() -> bool:
    """Async-safe shutdown check"""
    async with shutdown_lock:
        return _shutting_down

def sync_check_shutdown() -> bool:
    """Sync shutdown check"""
    with sync_shutdown_lock:
        return _shutting_down
    
async def async_is_shutting_down() -> bool:
    """Thread-safe async shutdown check"""
    async with shutdown_lock:
        return _shutting_down