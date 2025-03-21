import requests
import json
import time

def test_arabic_webhook():
    """Test sending an Arabic news webhook to the local server."""
    url = "http://localhost:5000/news-webhook"
    
    # Prepare the news data with the provided Arabic content
    news_data = {
        "secret": "crypto_news_webhook_secret_2025",
        "news": {
            "id": "arabic-test-123",
            "title": "أخبار الكريبتو هنا",  # The exact message you provided
            "content": "هذا محتوى اختباري للتحقق من عمل بوت الأخبار. نحن نختبر الآن إرسال المحتوى باللغة العربية.",
            "source": "اختبار المستخدم",
            "url": "https://example.com/arabic-test",
            "image_url": "",
            "tags": ["كريبتو", "بيتكوين", "إيثريوم"]
        }
    }
    
    # Send the POST request
    print("Sending Arabic test webhook...")
    try:
        response = requests.post(
            url, 
            headers={'Content-Type': 'application/json'},
            data=json.dumps(news_data)
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("Success! The Arabic webhook was processed.")
            print("\nHere's the message that would be sent to Telegram:")
            
            # Create a formatted example of what would be sent
            formatted_message = f"""
📰 *أخبار الكريبتو هنا*

هذا محتوى اختباري للتحقق من عمل بوت الأخبار. نحن نختبر الآن إرسال المحتوى باللغة العربية.

📊 *المصدر*: اختبار المستخدم
🔗 [اقرأ المزيد](https://example.com/arabic-test)

#كريبتو #بيتكوين #إيثريوم

📱 مقدم من: بوت أخبار الكريبتو من إنفترون داو
"""
            print(formatted_message)
        else:
            print("Failed to process the webhook.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Wait a moment for the server to be ready
    time.sleep(1)
    test_arabic_webhook()