import logging
import json
import asyncio
import threading
from flask import Blueprint, request, jsonify, current_app, render_template

from config import WEBHOOK_SECRET
import database
from models import News
from bot import broadcast_news

logger = logging.getLogger(__name__)

webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.route('/', methods=['GET'])
def index():
    """Landing page for the webhook service."""
    return render_template('index.html')

@webhook_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok", "service": "telegram-news-bot"})

@webhook_bp.route('/news-webhook', methods=['POST'])
def news_webhook():
    """
    Endpoint to receive news via webhook.
    
    Expected JSON format:
    {
        "secret": "your_webhook_secret",
        "news": {
            "id": "unique_id",
            "title": "News Title",
            "content": "News content...",
            "source": "Source Name",
            "url": "https://example.com/news",
            "image_url": "https://example.com/image.jpg",
            "tags": ["tag1", "tag2"]
        }
    }
    """
    # Verify content type
    if request.content_type != 'application/json':
        return jsonify({"error": "Content-Type must be application/json"}), 415
    
    try:
        data = request.json
        
        # Validate secret
        if not data.get('secret') or data.get('secret') != WEBHOOK_SECRET:
            logger.warning("Invalid webhook secret received")
            return jsonify({"error": "Invalid webhook secret"}), 403
        
        # Validate news data
        if not data.get('news'):
            return jsonify({"error": "No news data provided"}), 400
        
        # Create News object
        try:
            news = News.from_json(data['news'])
        except ValueError as e:
            logger.error(f"Invalid news format: {e}")
            return jsonify({"error": str(e)}), 400
        
        # Log webhook with extra details for crypto news
        crypto_tags = data['news'].get('tags', [])
        is_crypto_news = any(crypto_term in ' '.join(crypto_tags).lower() for crypto_term in ['crypto', 'bitcoin', 'ethereum', 'كريبتو', 'بيتكوين', 'إيثريوم'])
        
        if is_crypto_news:
            logger.info(f"Received cryptocurrency news: {news.title}")
        
        database.log_webhook(news.news_id, json.dumps(data['news']))
        
        # Start async handling in a separate thread
        def process_broadcast():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                success_count, error_count = loop.run_until_complete(broadcast_news(news))
                logger.info(f"Broadcast completed. Success: {success_count}, Errors: {error_count}")
            except Exception as e:
                logger.error(f"Error broadcasting news: {e}")
            finally:
                loop.close()
        
        thread = threading.Thread(target=process_broadcast)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "status": "success",
            "message": "News broadcast request accepted",
            "news_id": news.news_id
        })
        
    except Exception as e:
        logger.exception(f"Error processing webhook: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@webhook_bp.route('/telegram-webhook', methods=['POST'])
def telegram_webhook():
    """
    Endpoint to receive Telegram webhook events.
    This is set up to receive updates from Telegram when the bot is interacted with.
    """
    if request.content_type != 'application/json':
        return 'Content-Type must be application/json', 415
    
    try:
        # The update is forwarded to the bot application for processing
        update_json = request.get_json()
        logger.debug(f"Received Telegram update: {update_json}")
        
        # We acknowledge receipt of the update
        # The actual processing is handled by the bot's webhook updater
        return jsonify({"status": "ok"})
        
    except Exception as e:
        logger.exception(f"Error processing Telegram webhook: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500
