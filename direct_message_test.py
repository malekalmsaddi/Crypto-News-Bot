import logging
import os
import sys
from models import News
from telegram import Bot, Update
from telegram.constants import ParseMode

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get the bot token from environment variables
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

def send_direct_message_to_user(chat_id=None):
    """
    Send a direct test message to a specific user chat ID.
    
    Usage:
    1. Start a conversation with your bot on Telegram
    2. Run this script with your chat ID:
       python direct_message_test.py YOUR_CHAT_ID
    
    To get your Telegram chat ID:
    - Talk to @userinfobot on Telegram
    """
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not found in environment variables.")
        return False
    
    # Check if chat ID was provided
    if not chat_id and len(sys.argv) > 1:
        chat_id = sys.argv[1]
    
    if not chat_id:
        print("\n⚠️ Please provide a chat ID to send a test message to.")
        print("Usage: python direct_message_test.py YOUR_CHAT_ID")
        print("\nTo get your personal chat ID, talk to @userinfobot on Telegram.")
        return False
    
    try:
        # Initialize the bot
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        
        # Get bot info
        bot_info = bot.get_me()
        print(f"✓ Connected to bot: {bot_info.first_name} (@{bot_info.username})")
        
        # Create a test news item about Bitcoin in Arabic
        test_news = News(
            news_id="direct-message-test-001",
            title="بيتكوين يتجاوز سعر 75 ألف دولار لأول مرة",
            content="في تطور مثير، تجاوز سعر بيتكوين 75000 دولار أمريكي لأول مرة في التاريخ، مما يعكس ثقة المستثمرين المتزايدة في العملات الرقمية. ويأتي هذا الارتفاع وسط إقبال مؤسسي متزايد وتوقعات إيجابية للسوق.",
            source="بوت أخبار الكريبتو - اختبار",
            url="https://example.com/btc-75k",
            image_url="",
            tags=["بيتكوين", "سعر_قياسي", "عملات_رقمية", "استثمار"]
        )
        
        # Format the message
        formatted_message = test_news.format_telegram_message()
        
        print(f"\nAttempting to send test message to chat ID: {chat_id}")
        
        # Send the message
        message = bot.send_message(
            chat_id=chat_id,
            text=formatted_message,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False
        )
        
        print(f"\n✅ Success! Message sent to chat ID: {chat_id}")
        print(f"Message ID: {message.message_id}")
        
        # Also send a simple message without formatting
        simple_message = f"🔄 اختبار: هذه رسالة اختبار بدون تنسيق من بوت أخبار الكريبتو."
        
        bot.send_message(
            chat_id=chat_id,
            text=simple_message
        )
        
        print("✅ Simple message sent successfully!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error sending message: {str(e)}")
        print("\nPossible reasons for failure:")
        print("1. The chat ID is incorrect")
        print("2. You haven't started a conversation with the bot")
        print("3. The bot token is invalid")
        return False

if __name__ == "__main__":
    print("🚀 Direct Message Test - أخبار الكريبتو من إنفترون داو")
    print("-----------------------------------------------------")
    
    success = send_direct_message_to_user()
    
    if success:
        print("\n✅ Test completed successfully!")
    else:
        print("\n⚠️ To test the bot messaging:")
        print("1. Start a conversation with your bot on Telegram")
        print("2. Get your chat ID from @userinfobot")
        print("3. Run: python direct_message_test.py YOUR_CHAT_ID")