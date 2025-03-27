# logging_config.py
import os
import logging

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '[REDACTED]')

class SensitiveFilter(logging.Filter):
    def filter(self, record):
        msg = record.getMessage()
        if "api.telegram.org/bot" in msg and TELEGRAM_BOT_TOKEN:
            record.msg = msg.replace(TELEGRAM_BOT_TOKEN, '[REDACTED]')
        return True

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger("CryptoNewsBot")
logger.addFilter(SensitiveFilter())