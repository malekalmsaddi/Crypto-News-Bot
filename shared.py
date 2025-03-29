# shared_all.py

import os
import asyncio
import logging
from threading import Lock, Event
from typing import Optional, Dict, Any, List, Tuple

from flask import Flask, Blueprint, request, jsonify, render_template
from telegram import Bot, Update
from telegram.ext import Application, ApplicationBuilder
from telegram.constants import ParseMode
from pycoingecko import CoinGeckoAPI
import threading
# ---- Shutdown Flag ----
shutting_down_flag = Event()
_shutdown_lock = asyncio.Lock()
shutdown_lock = _shutdown_lock  # clearly expose publicly
shutting_down_flag = threading.Event()

# ---- Logging Config ----
from logging_config import logger

# ---- Environment Variables ----
TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
WEBHOOK_SECRET = os.environ['WEBHOOK_SECRET']
WEBHOOK_URL = os.getenv('WEBHOOK_URL', 'https://default.fly.dev/telegram-webhook')
SESSION_SECRET = os.getenv("SESSION_SECRET", "fallback-secret")

# ---- Type Aliases ----
PriceData = Dict[str, Dict[str, float]]
ChatData = Dict[str, Any]

# ---- Sensitive Log Filter ----
class SensitiveFilter(logging.Filter):
    def filter(self, record):
        msg = record.getMessage()
        if "api.telegram.org/bot" in msg:
            record.msg = msg.replace(TELEGRAM_BOT_TOKEN, '[REDACTED]')
        return True

# ---- Shared Flask App ----
flask_app = Flask(__name__)
flask_app.secret_key = SESSION_SECRET
webhook_bp = Blueprint("webhook", __name__)

# ---- Telegram App Management ----
_telegram_app = None
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
    return shutting_down_flag.is_set()

async def set_shutting_down(state: bool) -> None:
    async with _shutdown_lock:
        if state:
            shutting_down_flag.set()
        else:
            shutting_down_flag.clear()

shutdown_lock = _shutdown_lock

# ---- Async Utility ----
async def safe_async_exec(coroutine) -> None:
    try:
        loop = asyncio.get_running_loop()
        if loop.is_running():
            return loop.create_task(coroutine)
        return await coroutine
    except RuntimeError as e:
        logger.error(f"Async exec failed: {e}")
        await coroutine

# ---- Error Logging ----
def log_error(error: Exception, context: str = ""):
    logging.error(f"🚨 {context} - {type(error).__name__}: {error}")

# ---- Webhook Validator ----
def validate_webhook() -> Tuple[bool, str]:
    if is_shutting_down():
        return False, "Service shutting down"
    if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != WEBHOOK_SECRET:
        return False, "Invalid secret"
    return True, ""

# ---- Market Formatter ----
def format_market_update(prices: PriceData) -> str:
    return "\n".join(
        f"{coin}: ${data['price']:,.2f} "
        f"({'🟢+' if data['change'] > 0 else '🔴'}{data['change']:.2f}%)"
        for coin, data in prices.items()
    )