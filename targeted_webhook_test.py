#!/usr/bin/env python3
"""
Test sending a news webhook to a specific target chat ID.

This script sends a simulated news webhook to the local server,
but instructs the server to send it only to a specific chat ID
rather than broadcasting to all chats.

Usage:
python targeted_webhook_test.py YOUR_CHAT_ID
"""

import json
import sys
import requests
from datetime import datetime

from config import WEBHOOK_SECRET
from models import News

# Server URL - using localhost for testing
SERVER_URL = "http://localhost:5000/news-webhook"

def test_targeted_webhook(target_chat_id):
    """Test sending a news webhook to a specific chat ID."""
    if not target_chat_id:
        print("⚠️ Error: No target chat ID provided!")
        print("Usage: python targeted_webhook_test.py YOUR_CHAT_ID")
        return False

    # Try to convert to integer to validate
    try:
        int(target_chat_id)
    except ValueError:
        print(f"⚠️ Error: '{target_chat_id}' is not a valid chat ID (must be an integer)")
        return False

    # Create test news
    news_id = f"test-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    news = {
        "id": news_id,
        "title": "🚀 اختبار موجّه: أخبار البيتكوين",
        "content": "هذا اختبار مباشر موجّه لبوت أخبار الكريبتو. إذا كنت ترى هذه الرسالة، فهذا يعني أن البوت يعمل بشكل صحيح ويمكنه إرسال الأخبار موجهة إلى محادثة معينة. بلغت أسعار البيتكوين مستويات قياسية اليوم!",
        "source": "اختبار إرسال موجّه لبوت أخبار الكريبتو",
        "url": "https://example.com/crypto-news-targeted-test",
        "tags": ["اختبار_موجه", "بيتكوين", "أخبار_كريبتو"]
    }

    # Create request payload with target chat ID
    payload = {
        "secret": WEBHOOK_SECRET,
        "news": news,
        "target_chat_id": target_chat_id
    }

    print(f"🔄 اختبار إرسال موجّه - بوت أخبار الكريبتو")
    print("-" * 50)
    print(f"💬 الإرسال إلى معرف المحادثة: {target_chat_id}")
    print("\n📰 محتوى الخبر الاختباري:")
    print(f"العنوان: {news['title']}")
    print(f"المحتوى: {news['content']}")
    print(f"المصدر: {news['source']}")
    if 'tags' in news:
        print(f"الوسوم: {', '.join(news['tags'])}")

    print(f"\n📡 جاري إرسال الويب هوك إلى: {SERVER_URL}")
    
    try:
        response = requests.post(SERVER_URL, json=payload)
        print(f"📊 حالة الاستجابة: {response.status_code}")

        if response.status_code == 200:
            print("✅ تم استلام الويب هوك بنجاح!")
            print(f"الاستجابة: {response.text}")
            return True
        else:
            print(f"❌ فشل إرسال الويب هوك: {response.text}")
            return False
    except Exception as e:
        print(f"❌ خطأ في إرسال الويب هوك: {e}")
        return False
    finally:
        print("\n✅ اكتمل اختبار الويب هوك!")
        print("تحقق من سجلات الخادم لمعرفة ما إذا تم معالجة الخبر بشكل صحيح.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python targeted_webhook_test.py YOUR_CHAT_ID")
        print("Example: python targeted_webhook_test.py 123456789")
        sys.exit(1)
    
    target_id = sys.argv[1]
    test_targeted_webhook(target_id)