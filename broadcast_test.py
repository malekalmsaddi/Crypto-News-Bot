import logging
import os
import sys
from models import News
from telegram import Bot, ParseMode

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get the bot token from environment variables
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

def send_direct_test_message():
    """
    Send a test message directly to a specific Telegram chat.
    This is useful for testing without needing to simulate the webhook process.
    """
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables.")
        return
    
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    # Get bot info
    bot_info = bot.get_me()
    logger.info(f"Connected to bot: {bot_info.first_name} (@{bot_info.username})")
    
    # Create a test news item about Bitcoin in Arabic
    test_news = News(
        news_id="broadcast-test-001",
        title="بيتكوين يتجاوز سعر 75 ألف دولار لأول مرة",
        content="في تطور مثير، تجاوز سعر بيتكوين 75000 دولار أمريكي لأول مرة في التاريخ، مما يعكس ثقة المستثمرين المتزايدة في العملات الرقمية. ويأتي هذا الارتفاع وسط إقبال مؤسسي متزايد وتوقعات إيجابية للسوق.",
        source="بوت أخبار الكريبتو - اختبار",
        url="https://example.com/btc-75k",
        image_url="",
        tags=["بيتكوين", "سعر_قياسي", "عملات_رقمية", "استثمار"]
    )
    
    # Format the message using our enhanced formatter
    formatted_message = test_news.format_telegram_message()
    logger.info(f"Formatted message:\n{formatted_message}")
    
    # Ask user for a chat ID to send to
    print("\nDo you want to send this test message to your Telegram account or group?")
    print("If yes, please provide the chat ID when running the script again with:")
    print("python broadcast_test.py YOUR_CHAT_ID")
    print("\nTo get your personal chat ID, talk to @userinfobot on Telegram.")
    print("To get a group chat ID, add @RawDataBot to the group temporarily.")
    
    # Check if chat ID was provided as command line argument
    if len(sys.argv) > 1:
        try:
            chat_id = sys.argv[1]
            
            # Try to send the message
            print(f"\nAttempting to send test message to chat ID: {chat_id}")
            message = bot.send_message(
                chat_id=chat_id,
                text=formatted_message,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=False
            )
            
            print(f"\n✅ Success! Message sent to chat ID: {chat_id}")
            print(f"Message ID: {message.message_id}")
            
        except Exception as e:
            print(f"\n❌ Error sending message: {str(e)}")
            print("\nPossible reasons for failure:")
            print("1. The chat ID is incorrect")
            print("2. The bot is not a member of the specified group")
            print("3. The bot doesn't have permission to send messages in the group")
            print("4. You haven't started a conversation with the bot (for direct messages)")
    
if __name__ == "__main__":
    # Run the test
    send_direct_test_message()