import asyncio
from flask import Flask, request, jsonify, render_template, redirect, url_for
from telegram import Update
from telegram.constants import ParseMode
from logging_config import logger
import shared
import database
from models import News
from bot import broadcast_news
import json
from telegram.ext import Application
from shared import (
    log_error,
    WEBHOOK_SECRET,
    get_telegram_app, 
    is_shutting_down,
    webhook_bp,
    safe_async_exec,
    validate_webhook,
)

# No need to create new Flask app - using the shared blueprint
_bot_app = None

def set_bot_application(app):
    global _bot_app
    _bot_app = app

def get_bot_application():
    return _bot_app

@webhook_bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        logger.info("Redirecting POST from '/' to '/telegram-webhook'")
        return redirect(url_for('webhook.telegram_webhook'), code=307)  # preserves method and body

    return jsonify({
        "status": "ok",
        "shutting_down": is_shutting_down()
    })
@webhook_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "ok", 
        "service": "telegram-news-bot",
        "shutdown_status": is_shutting_down()
    })

@webhook_bp.route('/shutdown', methods=['POST'])
def shutdown_server():
    """Trigger graceful shutdown for local development."""
    if request.remote_addr != '127.0.0.1':
        return jsonify({"error": "Forbidden"}), 403

    logger.warning("🚪 Shutdown requested via /shutdown route")
    from threading import Thread
    Thread(target=lambda: shared.shutdown_event.set()).start()
    return jsonify({"status": "shutting down"}), 200


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
async def telegram_webhook():
    """Handle Telegram bot updates — direct + full debug logging."""
    import time
    start = time.time()

    print("\n🔔 ----------------------------------------")
    print("📥 [telegram-webhook] Received POST request")

    if is_shutting_down():
        logger.warning("Rejecting request during shutdown")
        print("⛔ [telegram-webhook] Shutdown in progress — rejecting request")
        print("🔔 ----------------------------------------\n")
        return jsonify({"error": "Service unavailable"}), 503

    # Webhook validation
    valid, reason = validate_webhook()
    if not valid:
        logger.warning(f"Webhook validation failed: {reason}")
        print(f"🚫 [telegram-webhook] Webhook validation failed: {reason}")
        print("🔔 ----------------------------------------\n")
        return jsonify({"error": reason}), 403

    try:
        app = get_telegram_app()
        print("✅ [telegram-webhook] Telegram application loaded")
    except RuntimeError:
        logger.warning("Telegram Application not yet initialized.")
        print("⚠️ [telegram-webhook] Telegram Application not yet initialized")
        print("🔔 ----------------------------------------\n")
        return jsonify({"error": "Bot not ready"}), 503

    try:
        update_data = request.get_json(force=True)
        update = Update.de_json(update_data, app.bot)
        logger.info("📥 Received Telegram update: %s", update_data)

        user = update.effective_user
        username = f"@{user.username}" if user and user.username else "NoUsername"
        user_id = user.id if user else "Unknown"
        full_name = user.full_name if user else "Unknown"

        print(f"📝 [telegram-webhook] Update parsed: ID={update.update_id}")
        print(f"🙋‍♂️ From user: {full_name} ({username}, ID: {user_id})")
        print(f"💬 Message: {update.message.text if update.message else '<non-text update>'}")

        print("⚙️ [telegram-webhook] Calling process_update...")
        asyncio.create_task(app.process_update(update))
        print(f"📊 [telegram-webhook] Update data: {json.dumps(update_data, indent=2)}")
        print(f"✅ [telegram-webhook] Update processed in {time.time() - start:.2f}s")
        print("🔔 ----------------------------------------\n")

        return "OK", 200

    except Exception as e:
        log_error(e, "telegram-webhook")
        print(f"❌ [telegram-webhook] Exception occurred: {e}")
        print("🔔 ----------------------------------------\n")
        return jsonify({"error": "Update failed"}), 500