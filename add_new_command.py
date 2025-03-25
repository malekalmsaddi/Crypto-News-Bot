#!/usr/bin/env python3
"""
نموذج لإضافة أوامر جديدة للبوت

يوضح هذا الملف كيفية إضافة أمر جديد للبوت. بعد تنفيذ التغييرات المطلوبة، ستحتاج أيضًا
لتسجيل الأمر مع BotFather باستخدام /setcommands.

خطوات إضافة أمر جديد:
1. إنشاء وظيفة لمعالجة الأمر (مثل market_command أدناه)
2. إضافة وظيفة معالجة الأمر إلى dispatcher.add_handler في وظيفة setup_bot
3. تحديث register_commands.py لإضافة الأمر الجديد إلى قائمة الأوامر
4. تسجيل الأوامر المحدثة مع BotFather

مثال توضيحي:
"""

import logging
from telegram import Bot, Update
from telegram.constants import ParseMode
from telegram.ext import CommandHandler, CallbackContext

logger = logging.getLogger(__name__)

# مثال على أمر جديد
def market_command(update: Update, context: CallbackContext) -> None:
    """معالجة أمر /market لعرض معلومات السوق."""
    market_info = (
        "📊 *حالة سوق الكريبتو*\n\n"
        "القيمة السوقية الإجمالية: $2.54 تريليون\n"
        "حجم التداول (24 ساعة): $98.7 مليار\n"
        "هيمنة بيتكوين: 47.8%\n"
        "هيمنة إيثريوم: 18.2%\n\n"
        "مؤشر الخوف والجشع: 72 (جشع)\n"
        "اتجاه السوق: صاعد 📈\n\n"
        "⚠️ *ملاحظة*: هذه المعلومات تقريبية لأغراض العرض فقط."
    )
    
    update.message.reply_text(market_info, parse_mode=ParseMode.MARKDOWN)

# كيفية تسجيل الأمر الجديد في setup_bot في bot.py
"""
def setup_bot():
    # Create an updater instance
    updater = Updater(token=TELEGRAM_BOT_TOKEN)
    dispatcher = updater.dispatcher
    
    # Add handlers
    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("about", about_command))
    dispatcher.add_handler(CommandHandler("status", status_command))
    dispatcher.add_handler(CommandHandler("price", price_command))
    
    # إضافة الأمر الجديد هنا
    dispatcher.add_handler(CommandHandler("market", market_command))
    
    # ... باقي الكود ...
"""

# كيفية تحديث قائمة الأوامر في register_commands.py
"""
def generate_bot_commands():
    commands = [
        ("start", "بدء استخدام البوت"),
        ("help", "عرض معلومات المساعدة"),
        ("about", "معلومات عن البوت"),
        ("status", "التحقق من عمل البوت"),
        ("price", "عرض أسعار العملات الرقمية"),
        ("market", "عرض معلومات سوق الكريبتو")  # الأمر الجديد
    ]
    
    formatted_commands = "\n".join([f"{cmd} - {desc}" for cmd, desc in commands])
    return formatted_commands
"""

if __name__ == "__main__":
    print("هذا مجرد نموذج لإضافة أوامر جديدة.")
    print("اتبع التعليمات في التعليقات لإضافة أمر جديد للبوت الخاص بك.")
    print("\nلتطبيق أمر جديد، ستحتاج إلى:")
    print("1. نسخ وظيفة الأمر (مثل market_command) إلى bot.py")
    print("2. تسجيل الأمر في setup_bot داخل bot.py")
    print("3. تحديث قائمة الأوامر في register_commands.py")
    print("4. تشغيل register_commands.py للحصول على قائمة محدثة")
    print("5. تسجيل القائمة المحدثة مع BotFather باستخدام /setcommands")