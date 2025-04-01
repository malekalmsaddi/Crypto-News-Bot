import asyncio
import logging
import os
import database
from models import News
from database import get_all_chats, log_message
from telegram import Bot
from telegram.constants import ParseMode  # Updated for compatibility with python-telegram-bot v20+
from telegram.error import TelegramError

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get the bot token from environment variables
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

async def broadcast_to_all_chats():
    """
    Send a test news message to all chats where the bot is a member.
    """
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not found in environment variables.")
        return False
    
    try:
        # Initialize the bot
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
    except Exception as e:
        print(f"❌ Failed to initialize the bot: {str(e)}")
        return False
    
    try:
        # Get bot info
        bot_info = await bot.get_me()
        print(f"✓ Connected to bot: {bot_info.first_name} (@{bot_info.username})")
        
        # Get all chats from the database
        chats = get_all_chats()
        
        if not chats:
            print("\n❌ No chats found in the database.")
            print("Add chats using add_test_chat.py before running this script.")
            return False
        
        print(f"\nFound {len(chats)} chats in the database:")
        for i, chat in enumerate(chats, 1):
            print(f"{i}. {chat['chat_title']} (ID: {chat['chat_id']}, Type: {chat['chat_type']})")
        
        # Create a test news item about Ethereum in Arabic
        test_news = News(
            news_id="broadcast-test-002",
            title="إيثريوم يتابع صعوده وسط أنباء عن تحديثات جديدة",
            content="أظهر سعر الإيثريوم (ETH) قوة ملحوظة اليوم، متجاوزاً مستوى 4000 دولار وسط أنباء عن تحديثات تقنية مرتقبة. يأتي هذا في وقت تشهد فيه العملات الرقمية البديلة تعافياً قوياً بعد فترة من التراجع.",
            source="بوت أخبار الكريبتو - اختبار",
            url="https://example.com/eth-updates",
            image_url="",
            tags=["إيثريوم", "سعر_قياسي", "تحديثات_تقنية", "ETH"]
        )
        
        # Format the message
        formatted_message = test_news.format_telegram_message()
        
        print("\n📣 Starting broadcast...")
        
        success_count = 0
        error_count = 0
        
        for chat in chats:
            chat_id = chat['chat_id']
        
            try:
                print(f"Sending to: {chat['chat_title']} (ID: {chat_id})")
                
                # Send the message using the bot instance
                message = await bot.send_message(
                    chat_id=chat_id,
                    text=formatted_message,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=False
                )
                
                # Log the sent message
                log_message(test_news.news_id, chat_id, message.message_id)
                
                print(f"✓ Message sent successfully to {chat['chat_title']}")
                success_count += 1
                
                # Sleep briefly to avoid hitting rate limits
                await asyncio.sleep(0.5)
                
            except TelegramError as e:
                print(f"❌ Failed to send message to {chat['chat_title']}: {str(e)}")
                
                if "chat not found" in str(e).lower() or "bot was kicked" in str(e).lower():
                    print(f"  ⚠️ The bot may have been removed from this chat or the chat no longer exists.")
                    await remove_invalid_chat(chat_id)  # Remove invalid chat
                
                error_count += 1
        
        print(f"\n📊 Broadcast completed:")
        print(f"✓ Success: {success_count} chats")
        print(f"❌ Errors: {error_count} chats")
        
        if success_count > 0:
            return True
        else:
            return False
        
    except Exception as e:
        print(f"\n❌ Error during broadcast: {str(e)}")
        return False

async def remove_invalid_chat(chat_id):
    """
    Remove invalid chats from the database.
    """
    try:
        print(f"Removing invalid chat with ID: {chat_id}")
        # Remove the `await` if the function is synchronous
        database.remove_chat(chat_id)  # Ensure this function is synchronous in your database module
        print(f"✓ Chat with ID {chat_id} removed successfully.")
    except Exception as e:
        print(f"❌ Failed to remove chat with ID {chat_id}: {str(e)}")
if __name__ == "__main__":
    print("📣 Broadcast Test - أخبار الكريبتو من إنفترون داو")
    print("--------------------------------------------------")
    
    # Run the async function
    success = asyncio.run(broadcast_to_all_chats())
    
    if success:
        print("\n✅ Test completed successfully!")
    else:
        print("\n⚠️ To test broadcasting to chats:")
        print("1. Make sure the bot is added to at least one chat")
        print("2. Add chat(s) to the database using add_test_chat.py")
        print("3. Run this script again")