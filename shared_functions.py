import logging

from shared_apps import get_telegram_app, is_shutting_down
from shared_imports import WEBHOOK_SECRET
from shared_imports import (
    logger, asyncio, request,
    WEBHOOK_SECRET, Tuple, PriceData, 
    ChatData, ParseMode
)

# ---- Async Utilities ----
async def safe_async_exec(coroutine) -> None:
    """Handle async execution with loop safety."""
    try:
        loop = asyncio.get_running_loop()
        if loop.is_running():
            return loop.create_task(coroutine)
        return await coroutine
    except RuntimeError as e:
        logger.error(f"Async exec failed: {e}")
        await coroutine

def log_error(error: Exception):
    logging.error(f"🚨 {type(error).__name__}: {error}")


def validate_webhook() -> Tuple[bool, str]:
    """Validate webhook request."""
    if is_shutting_down():
        return False, "Service shutting down"
    if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != WEBHOOK_SECRET:
        return False, "Invalid secret"
    return True, ""

# ---- Formatting ----
def format_market_update(prices: PriceData) -> str:
    return "\n".join(
        f"{coin}: ${data['price']:,.2f} "
        f"({'🟢+' if data['change'] > 0 else '🔴'}{data['change']:.2f}%)"
        for coin, data in prices.items()
    )