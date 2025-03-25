import logging
import json
import asyncio
import threading
from flask import Blueprint, request, jsonify, render_template
from telegram.constants import ParseMode
from telegram import Update
<<<<<<< HEAD
=======

>>>>>>> upstream/main
from config import WEBHOOK_SECRET
import database
from models import News
from bot import broadcast_news, application

logger = logging.getLogger(__name__)
webhook_bp = Blueprint('webhook', __name__)

# ✅ Bot Application placeholder - will be set from main.py
application = None

def set_bot_application(app):
    global application
    application = app

@webhook_bp.route('/', methods=['GET'])
async def index():
    return render_template('index.html')

@webhook_bp.route('/health', methods=['GET'])
async def health_check():
    return jsonify({"status": "ok", "service": "telegram-news-bot"})

@webhook_bp.route('/news-webhook', methods=['POST'])
<<<<<<< HEAD
async def news_webhook():
=======
def news_webhook():
>>>>>>> upstream/main
    if request.content_type != 'application/json':
        return jsonify({"error": "Content-Type must be application/json"}), 415

    try:
<<<<<<< HEAD
        data = request.json
        if not data.get('secret') or data.get('secret') != WEBHOOK_SECRET:
            logger.warning("Invalid webhook secret received")
            return jsonify({"error": "Invalid webhook secret"}), 403

        if not data.get('news'):
            return jsonify({"error": "No news data provided"}), 400

        news = News.from_json(data['news'])
        crypto_tags = data['news'].get('tags', [])
        is_crypto_news = any(term in ' '.join(crypto_tags).lower() for term in ['crypto', 'bitcoin', 'ethereum', 'كريبتو', 'بيتكوين', 'إيثريوم'])
        if is_crypto_news:
            logger.info(f"Received cryptocurrency news: {news.title}")

        database.log_webhook(news.news_id, json.dumps(data['news']))
        target_chat_id = data.get('target_chat_id')

        async def process_broadcast():
=======
        data = request.get_json()

        # Validate secret
        if data.get('secret') != WEBHOOK_SECRET:
            logger.warning("Invalid webhook secret received")
            return jsonify({"error": "Invalid webhook secret"}), 403

        # Validate and parse news data
        if not data.get('news'):
            return jsonify({"error": "No news data provided"}), 400

        try:
            news = News.from_json(data['news'])
        except ValueError as e:
            logger.error(f"Invalid news format: {e}")
            return jsonify({"error": str(e)}), 400

        # Log crypto-specific news
        crypto_tags = data['news'].get('tags', [])
        if any(term in ' '.join(crypto_tags).lower() for term in ['crypto', 'bitcoin', 'ethereum', 'كريبتو', 'بيتكوين', 'إيثريوم']):
            logger.info(f"Received cryptocurrency news: {news.title}")

        database.log_webhook(news.news_id, json.dumps(data['news']))

        target_chat_id = data.get('target_chat_id')

        def process_broadcast():
>>>>>>> upstream/main
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                if target_chat_id:
<<<<<<< HEAD
                    logger.info(f"Sending news to specific chat ID: {target_chat_id}")
                    message_text = news.format_telegram_message()
                    message = await application.bot.send_message(
                        chat_id=target_chat_id,
                        text=message_text,
                        parse_mode=ParseMode.MARKDOWN,
                        disable_web_page_preview=not bool(news.image_url)
                    )
                    database.log_message(news.news_id, target_chat_id, message.message_id)
                    success_count, error_count = 1, 0
                else:
                    success_count, error_count = await broadcast_news(news)

                logger.info(f"Broadcast completed. Success: {success_count}, Errors: {error_count}")
            except Exception as e:
                logger.error(f"Error broadcasting news: {e}")

        threading.Thread(target=lambda: asyncio.run(process_broadcast()), daemon=True).start()

        response_data = {
            "status": "success",
            "message": "News broadcast request accepted",
            "news_id": news.news_id,
            "target_mode": "single_chat" if target_chat_id else "broadcast"
        }
        if target_chat_id:
            response_data["target_chat_id"] = target_chat_id

        return jsonify(response_data)
=======
                    logger.info(f"Sending news to chat ID: {target_chat_id}")
                    message_text = news.format_telegram_message()
                    message = loop.run_until_complete(
                        application.bot.send_message(
                            chat_id=target_chat_id,
                            text=message_text,
                            parse_mode=ParseMode.MARKDOWN,
                            disable_web_page_preview=bool(news.image_url)
                        )
                    )
                    database.log_message(news.news_id, target_chat_id, message.message_id)
                    logger.info(f"Message sent to chat {target_chat_id}")
                else:
                    success_count, error_count = loop.run_until_complete(broadcast_news(news))
                    logger.info(f"Broadcast completed. Success: {success_count}, Errors: {error_count}")

            except Exception as e:
                logger.exception(f"Error broadcasting news: {e}")
            finally:
                loop.close()

        threading.Thread(target=process_broadcast, daemon=True).start()

        response = {
            "status": "success",
            "message": "News broadcast request accepted",
            "news_id": news.news_id,
            "target_mode": "single_chat" if target_chat_id else "broadcast",
            "target_chat_id": target_chat_id if target_chat_id else None
        }
        return jsonify(response)
>>>>>>> upstream/main

    except Exception as e:
        logger.exception(f"Error processing webhook: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@webhook_bp.route('/telegram-webhook', methods=['POST'])
async def telegram_webhook():
<<<<<<< HEAD
    global application
    if not application:
        logger.error("Bot application is not initialized")
        return jsonify({"error": "Bot not initialized"}), 503
=======
    if request.content_type != 'application/json':
        return 'Content-Type must be application/json', 415
>>>>>>> upstream/main

    try:
        update_json = request.get_json()
        logger.debug(f"Received Telegram update: {update_json}")

<<<<<<< HEAD
        # ✅ Convert JSON to Update object (MUST)
        update = Update.de_json(update_json, application.bot)

        # ✅ Process the update fully
        await application.process_update(update)

        return jsonify({"status": "success"}), 200
=======
        update = Update.de_json(update_json, application.bot)

        # Ensure application is initialized if needed
        if not application.running:
            await application.initialize()

        # Schedule processing asynchronously
        asyncio.create_task(application.process_update(update))

        return jsonify({"status": "ok"})
>>>>>>> upstream/main
    except Exception as e:
        logger.exception(f"Error processing Telegram webhook: {e}")
        return jsonify({"error": str(e)}), 500
