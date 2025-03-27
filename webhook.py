# webhook.py
import logging
import json
import asyncio
from flask import Blueprint, request, jsonify, render_template
from telegram.constants import ParseMode
from telegram import Update
from config import WEBHOOK_SECRET
import database
from models import News
from bot import broadcast_news

logger = logging.getLogger(__name__)
webhook_bp = Blueprint('webhook', __name__)

# This gets set in main.py:
application = None

def set_bot_application(app):
    """Called from main.py to make the PTB Application available here."""
    global application
    application = app

@webhook_bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@webhook_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "service": "telegram-news-bot"})

@webhook_bp.route('/news-webhook', methods=['POST'])
def news_webhook():
    """
    Example webhook that receives JSON with 'news' data, then broadcasts it.
    """
    if request.content_type != 'application/json':
        return jsonify({"error": "Content-Type must be application/json"}), 415

    try:
        data = request.json

        # Verify secret
        if not data.get('secret') or data['secret'] != WEBHOOK_SECRET:
            logger.warning("Invalid webhook secret received")
            return jsonify({"error": "Unauthorized, bad secret"}), 403

        # Parse 'news' data
        if not data.get('news'):
            return jsonify({"error": "Missing 'news' field"}), 400

        news = News.from_json(data['news'])
        database.log_webhook(news.news_id, json.dumps(data['news']))

        crypto_tags = data['news'].get('tags', [])
        is_crypto_news = any(
            term in ' '.join(crypto_tags).lower()
            for term in ['crypto', 'bitcoin', 'ethereum', 'كريبتو', 'بيتكوين', 'إيثريوم']
        )
        if is_crypto_news:
            logger.info(f"Received cryptocurrency news: {news.title}")

        target_chat_id = data.get('target_chat_id')

        async def process_broadcast():
            """
            Async function that actually sends the news to Telegram.
            """
            try:
                if target_chat_id:
                    logger.info(f"Sending news to specific chat ID: {target_chat_id}")
                    message_text = news.format_telegram_message()
                    msg = await application.bot.send_message(
                        chat_id=target_chat_id,
                        text=message_text,
                        parse_mode=ParseMode.MARKDOWN,
                        disable_web_page_preview=bool(news.image_url)
                    )
                    database.log_message(news.news_id, target_chat_id, msg.message_id)
                    success_count, error_count = 1, 0
                else:
                    # broadcast_news is an async function in bot.py
                    success_count, error_count = await broadcast_news(news)

                logger.info(f"Broadcast finished. Success: {success_count}, Errors: {error_count}")

            except Exception as exc:
                logger.error(f"Error broadcasting news: {exc}", exc_info=True)

        # Schedule our async function on the application's event loop:
        application.create_task(process_broadcast())

        response_data = {
            "status": "success",
            "message": "News broadcast request accepted",
            "news_id": news.news_id,
            "target_mode": "single_chat" if target_chat_id else "broadcast"
        }
        if target_chat_id:
            response_data["target_chat_id"] = target_chat_id

        return jsonify(response_data)

    except Exception as e:
        logger.exception(f"Error processing /news-webhook: {e}")
        return jsonify({"error": "Unexpected error"}), 500

@webhook_bp.route('/telegram-webhook', methods=['POST'])
def telegram_webhook():
    """
    Receives Telegram updates via webhook, then feeds them to PTB.
    """
    if not application:
        return jsonify({"error": "Bot not initialized"}), 503

    try:
        update_json = request.get_json(force=True)
        update = Update.de_json(update_json, application.bot)

        async def handle_update():
            await application.process_update(update)

        # Just get the loop safely
        loop = asyncio.get_event_loop()

        if loop.is_running():
            loop.create_task(handle_update())
        else:
            # This should never happen if your main loop is running
            logging.warning("⚠️ No running loop, this should not happen. Falling back to run_until_complete.")
            loop.run_until_complete(handle_update())

        return jsonify({"status": "success"}), 200

    except Exception as e:
        logger.exception(f"Error processing Telegram webhook: {e}")
        return jsonify({"error": str(e)}), 500