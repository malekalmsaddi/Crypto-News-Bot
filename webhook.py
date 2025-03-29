import asyncio
import json
from datetime import datetime
from flask import Blueprint, request, jsonify, redirect, url_for
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application

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
    safe_async_exec,
    validate_webhook,
)

webhook_bp = Blueprint("webhook", __name__)

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
        "shutdown_status": is_shutting_down()
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

        asyncio.run(process_broadcast())

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
    try:
        return asyncio.run(_handle_telegram_webhook())
    except RuntimeError as e:
        logger.error(f"RuntimeError during webhook processing: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

async def _handle_telegram_webhook():
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