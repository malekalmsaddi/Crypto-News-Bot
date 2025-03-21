#!/usr/bin/env python3
"""
Add a group to the database using a Telegram group link.

This script:
1. Prompts the user for a group link
2. Asks for a chat ID to associate with the link (since we can't extract it directly from the link)
3. Adds the group to the database with a descriptive title
4. Optionally sends a test message to the group

Usage:
python add_group_link.py
"""

import asyncio
import sys
import logging
import sqlite3
from datetime import datetime
import re

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import project modules
from bot import broadcast_news
from models import News
import database


def extract_group_info(group_link):
    """Try to extract information from a group link"""
    
    # For testing, check if it's a group link
    if not group_link or not group_link.startswith('https://t.me/'):
        logger.error(f"Invalid group link format: {group_link}")
        return None
        
    # Extract any identifiable information from the link
    # For private groups with invite links, we can't extract the actual ID
    link_id = group_link.split('t.me/')[1]
    
    # For readable info
    if link_id.startswith('+'):
        return f"Private group with invite code: {link_id[1:][:8]}..."
    else:
        return f"Public group: @{link_id}"


def clean_test_chats():
    """Remove all test chats from the database"""
    conn = sqlite3.connect('bot_database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chats")
    conn.commit()
    conn.close()
    logger.info("Cleaned all chats from database")


def add_group_chat(chat_id, group_link):
    """Add a group chat to the database"""
    if not chat_id:
        logger.error("No chat ID provided.")
        return False
    
    # Convert to integer to ensure it's a valid ID
    try:
        chat_id = int(chat_id)
    except ValueError:
        logger.error(f"Invalid chat ID format: {chat_id}. Must be an integer.")
        return False
    
    # Create a descriptive name based on the link
    group_info = extract_group_info(group_link)
    chat_title = f"مجموعة أخبار الكريبتو - {group_info}" if group_info else f"مجموعة أخبار الكريبتو {chat_id}"
    
    # Add chat to database
    database.add_chat(chat_id, chat_title, "supergroup")
    logger.info(f"Added group chat ID {chat_id} to database")
    return True


def create_test_news():
    """Create a test crypto news item"""
    return News(
        news_id=f"test-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        title="🚀 اختبار إرسال لمجموعة: أخبار بيتكوين",
        content="هذا اختبار لبوت أخبار الكريبتو للتأكد من إمكانية الإرسال للمجموعات. إذا كنت ترى هذه الرسالة، فهذا يعني أن البوت يعمل بشكل صحيح ويمكنه إرسال الأخبار تلقائياً للمجموعات. البيتكوين يتجاوز الـ 70 ألف دولار!",
        source="اختبار بوت أخبار الكريبتو",
        url="https://example.com/crypto-news-group-test",
        tags=["اختبار", "بيتكوين", "أخبار_المجموعات"]
    )


async def send_test_message():
    """Send a test news message to all configured chats"""
    # Create test news
    news = create_test_news()
    
    # Broadcast the news to all chats (which should now include our group)
    success, errors = await broadcast_news(news)
    
    if success > 0:
        logger.info(f"✅ Test message sent successfully to {success} chats")
        return True
    else:
        logger.error(f"❌ Failed to send test messages. Errors: {errors}")
        return False


async def main():
    """Main function"""
    print("🔄 إضافة مجموعة إلى قاعدة البيانات")
    print("-" * 50)
    
    if len(sys.argv) < 3:
        # Get info from user
        print("📝 أدخل رابط المجموعة:")
        group_link = input("> ").strip()
        
        print("\n📝 أدخل معرف المجموعة:")
        print("(يمكنك الحصول على المعرف من مطور البوت، عادةً يكون بالصيغة -100xxxxxxxxxx)")
        chat_id = input("> ").strip()
    else:
        group_link = sys.argv[1]
        chat_id = sys.argv[2]
    
    # Clean database and add only the target group
    clean_test_chats()
    
    if not add_group_chat(chat_id, group_link):
        return
    
    print(f"\n✅ تمت إضافة المجموعة بمعرف {chat_id} إلى قاعدة البيانات")
    
    # Ask if user wants to send a test message
    print("\nهل تريد إرسال رسالة اختبارية للمجموعة؟ (y/n)")
    choice = input("> ").strip().lower()
    
    if choice == 'y':
        print("\n🔄 جاري إرسال رسالة اختبارية...")
        success = await send_test_message()
        
        if success:
            print("✅ تم إرسال الرسالة الاختبارية بنجاح!")
            print("تحقق من المجموعة للتأكد من وصول الرسالة")
        else:
            print("❌ فشل إرسال الرسالة الاختبارية. تحقق من السجلات لمزيد من التفاصيل.")
            print("تأكد من:")
            print("1. أن البوت عضو في المجموعة")
            print("2. أن للبوت صلاحيات إرسال الرسائل")
            print("3. أن معرف المجموعة صحيح")
    else:
        print("\nلم يتم إرسال رسالة اختبارية.")
        print("يمكنك اختبار البوت لاحقاً باستخدام:")
        print("python test_webhook_endpoint.py")


if __name__ == "__main__":
    asyncio.run(main())