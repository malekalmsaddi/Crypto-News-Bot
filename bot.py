import logging
import asyncio
from telegram import Bot, Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from telegram.error import TelegramError

from config import TELEGRAM_BOT_TOKEN, WEBHOOK_URL
import database
from models import News

logger = logging.getLogger(__name__)

# Initialize the bot instance
bot = Bot(token=TELEGRAM_BOT_TOKEN)

def start_command(update: Update, context: CallbackContext) -> None:
    """Handle the /start command."""
    chat_id = update.effective_chat.id
    chat_title = update.effective_chat.title or f"Private chat with {update.effective_user.first_name}"
    chat_type = update.effective_chat.type
    
    welcome_message = (
        "👋 أهلاً! مرحباً بك في بوت أخبار الكريبتو من إنفترون داو.\n\n"
        "سأقوم بنشر أخبار الكريبتو تلقائياً في هذه المحادثة.\n\n"
        "الأوامر المتاحة:\n"
        "/start - عرض هذه الرسالة\n"
        "/help - عرض معلومات المساعدة\n"
        "/about - معلومات عن البوت\n"
    )
    
    if chat_type == "private":
        welcome_message += (
            "\nأضفني إلى مجموعة لنشر الأخبار هناك!\n"
            "تأكد من منحي صلاحيات إرسال الرسائل."
        )
    
    # Store the chat in the database
    database.add_chat(chat_id, chat_title, chat_type)
    
    update.message.reply_text(welcome_message)

def help_command(update: Update, context: CallbackContext) -> None:
    """Handle the /help command."""
    help_text = (
        "📢 *مساعدة بوت أخبار الكريبتو*\n\n"
        "يقوم هذا البوت باستقبال أخبار الكريبتو عبر الويب هوك وإعادة نشرها تلقائياً في جميع المجموعات المضاف إليها.\n\n"
        "*الأوامر:*\n"
        "/start - بدء استخدام البوت\n"
        "/help - عرض رسالة المساعدة هذه\n"
        "/about - معلومات عن البوت\n"
        "/status - التحقق من عمل البوت\n"
        "/price - عرض أسعار العملات الرقمية\n\n"
        "💡 *نصائح:*\n"
        "• أضف البوت إلى مجموعتك لتلقي أخبار الكريبتو تلقائياً\n"
        "• استخدم أمر /price في أي وقت لمعرفة أحدث أسعار العملات الرقمية\n"
    )
    
    update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

def about_command(update: Update, context: CallbackContext) -> None:
    """Handle the /about command."""
    about_text = (
        "📰 *بوت أخبار الكريبتو من إنفترون داو*\n\n"
        "تم تصميم هذا البوت لنشر أخبار الكريبتو تلقائياً في مجموعات تيليجرام.\n\n"
        "يستقبل البوت الأخبار عبر الويب هوك ويعيد نشرها في جميع المجموعات المضاف إليها.\n\n"
        "*المميزات:*\n"
        "• نشر أخبار الكريبتو تلقائياً\n"
        "• عرض أسعار العملات الرقمية\n"
        "• تتبع المجموعات\n"
        "• تنسيق منشورات الأخبار بشكل جميل\n"
        "• دعم اللغة العربية بالكامل\n\n"
        "*العملات المدعومة:*\n"
        "• بيتكوين (BTC)\n"
        "• إيثريوم (ETH)\n"
        "• سولانا (SOL)\n"
        "• بينانس كوين (BNB)\n"
        "• كاردانو (ADA)\n"
        "وغيرها الكثير...\n\n"
        "📱 هذا البوت مقدم من: إنفترون داو"
    )
    
    update.message.reply_text(about_text, parse_mode=ParseMode.MARKDOWN)

def status_command(update: Update, context: CallbackContext) -> None:
    """Handle the /status command to check if the bot is working."""
    update.message.reply_text("✅ بوت أخبار الكريبتو يعمل بنجاح!")

