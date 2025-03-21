import requests
import json
import os
import sys
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Default test configuration
WEBHOOK_URL = "http://localhost:5000/news-webhook"
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "crypto_news_webhook_secret_2025")

def test_webhook_endpoint(chat_id=None):
    """
    Test the webhook endpoint by sending a simulated news item.
    
    If a chat_id is provided, the webhook will request direct sending to that chat.
    
    Usage:
    python test_webhook_endpoint.py [CHAT_ID]
    """
    # Check if chat_id was provided as command line argument
    if not chat_id and len(sys.argv) > 1:
        chat_id = sys.argv[1]
    
    # Generate a unique news ID based on timestamp
    news_id = f"test-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Create test news data
    test_news = {
        "id": news_id,
        "title": "سوق الكريبتو يشهد انتعاشاً قوياً بعد قرارات البنوك المركزية",
        "content": "شهدت أسواق العملات الرقمية انتعاشاً ملحوظاً اليوم بعد قرارات البنوك المركزية العالمية بخفض أسعار الفائدة. وارتفعت قيمة البيتكوين بنسبة 5٪ في الساعات الأخيرة، في حين حققت العملات البديلة مكاسب أكبر.",
        "source": "اختبار بوت أخبار الكريبتو",
        "url": f"https://example.com/crypto-news/{news_id}",
        "image_url": "",
        "tags": ["بيتكوين", "أسواق_الكريبتو", "بنوك_مركزية", "أسعار_الفائدة"]
    }
    
    # Prepare webhook payload
    webhook_data = {
        "secret": WEBHOOK_SECRET,
        "news": test_news
    }
    
    # Add specific chat_id if provided
    if chat_id:
        webhook_data["target_chat_id"] = chat_id
        print(f"Targeting specific chat ID: {chat_id}")
    
    # Print the news being sent
    print("\n📰 Test News Content:")
    print(f"Title: {test_news['title']}")
    print(f"Content: {test_news['content']}")
    print(f"Source: {test_news['source']}")
    print(f"Tags: {', '.join(test_news['tags'])}")
    
    # Send the webhook to the local server
    try:
        print(f"\n📡 Sending webhook to: {WEBHOOK_URL}")
        response = requests.post(
            WEBHOOK_URL,
            json=webhook_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Webhook received successfully!")
            print(f"Response: {response.text}")
            return True
        else:
            print(f"❌ Webhook failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending webhook: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔄 Webhook Test - أخبار الكريبتو من إنفترون داو")
    print("-------------------------------------------------")
    
    success = test_webhook_endpoint()
    
    if success:
        print("\n✅ Webhook test completed successfully!")
        print("Check the server logs to see if the news was processed correctly.")
    else:
        print("\n❌ Webhook test failed.")
        print("Make sure the server is running and accessible at the configured URL.")