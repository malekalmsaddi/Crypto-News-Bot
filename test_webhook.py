import requests
import json
import time

def test_webhook():
    """Test sending a news webhook to the local server."""
    url = "http://localhost:5000/news-webhook"
    
    # Prepare the news data with Arabic content
    news_data = {
        "secret": "crypto_news_webhook_secret_2025",
        "news": {
            "id": "test-123",
            "title": "أخبار الكريبتو هنا",  # "Cryptocurrency news here"
            "content": "هذا اختبار لبوت نشر أخبار الكريبتو. إذا رأيت هذه الرسالة، فهذا يعني أن البوت يعمل بشكل صحيح!",  # This is a test for the crypto news broadcasting bot. If you see this message, it means the bot is working correctly!
            "source": "اختبار البوت",  # Bot Test
            "url": "https://example.com/test",
            "image_url": "",
            "tags": ["اختبار", "بيتكوين", "كريبتو"]  # Test, Bitcoin, Crypto
        }
    }
    
    # Send the POST request
    print("Sending test webhook...")
    try:
        response = requests.post(
            url, 
            headers={'Content-Type': 'application/json'},
            data=json.dumps(news_data)
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("Success! The webhook was processed.")
        else:
            print("Failed to process the webhook.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Wait a moment for the server to be ready
    time.sleep(1)
    test_webhook()