def price_command(update: Update, context: CallbackContext) -> None:
    """Handle the /price command to show cryptocurrency prices."""
    # In a real implementation, this would fetch real price data from an API
    # For now, we're using sample data for demonstration
    prices = {
        "BTC": {"price": 74850.25, "change": 2.5},
        "ETH": {"price": 3975.12, "change": 1.8},
        "SOL": {"price": 189.45, "change": 3.2},
        "BNB": {"price": 628.74, "change": -0.7},
        "ADA": {"price": 0.58, "change": 1.2}
    }
    
    # Format the message in Arabic
    price_message = "💰 *أسعار العملات الرقمية الآن:*\n\n"
    
    for coin, data in prices.items():
        change_emoji = "🟢" if data["change"] > 0 else "🔴"
        change_sign = "+" if data["change"] > 0 else ""
        price_message += f"{coin}: ${data['price']:,.2f} {change_emoji} {change_sign}{data['change']}%\n"
    
    price_message += "\n⚠️ *ملاحظة*: هذه الأسعار تقريبية لأغراض العرض فقط."
    
    update.message.reply_text(price_message, parse_mode=ParseMode.MARKDOWN)


def market_command(update: Update, context: CallbackContext) -> None:
    """Handle the /market command to show cryptocurrency market information."""
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


