import logging
import os
import asyncio
from models import News
from telegram import Bot, ParseMode

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get the bot token from environment variables
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TEST_CHAT_ID = "-1001234567890"  # Our test group chat ID

async def send_direct_test_message():
    """
    Send a test message directly to a specific Telegram chat.
    This is useful for testing without needing to simulate the webhook process.
    """
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables.")
        return False
    
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        
        # Get bot info - in PTB v13.15, get_me() is not async
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
        
        # First try to send with plain text (no formatting)
        print(f"\nAttempting to send plain text message to chat ID: {TEST_CHAT_ID}")
        simple_message = f"🔄 اختبار: بيتكوين يتجاوز 75 ألف دولار\n\nهذه رسالة اختبار بدون تنسيق من بوت أخبار الكريبتو."
        
        await bot.send_message(
            chat_id=TEST_CHAT_ID,
            text=simple_message
        )
        print("✅ Plain text message sent successfully!")
        
        # Now try to send the formatted message with limited markdown
        print(f"\nAttempting to send formatted message to chat ID: {TEST_CHAT_ID}")
        
        try:
            # We'll use a more careful formatting approach to avoid Markdown parsing issues
            safe_message = (
                f"₿ *بيتكوين يتجاوز سعر 75 ألف دولار لأول مرة*\n\n"
                f"في تطور مثير، تجاوز سعر بيتكوين 75000 دولار أمريكي لأول مرة في التاريخ، "
                f"مما يعكس ثقة المستثمرين المتزايدة في العملات الرقمية.\n\n"
                f"📊 *المصدر*: بوت أخبار الكريبتو - اختبار\n"
                f"🔗 [اقرأ المزيد](https://example.com/btc-75k)\n\n"
                f"#بيتكوين #سعر_قياسي #عملات_رقمية #استثمار\n\n"
                f"🟢 السوق: صاعد\n\n"
                f"📱 مقدم من: بوت أخبار الكريبتو من إنفترون داو"
            )
            
            await bot.send_message(
                chat_id=TEST_CHAT_ID,
                text=safe_message,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=False
            )
            print("✅ Formatted message sent successfully!")
            
        except Exception as e:
            print(f"❌ Error sending formatted message: {str(e)}")
            
            # If formatted message fails, try without parse_mode
            print("\nRetrying with original formatted message but without parse_mode...")
            try:
                await bot.send_message(
                    chat_id=TEST_CHAT_ID,
                    text=formatted_message
                )
                print("✅ Unformatted original message sent successfully!")
            except Exception as e2:
                print(f"❌ Error sending unformatted message: {str(e2)}")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to execute test broadcast: {e}")
        print(f"\n❌ Error in test broadcast: {str(e)}")
        return False

if __name__ == "__main__":
    print("Starting broadcast test...")
    # Run the async function
    success = asyncio.run(send_direct_test_message())
    
    if success:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed.")