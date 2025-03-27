from threading import Lock
import asyncio
from typing import Optional, Dict, Any, List, Tuple
from shared_imports import Flask, Application, logger, SESSION_SECRET

# ---- Shared Instances ----
flask_app = Flask(__name__)
flask_app.secret_key = SESSION_SECRET

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