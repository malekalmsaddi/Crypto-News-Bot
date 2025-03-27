# shared_apps.py
from threading import Lock
import asyncio
from typing import Optional, Dict, Any

from flask import Flask, Blueprint
from telegram.ext import Application
from logging_config import logger

from shared_imports import SESSION_SECRET

# ---- Shared Instances ----
flask_app = Flask(__name__)
flask_app.secret_key = SESSION_SECRET

# Define an actual Blueprint for webhook routes
webhook_bp = Blueprint("webhook", __name__)

_telegram_app = None
_telegram_app_lock = Lock()
_shutting_down = False
_shutdown_lock = asyncio.Lock()

# ---- Telegram App Management ----
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
async def set_shutting_down(state: bool) -> None:
    global _shutting_down
    async with _shutdown_lock:
        _shutting_down = state

def is_shutting_down() -> bool:
    return _shutting_down
__all__ = ["flask_app", "webhook_bp", "set_telegram_app", "get_telegram_app", "set_shutting_down", "is_shutting_down"]