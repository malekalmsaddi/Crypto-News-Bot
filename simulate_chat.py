import logging
import database
from models import News
import asyncio
from bot import broadcast_news

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_broadcast():
    """
    Simulate broadcasting a message to a chat.
    
    This function:
    1. Adds a simulated chat to the database
    2. Creates a test news message in Arabic
    3. Broadcasts the message using the bot's broadcast function
    """
    # First, clear any existing chats (for testing purposes)
    chats = database.get_all_chats()
    for chat in chats:
        database.remove_chat(chat['chat_id'])
    
    # Add a simulated chat (using a test chat ID)
    test_chat_id = -1001234567890  # Simulated group chat ID
    database.add_chat(test_chat_id, "اختبار مجموعة أخبار الكريبتو", "group")
    logger.info(f"Added test chat with ID: {test_chat_id}")
    
    # Create a news item
    news = News(
        news_id="test-arabic-123",
        title="أخبار الكريبتو هنا",
        content="هذا اختبار لبوت نشر أخبار الكريبتو. إذا رأيت هذه الرسالة، فهذا يعني أن البوت يعمل بشكل صحيح!",
        source="اختبار البوت",
        url="https://example.com/test",
        image_url="",
        tags=["اختبار", "بيتكوين", "كريبتو"]
    )
    
    # Show what would be sent
    formatted_message = news.format_telegram_message()
    logger.info(f"Formatted message that would be sent:\n{formatted_message}")
    
    logger.info("Note: The actual message won't be delivered since this is a simulation with a fake chat ID")
    
    # Try to broadcast (this will attempt to send but will likely fail due to invalid chat ID)
    try:
        success_count, error_count = await broadcast_news(news)
        logger.info(f"Broadcast result: Success: {success_count}, Errors: {error_count}")
    except Exception as e:
        logger.error(f"Error in broadcasting: {e}")
    
    # Get all chats to verify
    chats_after = database.get_all_chats()
    logger.info(f"Chats in database: {chats_after}")

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_broadcast())