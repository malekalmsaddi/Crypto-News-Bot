import os
from typing import Optional, Dict, Any, List, Tuple

from flask import Flask, request, jsonify, render_template
from telegram import Bot, Update
from telegram.ext import Application, ApplicationBuilder
from telegram.constants import ParseMode
from pycoingecko import CoinGeckoAPI

from loggin_config import logger
from shared_functions import log_error

# Environment variables (fail-fast validation)
TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
WEBHOOK_SECRET = os.environ['WEBHOOK_SECRET']
WEBHOOK_URL = os.getenv('WEBHOOK_URL', 'https://default.fly.dev/telegram-webhook')
SESSION_SECRET = os.getenv("SESSION_SECRET", "fallback-secret")

# Logging configuration with sensitive data filtering
class SensitiveFilter(logging.Filter):
    def filter(self, record):
        msg = record.getMessage()
        if "api.telegram.org/bot" in msg:
            record.msg = msg.replace(TELEGRAM_BOT_TOKEN, '[REDACTED]')
        return True

# Type aliases
PriceData = Dict[str, Dict[str, float]]
ChatData = Dict[str, Any]