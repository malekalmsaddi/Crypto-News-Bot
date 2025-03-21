#!/usr/bin/env python3
"""
Register commands with BotFather

This script generates the command list in the format needed by BotFather.
It doesn't actually register the commands - you'll need to manually send
this list to @BotFather using the /setcommands command.

Usage:
python register_commands.py
"""

def generate_bot_commands():
    """Generate command list for BotFather in the required format"""
    
    # Define commands with descriptions in Arabic
    commands = [
        ("start", "بدء استخدام البوت"),
        ("help", "عرض معلومات المساعدة"),
        ("about", "معلومات عن البوت"),
        ("status", "التحقق من عمل البوت"),
        ("price", "عرض أسعار العملات الرقمية"),
        ("market", "عرض معلومات سوق الكريبتو"),
        ("feedback", "إرسال ملاحظات أو اقتراحات")
    ]
    
    # Format according to BotFather requirements
    formatted_commands = "\n".join([f"{cmd} - {desc}" for cmd, desc in commands])
    
    return formatted_commands

if __name__ == "__main__":
    print("📝 قائمة الأوامر لتسجيلها مع BotFather:\n")
    print("====================")
    print(generate_bot_commands())
    print("====================\n")
    
    print("تعليمات التسجيل:")
    print("1. افتح محادثة مع @BotFather على تلغرام")
    print("2. أرسل الأمر /setcommands")
    print("3. اختر البوت الخاص بك: @Crypto_news_invtron_bot")
    print("4. انسخ والصق قائمة الأوامر أعلاه وأرسلها")
    print("\nبعد الانتهاء، ستظهر الأوامر كاقتراحات للمستخدمين عند الكتابة '/'")