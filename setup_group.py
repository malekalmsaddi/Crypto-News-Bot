#!/usr/bin/env python3
"""
اختبار سريع لإرسال رسائل إلى مجموعة التلغرام

هذا السكريبت:
1. يضيف المجموعة المقدمة إلى قاعدة البيانات
2. ينشئ رسالة اختبار
3. يرسل الرسالة إلى المجموعة

استخدام:
python setup_group.py -100xxxxxxxxxx

أو

python setup_group.py  # وسيطلب منك إدخال معرف المجموعة
"""

import asyncio
import sys
import logging
from datetime import datetime

# إعداد التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# استيراد وحدات المشروع
from bot import broadcast_news
from models import News
import database


def reset_database():
    """إزالة جميع المحادثات من قاعدة البيانات"""
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chats")
    conn.commit()
    conn.close()
    logger.info("تم مسح جميع المحادثات من قاعدة البيانات")


def add_group(chat_id):
    """إضافة مجموعة إلى قاعدة البيانات"""
    # تحويل إلى رقم صحيح للتأكد من صحة المعرف
    try:
        chat_id = int(chat_id)
    except ValueError:
        logger.error(f"صيغة معرف المحادثة غير صالحة: {chat_id}. يجب أن تكون رقماً صحيحاً.")
        return False
    
    # إضافة المحادثة إلى قاعدة البيانات
    chat_title = f"مجموعة أخبار الكريبتو المخصصة"
    database.add_chat(chat_id, chat_title, "supergroup")
    logger.info(f"تمت إضافة مجموعة بمعرف {chat_id} إلى قاعدة البيانات")
    return True


def create_test_news():
    """إنشاء خبر اختباري للكريبتو"""
    return News(
        news_id=f"test-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        title="🚀 اختبار: أخبار بيتكوين لمجموعتك",
        content="هذا اختبار لبوت أخبار الكريبتو للتأكد من إمكانية الإرسال للمجموعة. إذا كنت ترى هذه الرسالة، فهذا يعني أن البوت يعمل بشكل صحيح ويمكنه إرسال الأخبار تلقائياً للمجموعة. هل تعلم أن البيتكوين قد يتجاوز الـ 100 ألف دولار هذا العام؟",
        source="اختبار بوت أخبار الكريبتو",
        url="https://example.com/crypto-news-test",
        tags=["اختبار", "بيتكوين", "أخبار_كريبتو"]
    )


async def send_test_message():
    """إرسال رسالة اختبار إلى جميع المحادثات المكونة"""
    # إنشاء خبر اختباري
    news = create_test_news()
    
    # بث الخبر إلى جميع المحادثات (والتي يجب أن تتضمن الآن مجموعتنا)
    success, errors = await broadcast_news(news)
    
    if success > 0:
        logger.info(f"✅ تم إرسال رسالة الاختبار بنجاح إلى {success} محادثة")
        return True
    else:
        logger.error(f"❌ فشل إرسال رسائل الاختبار. الأخطاء: {errors}")
        return False


async def main():
    """الوظيفة الرئيسية"""
    print("🔄 اختبار إرسال رسائل إلى مجموعة التلغرام")
    print("-" * 50)
    
    if len(sys.argv) < 2:
        # الحصول على المعلومات من المستخدم
        print("\n📝 أدخل معرف المجموعة:")
        print("(يمكنك الحصول على المعرف من مطور البوت، عادةً يكون بالصيغة -100xxxxxxxxxx)")
        chat_id = input("> ").strip()
    else:
        chat_id = sys.argv[1]
    
    # مسح قاعدة البيانات وإضافة المجموعة المستهدفة فقط
    reset_database()
    
    if not add_group(chat_id):
        print("❌ فشل إضافة المجموعة. تأكد من صحة معرف المحادثة.")
        return
    
    print(f"\n✅ تمت إضافة المجموعة بمعرف {chat_id} إلى قاعدة البيانات")
    
    # إرسال رسالة اختبار
    print("\n🔄 جاري إرسال رسالة اختبارية...")
    success = await send_test_message()
    
    if success:
        print("✅ تم إرسال الرسالة الاختبارية بنجاح!")
        print("تحقق من المجموعة للتأكد من وصول الرسالة")
    else:
        print("❌ فشل إرسال الرسالة الاختبارية. تحقق من سجلات الخادم لمزيد من التفاصيل.")
        print("تأكد من:")
        print("1. أن البوت عضو في المجموعة (أضف @Crypto_news_invtron_bot إلى المجموعة)")
        print("2. أن للبوت صلاحيات إرسال الرسائل")
        print("3. أن معرف المجموعة صحيح")


if __name__ == "__main__":
    asyncio.run(main())