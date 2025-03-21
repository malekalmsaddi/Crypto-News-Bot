import logging
import os
import json
import random
import requests
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load config (update this if you have a different way to get config)
try:
    from config import WEBHOOK_SECRET, WEBHOOK_URL
except ImportError:
    # Fallback if not imported from config
    WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET')
    WEBHOOK_URL = os.environ.get('WEBHOOK_URL', 'http://localhost:5000')

def simulate_webhook(use_arabic=True):
    """
    Simulate sending a news webhook to the local server.
    This tests the end-to-end functionality of receiving news and broadcasting it.
    """
    # Define the news data (with Arabic content if specified)
    if use_arabic:
        news_id = f"simulated-news-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Random list of Arabic cryptocurrency news titles
        titles = [
            "بيتكوين يتجاوز مستوى جديد ويسجل رقماً قياسياً",
            "إيثيريوم يستعد لتحديث جديد يخفض رسوم الغاز",
            "قرار جديد من هيئة الأوراق المالية حول ETF البيتكوين",
            "سولانا تحقق نمواً هائلاً وتنافس المنصات الكبرى",
            "بينانس تطلق ميزات جديدة للمستخدمين العرب",
            "الريبل يفوز في جزء من قضيته مع هيئة الأوراق المالية"
        ]
        
        # Random list of Arabic cryptocurrency news content
        contents = [
            "في تطور مثير، سجل سعر البيتكوين رقماً قياسياً جديداً متجاوزاً جميع التوقعات. ويأتي هذا الارتفاع بعد موجة من الاستثمارات المؤسسية الكبيرة والإقبال المتزايد على العملات الرقمية.",
            "أعلن مطورو إيثيريوم عن موعد التحديث الجديد للشبكة، والذي سيهدف إلى تخفيض رسوم المعاملات وزيادة سرعة الشبكة. ويتوقع الخبراء أن يؤدي هذا التحديث إلى تعزيز قيمة الإيثر.",
            "أصدرت هيئة الأوراق المالية قراراً جديداً بشأن صناديق البيتكوين المتداولة، مما أثار موجة من ردود الفعل الإيجابية في أسواق العملات الرقمية وأدى إلى ارتفاع الأسعار.",
            "حققت عملة سولانا قفزة كبيرة في سعرها خلال الأسبوع الماضي، مدفوعة بتزايد استخدام التطبيقات اللامركزية على منصتها والاهتمام المؤسسي المتزايد بتقنيتها فائقة السرعة.",
            "أعلنت منصة بينانس عن مجموعة من الميزات الجديدة الموجهة للمستخدمين في العالم العربي، بما في ذلك دعم أساليب دفع محلية جديدة وواجهة مستخدم محسنة باللغة العربية.",
            "أعلنت شركة ريبل عن تقدم إيجابي في قضيتها القانونية المستمرة مع هيئة الأوراق المالية الأمريكية، مما أدى إلى ارتفاع سعر العملة وزيادة ثقة المستثمرين في مستقبلها."
        ]
        
        # Random list of Arabic sources
        sources = [
            "وكالة أنباء الكريبتو",
            "بوابة البلوكشين",
            "مجلة العملات الرقمية",
            "شبكة أخبار التقنية المالية",
            "صحيفة الاقتصاد الرقمي"
        ]
        
        # Random list of Arabic tags
        tag_options = [
            ["بيتكوين", "عملات_رقمية", "سعر_قياسي"],
            ["إيثيريوم", "تحديث", "تطوير_البلوكشين"],
            ["تنظيم", "هيئات_رقابية", "استثمار"],
            ["سولانا", "نمو", "منصات_لامركزية"],
            ["بينانس", "منصات_تداول", "خدمات_عربية"],
            ["ريبل", "قضايا_قانونية", "تنظيم"]
        ]
        
        # Select random items from each list
        rand_idx = random.randint(0, min(len(titles), len(contents), len(tag_options)) - 1)
        title = titles[rand_idx]
        content = contents[rand_idx]
        tags = tag_options[rand_idx]
        source = random.choice(sources)
        
    else:
        # English fallback
        news_id = f"simulated-news-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        title = "Bitcoin Reaches New All-Time High"
        content = "Bitcoin has reached a new all-time high price today, surpassing all analyst predictions. The surge comes amid increasing institutional adoption and growing interest in digital assets."
        source = "Crypto News Network"
        tags = ["bitcoin", "price", "record"]
    
    # Create the webhook payload
    webhook_data = {
        "secret": WEBHOOK_SECRET,
        "news": {
            "id": news_id,
            "title": title,
            "content": content,
            "source": source,
            "url": "https://example.com/news/" + news_id,
            "image_url": "",
            "tags": tags
        }
    }
    
    # Print the payload for verification
    print(f"\n🔵 Simulating webhook with the following news:")
    print(f"Title: {title}")
    print(f"Content: {content}")
    print(f"Source: {source}")
    print(f"Tags: {', '.join(tags)}")
    print(f"URL: https://example.com/news/{news_id}")
    
    # Automatically confirm in this environment
    print("\nAutomatically sending webhook...")
    confirm = 'y'
    
    # Send the webhook to the local server
    webhook_url = f"{WEBHOOK_URL}/webhook/news"
    
    if not WEBHOOK_SECRET:
        print("\n⚠️ WEBHOOK_SECRET is not set. Using 'test_secret' as a placeholder.")
        webhook_data["secret"] = "test_secret"
    
    try:
        response = requests.post(
            webhook_url,
            json=webhook_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n📡 Webhook sent to: {webhook_url}")
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Webhook received successfully!")
            print(f"Response: {response.text}")
        else:
            print(f"❌ Webhook failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error sending webhook: {str(e)}")

if __name__ == "__main__":
    # Automatically use Arabic content in this environment
    print("Using Arabic content by default...")
    use_arabic = True
    
    # Send the webhook
    simulate_webhook(use_arabic)