def feedback_command(update: Update, context: CallbackContext) -> None:
    """Handle the /feedback command for receiving user feedback."""
    # Check if user provided feedback message
    if context.args:
        # Join all arguments into a feedback message
        feedback_message = ' '.join(context.args)
        
        # Log the feedback
        user = update.effective_user
        chat = update.effective_chat
        logger.info(f"Feedback received from {user.id} ({user.username}): {feedback_message}")
        
        # Thank the user
        update.message.reply_text(
            "👍 شكراً لك على ملاحظاتك! تم استلامها وسيتم النظر فيها.",
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        # No feedback message provided, send instructions
        instructions = (
            "🔄 *إرسال ملاحظات أو اقتراحات*\n\n"
            "لإرسال ملاحظاتك، استخدم الأمر على الشكل التالي:\n\n"
            "`/feedback أحب الأخبار التي يوفرها البوت، لكن أتمنى أن تكون هناك تنبيهات للأسعار`\n\n"
            "نحن نقدر ملاحظاتك ونسعى لتحسين البوت باستمرار!"
        )
        update.message.reply_text(instructions, parse_mode=ParseMode.MARKDOWN)

def handle_group_migration(update: Update, context: CallbackContext) -> None:
    """Handle migration to a supergroup."""
    if update.message and update.message.migrate_from_chat_id:
        old_chat_id = update.message.migrate_from_chat_id
        new_chat_id = update.effective_chat.id
        
        # Remove old chat and add the new one
        database.remove_chat(old_chat_id)
        database.add_chat(new_chat_id, update.effective_chat.title, update.effective_chat.type)
        
        logger.info(f"Chat migrated from {old_chat_id} to {new_chat_id}")

def chat_member_updated(update: Update, context: CallbackContext) -> None:
    """Track when the bot is added to or removed from a chat."""
    result = update.my_chat_member
    
    if not result:
        return
    
    chat_id = result.chat.id
    chat_title = result.chat.title or f"Chat {chat_id}"  # Fallback title if none
    chat_type = result.chat.type
    
    # Log the update details for debugging
    logger.info(f"Bot membership update in {chat_title} ({chat_id}): "
                f"{result.old_chat_member.status} -> {result.new_chat_member.status}")
    
    # Bot was added to a group
    if (result.old_chat_member.status in ['left', 'kicked'] and 
            result.new_chat_member.status in ['member', 'administrator']):
        # Add chat to database
        database.add_chat(chat_id, chat_title, chat_type)
        logger.info(f"Bot was added to {chat_title} ({chat_id})")
        
        # Send welcome message if it's a group or supergroup
        if chat_type in ['group', 'supergroup']:
            try:
                welcome_message = (
                    "👋 أهلاً! تم إضافة بوت أخبار الكريبتو إلى هذه المجموعة.\n\n"
                    "سأقوم بنشر أخبار الكريبتو تلقائياً هنا.\n\n"
                    "الأوامر المتاحة:\n"
                    "/help - عرض معلومات المساعدة\n"
                    "/about - معلومات عن البوت\n"
                    "/price - عرض أسعار العملات الرقمية\n"
                )
                context.bot.send_message(chat_id=chat_id, text=welcome_message)
            except Exception as e:
                logger.error(f"Failed to send welcome message to {chat_id}: {e}")
        
    # Bot was removed from a group
    elif (result.old_chat_member.status in ['member', 'administrator'] and 
            result.new_chat_member.status in ['left', 'kicked']):
        database.remove_chat(chat_id)
        logger.info(f"Bot was removed from {chat_title} ({chat_id})")
        
    # Bot permissions were changed but still in the group
    elif (result.old_chat_member.status != result.new_chat_member.status and
          result.new_chat_member.status in ['member', 'administrator']):
        # Update the chat in database if there are permission changes
        database.add_chat(chat_id, chat_title, chat_type)
        logger.info(f"Bot status updated in {chat_title} ({chat_id}) to {result.new_chat_member.status}")

async def broadcast_news(news: News):
    """Broadcast news to all chats where the bot is a member."""
    chats = database.get_all_chats()
    
    if not chats:
        logger.warning("No chats to broadcast to.")
        return 0, 0
    
    message_text = news.format_telegram_message()
    success_count = 0
    error_count = 0
    
    for chat in chats:
        chat_id = chat['chat_id']
        
        try:
            # Send message with no markdown formatting to avoid parsing errors
            message = await bot.send_message(
                chat_id=chat_id,
                text=message_text,
                parse_mode=None,  # No Markdown parsing
                disable_web_page_preview=False if news.image_url else True
            )
            
            # Log sent message
            database.log_message(news.news_id, chat_id, message.message_id)
            success_count += 1
            
            # Sleep briefly to avoid hitting rate limits
            await asyncio.sleep(0.05)
            
        except TelegramError as e:
            logger.error(f"Failed to send message to chat {chat_id}: {e}")
            error_count += 1
            
            # If bot was kicked, remove the chat
            if "bot was kicked" in str(e) or "chat not found" in str(e):
                database.remove_chat(chat_id)
                logger.info(f"Removed chat {chat_id} because bot was kicked or chat not found")
    
    logger.info(f"Broadcast completed. Success: {success_count}, Errors: {error_count}")
    return success_count, error_count

def setup_bot():
    """Set up the bot with handlers and webhook."""
    # Create an updater instance
    updater = Updater(token=TELEGRAM_BOT_TOKEN)
    dispatcher = updater.dispatcher
    
    # Add handlers
    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("about", about_command))
    dispatcher.add_handler(CommandHandler("status", status_command))
    dispatcher.add_handler(CommandHandler("price", price_command))
    dispatcher.add_handler(CommandHandler("market", market_command))
    dispatcher.add_handler(CommandHandler("feedback", feedback_command))
    
    # Track group migrations
    dispatcher.add_handler(MessageHandler(Filters.status_update.migrate, handle_group_migration))
    
    # Track bot membership changes (when added to or removed from a group)
    from telegram.ext import ChatMemberHandler
    dispatcher.add_handler(ChatMemberHandler(chat_member_updated, ChatMemberHandler.MY_CHAT_MEMBER))
    
    if WEBHOOK_URL:
        # Set webhook
        updater.bot.set_webhook(url=f"{WEBHOOK_URL}/telegram-webhook")
        logger.info(f"Webhook set to {WEBHOOK_URL}/telegram-webhook")
        return updater
    else:
        # Start polling mode if webhook URL isn't provided
        updater.start_polling()
        logger.warning("Starting in polling mode as no webhook URL was provided")
        return updater

def get_bot_username():
    """Get the bot's username (synchronously)."""
    try:
        bot_user = bot.get_me()
        return bot_user.username
    except Exception as e:
        logger.error(f"Failed to get bot username: {e}")
        return None
