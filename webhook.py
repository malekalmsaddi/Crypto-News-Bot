import asyncio
import json
from datetime import datetime
from flask import Blueprint, request, jsonify, redirect, url_for
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application
from functools import wraps

from logging_config import logger
import shared
import database
from models import News
from bot import broadcast_news
from shared import (
    log_error,
    WEBHOOK_SECRET, 
    get_telegram_app,
    is_shutting_down,
    validate_webhook,
    safe_async_exec
)

webhook_bp = Blueprint("webhook", __name__)

def async_route(f):
    """Decorator to handle async routes properly"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        try:
            return loop.run_until_complete(f(*args, **kwargs))
        except RuntimeError as e:
            if "Event loop is closed" in str(e):
                logger.error("Event loop closed during request")
                return jsonify({"error": "Service unavailable"}), 503
            raise
    return wrapper

@webhook_bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        logger.info("Redirecting POST from '/' to '/telegram-webhook'")
        return redirect(url_for('webhook.telegram_webhook'), code=307)

    return jsonify({
        "status": "ok",
        "shutting_down": is_shutting_down()
    })

@webhook_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "ok",
        "service": "telegram-news-bot",
        "shutdown_status": is_shutting_down(),
        "event_loop": "running" if not shared.is_shutting_down() else "closing"
    })

@webhook_bp.route('/shutdown', methods=['POST'])
def shutdown_server():
    if request.remote_addr != '127.0.0.1':
        return jsonify({"error": "Forbidden"}), 403

    logger.warning("🚪 Shutdown requested via /shutdown route")
    from threading import Thread
    Thread(target=lambda: shared.shutdown_event.set()).start()
    return jsonify({"status": "shutting down"}), 200

@webhook_bp.route('/news-webhook', methods=['POST'])
def news_webhook():
    if is_shutting_down():
        return jsonify({"error": "Service is shutting down"}), 503

    if request.content_type != 'application/json':
        return jsonify({"error": "Content-Type must be application/json"}), 415

    try:
        data = request.json

        if not data.get('secret') or data['secret'] != WEBHOOK_SECRET:
            logger.warning("Invalid webhook secret")
            return jsonify({"error": "Unauthorized"}), 403

        if not data.get('news'):
            return jsonify({"error": "Missing news data"}), 400

        news = News.from_json(data['news'])
        database.log_webhook(news.news_id, json.dumps(data['news']))

        crypto_terms = {'crypto', 'bitcoin', 'ethereum', 'كريبتو', 'بيتكوين', 'إيثريوم'}
        tags = data['news'].get('tags', [])
        if any(term in ' '.join(tags).lower() for term in crypto_terms):
            logger.info(f"Crypto news received: {news.title}")

        target_chat_id = data.get('target_chat_id')

        async def process_broadcast():
            try:
                app = get_telegram_app()
                if not app or not app.running:
                    raise RuntimeError("Telegram application not running")
                
                if target_chat_id:
                    msg = await app.bot.send_message(
                        chat_id=target_chat_id,
                        text=news.format_telegram_message(),
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=bool(news.image_url)
                    )
                    database.log_message(news.news_id, target_chat_id, msg.message_id)
                    return 1, 0
                return await broadcast_news(news)
            except Exception as e:
                log_error(e, "news broadcast")
                return 0, 1

        # Use safe_async_exec instead of direct asyncio.run
        success, _ = safe_async_exec(process_broadcast())
        if not success:
            return jsonify({"error": "Failed to process broadcast"}), 500

        return jsonify({
            "status": "success",
            "news_id": news.news_id,
            "target": target_chat_id or "broadcast"
        })

    except Exception as e:
        log_error(e, "news-webhook")
        return jsonify({"error": "Processing failed"}), 500

@webhook_bp.route('/telegram-webhook', methods=['POST'])
@async_route
async def telegram_webhook():
    request_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}-{hash(datetime.now().timestamp())}"
    logger.info(f"🔔 [{request_id}] Incoming Telegram webhook")

    if is_shutting_down():
        return jsonify({
            "status": "error",
            "code": 503,
            "message": "Service unavailable",
            "request_id": request_id
        }), 503

    is_valid, validation_reason = validate_webhook()
    if not is_valid:
        return jsonify({
            "status": "error",
            "code": 403,
            "message": validation_reason,
            "request_id": request_id
        }), 403

    try:
        update_data = request.get_json(force=True)
        app = get_telegram_app()
        
        if not app or not app.running:
            raise RuntimeError("Telegram application not running")

        update = Update.de_json(update_data, app.bot)

        user = update.effective_user or update.effective_chat
        user_info = {
            "id": getattr(user, 'id', 'N/A'),
            "username": f"@{user.username}" if getattr(user, 'username', None) else "N/A",
            "name": getattr(user, 'full_name', 'Unknown User'),
            "language": getattr(user, 'language_code', 'und')
        }

        logger.info(f"👤 [{request_id}] From: {user_info['name']} ({user_info['username']})")

        await app.process_update(update)

        return jsonify({
            "status": "success",
            "request_id": request_id,
            "user": user_info['id'],
            "timestamp": datetime.now().isoformat()
        })

    except RuntimeError as e:
        if "Event loop is closed" in str(e):
            logger.error(f"Event loop closed during webhook processing: {request_id}")
            return jsonify({
                "status": "error",
                "code": 503,
                "message": "Service unavailable",
                "request_id": request_id
            }), 503
        raise
    except Exception as e:
        error_id = f"ERR-{hash(datetime.now().timestamp())}"
        log_error(e, f"[{request_id}] update-processing")
        return jsonify({
            "status": "error",
            "code": 500,
            "error_id": error_id,
            "message": "Internal server error",
            "request_id": request_id
        }), 500