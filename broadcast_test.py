import logging
import os
import asyncio
from models import News
from telegram import Bot, Update
from telegram.constants import ParseMode
from config import TELEGRAM_BOT_TOKEN # Added import
from database import get_all_chats, log_message # Added import
from datetime import datetime # Added import

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

#Removed original send_direct_test_message function

async def test_broadcast():
    """Send a test broadcast message to all chats"""
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not found in environment variables.")
        return False

    try:
        # Initialize bot
        bot = Bot(token=TELEGRAM_BOT_TOKEN)

        # Create test news
        test_news = News(
            news_id=f"test-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            title="🔄 اختبار البث المباشر",
            content="هذه رسالة اختبار للتأكد من عمل نظام البث المباشر في بوت أخبار الكريبتو. إذا وصلتك هذه الرسالة، فهذا يعني أن النظام يعمل بشكل صحيح.",
            source="بوت أخبار الكريبتو",
            url="https://example.com/test",
            image_url="",
            tags=["اختبار", "بث_مباشر"]
        )

        # Get all chats
        chats = get_all_chats()
        if not chats:
            print("❌ No chats found in database.")
            return False

        print(f"\nBroadcasting to {len(chats)} chats...")
        success_count = 0
        error_count = 0

        # Send to each chat
        for chat in chats:
            try:
                message = await bot.send_message(
                    chat_id=chat['chat_id'],
                    text=test_news.format_telegram_message(),
                    parse_mode=None
                )
                log_message(test_news.news_id, chat['chat_id'], message.message_id)
                print(f"✓ Sent to {chat['chat_title']}")
                success_count += 1
                await asyncio.sleep(0.1)  # Prevent rate limiting
            except Exception as e:
                print(f"❌ Failed to send to {chat['chat_title']}: {str(e)}")
                error_count += 1

        print(f"\n📊 Broadcast Results:")
        print(f"✓ Success: {success_count}")
        print(f"❌ Errors: {error_count}")
        return success_count > 0

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting broadcast test...")
    success = asyncio.run(test_broadcast())
    if success:
        print("\n✅ Broadcast test completed successfully!")
    else:
        print("\n❌ Broadcast test failed.")