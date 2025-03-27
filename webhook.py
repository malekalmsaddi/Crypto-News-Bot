import asyncio
from flask import Flask, request, jsonify, render_template
from telegram import Update
from telegram.constants import ParseMode

from logging_config import logger
from shared_functions import log_error
from shared_imports import WEBHOOK_SECRET

from shared_apps import (
    get_telegram_app, 
    is_shutting_down,
    webhook_bp  # This is the Blueprint object
)
from shared_functions import (
    safe_async_exec,
    validate_webhook,
)
import database
from models import News
from bot import broadcast_news
import json

# No need to create new Flask app - using the shared blueprint
_bot_app = None

def set_bot_application(app):
    global _bot_app
    _bot_app = app

def get_bot_application():
    return _bot_app

@webhook_bp.route('/', methods=['GET'])
def index():
    """Simple health check endpoint."""
    return render_template('index.html')

@webhook_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "ok", 
        "service": "telegram-news-bot",
        "shutdown_status": is_shutting_down()
    })

@webhook_bp.route('/news-webhook', methods=['POST'])
def news_webhook():
    """
    Process incoming news and broadcast to Telegram chats.
    """
    # Request validation
    if request.content_type != 'application/json':
        return jsonify({"error": "Content-Type must be application/json"}), 415

    try:
        data = request.json
        
        # Secret validation
        if not data.get('secret') or data['secret'] != WEBHOOK_SECRET:
            logger.warning("Invalid webhook secret")
            return jsonify({"error": "Unauthorized"}), 403

        # News data validation
        if not data.get('news'):
            return jsonify({"error": "Missing news data"}), 400

        # Process news
        news = News.from_json(data['news'])
        database.log_webhook(news.news_id, json.dumps(data['news']))

        # Check if crypto-related news
        crypto_terms = {'crypto', 'bitcoin', 'ethereum', 'كريبتو', 'بيتكوين', 'إيثريوم'}
        tags = data['news'].get('tags', [])
        if any(term in ' '.join(tags).lower() for term in crypto_terms):
            logger.info(f"Crypto news received: {news.title}")

        # Prepare broadcast
        target_chat_id = data.get('target_chat_id')

        async def process_broadcast():
            """Async broadcast handler."""
            try:
                app = get_telegram_app()
                if target_chat_id:
                    msg = await app.bot.send_message(
                        chat_id=target_chat_id,
                        text=news.format_telegram_message(),
                        parse_mode=ParseMode.MARKDOWN,
                        disable_web_page_preview=bool(news.image_url)
                    )
                    database.log_message(news.news_id, target_chat_id, msg.message_id)
                    return 1, 0  # success_count, error_count
                return await broadcast_news(news)
            except Exception as e:
                log_error(e, "news broadcast")
                return 0, 1

        # Execute safely
        asyncio.create_task(safe_async_exec(process_broadcast()))

        return jsonify({
            "status": "success",
            "news_id": news.news_id,
            "target": target_chat_id or "broadcast"
        })

    except Exception as e:
        log_error(e, "news-webhook")
        return jsonify({"error": "Processing failed"}), 500

@webhook_bp.route('/telegram-webhook', methods=['POST'])
def telegram_webhook():
    """Handle Telegram bot updates."""
    # Shutdown check
    if is_shutting_down():
        logger.warning("Rejecting request during shutdown")
        return jsonify({"error": "Service unavailable"}), 503

    # Webhook validation
    valid, reason = validate_webhook()
    if not valid:
        logger.warning(f"Webhook validation failed: {reason}")
        return jsonify({"error": reason}), 403

    try:
        app = get_telegram_app()
    except RuntimeError:
        logger.warning("Telegram Application not yet initialized.")
        return jsonify({"error": "Bot not ready"}), 503

    try:
        update = Update.de_json(request.get_json(force=True), app.bot)
        logger.info("Received Telegram update: %s", request.get_data(as_text=True))

        async def run_update():
            await safe_async_exec(app.process_update(update))

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        loop = asyncio.get_event_loop()
        loop.create_task(run_update())


        return "OK", 200

    except Exception as e:
        log_error(e, "telegram-webhook")
        return "Error", 500
