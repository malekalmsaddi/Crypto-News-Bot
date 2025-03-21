#!/usr/bin/env python3
"""
Test sending a direct message to a specific user.

This script:
1. Cleans the database of test chats
2. Adds a test chat (yours) to the database
3. Creates and formats a cryptocurrency news item
4. Sends the news directly to your chat
"""

import asyncio
import sys
import os
import logging
import sqlite3
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import project modules
from bot import broadcast_news
from models import News
import database


def clean_test_chats():
    """Remove all test chats from the database"""
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chats")
    conn.commit()
    conn.close()
    logger.info("Cleaned all chats from database")


def add_user_chat(chat_id):
    """Add a user chat to the database"""
    if not chat_id:
        logger.error("No chat ID provided. Please specify your Telegram chat ID.")
        return False
    
    # Convert to integer to ensure it's a valid ID
    try:
        chat_id = int(chat_id)
    except ValueError:
        logger.error(f"Invalid chat ID format: {chat_id}. Must be an integer.")
        return False
    
    # Add chat to database
    database.add_chat(chat_id, f"User Chat {chat_id}", "private")
    logger.info(f"Added chat ID {chat_id} to database")
    return True


def create_test_news():
    """Create a test crypto news item"""
    return News(
        news_id=f"test-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        title="🚀 اختبار مباشر: إرسال أخبار الكريبتو",
        content="هذا اختبار مباشر لبوت أخبار الكريبتو. إذا كنت ترى هذه الرسالة، فهذا يعني أن البوت يعمل بشكل صحيح ويمكنه إرسال الأخبار مباشرة إلى محادثتك. نظام البيتكوين يمر بمرحلة تطور قوية هذه الأيام.",
        source="اختبار بوت أخبار الكريبتو",
        url="https://example.com/crypto-news-test",
        tags=["اختبار", "بيتكوين", "بوت_تلغرام"]
    )


async def send_direct_message(chat_id):
    """Send a test news message directly to a specific chat"""
    # Create test news
    news = create_test_news()
    
    # Broadcast the news (which will only go to the chat we just added)
    success, errors = await broadcast_news(news)
    
    if success > 0:
        logger.info(f"✅ Test message sent successfully to chat ID {chat_id}")
        return True
    else:
        logger.error(f"❌ Failed to send test message to chat ID {chat_id}")
        return False


async def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python test_direct_message.py YOUR_CHAT_ID")
        print("\nTo get your chat ID:")
        print("1. Start a conversation with @userinfobot on Telegram")
        print("2. It will reply with your user info including your chat ID")
        return
    
    chat_id = sys.argv[1]
    
    print(f"🔄 Testing direct message to chat ID: {chat_id}")
    print("-" * 50)
    
    # Clean database and add only the target chat
    clean_test_chats()
    
    if not add_user_chat(chat_id):
        return
    
    # Send the test message
    success = await send_direct_message(chat_id)
    
    if success:
        print("✅ Test completed successfully!")
        print(f"Check your Telegram chat (ID: {chat_id}) for the test message")
    else:
        print("❌ Test failed. Check the logs for more details.")
        print("Make sure you've started a conversation with the bot first!")


if __name__ == "__main__":
    asyncio.run(main())