import logging
import os
from models import News
from database import get_all_chats
from bot import broadcast_news

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def broadcast_to_all_chats():
    """
    Send a test news message to all chats where the bot is a member.
    This uses the broadcast_news function from bot.py to send to all registered chats.
    """
    # Create a test news item about Ethereum in Arabic
    test_news = News(
        news_id="broadcast-all-test-001",
        title="إيثيريوم يستعد للتحديث الجديد ويتوقع ارتفاع في الأسعار",
        content="أعلن مطورو إيثيريوم عن موعد التحديث القادم للشبكة، والذي من المتوقع أن يحسن كفاءة المعاملات ويقلل من رسوم الغاز. وتشير التحليلات إلى أن هذا التحديث قد يؤدي إلى ارتفاع سعر الإيثيريوم خلال الأسابيع القادمة نتيجة زيادة الثقة في النظام البيئي.",
        source="بوت أخبار الكريبتو - اختبار بث شامل",
        url="https://example.com/eth-update",
        image_url="",
        tags=["إيثيريوم", "تحديث_الشبكة", "عملات_رقمية", "تقنية_بلوكتشين"]
    )
    
    # Get all chats from the database
    chats = get_all_chats()
    if not chats:
        logger.warning("No chats found in the database. The bot needs to be added to at least one chat.")
        print("\n❌ No chats found in database. Try adding the bot to a group first.")
        print("You can also use broadcast_test.py to send to a specific chat ID.")
        return
    
    # Show chat information
    print(f"\nFound {len(chats)} chat(s) in the database:")
    for i, chat in enumerate(chats, 1):
        chat_id, title, chat_type = chat
        print(f"{i}. {title} (ID: {chat_id}, Type: {chat_type})")
    
    # Ask for confirmation
    print("\nDo you want to broadcast a test message to ALL these chats?")
    confirmation = input("Type 'YES' to confirm or anything else to cancel: ")
    
    if confirmation.upper() == 'YES':
        print("\nBroadcasting test message to all chats...")
        try:
            # This call may need to be await if you're using asyncio
            result = broadcast_news(test_news)
            print(f"\n✅ Message broadcast complete. Result: {result}")
        except Exception as e:
            print(f"\n❌ Error broadcasting message: {str(e)}")
    else:
        print("\nBroadcast cancelled.")

if __name__ == "__main__":
    # Run the broadcast
    broadcast_to_all_chats()