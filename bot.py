import logging
import asyncio
from telegram.ext import filters  # Correctly import filters
from telegram import Bot, Update
from telegram.constants import ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler
from telegram.ext.filters import MessageFilter
from telegram.error import TelegramError
from config import TELEGRAM_BOT_TOKEN
from config import WEBHOOK_URL
import database
from models import News

logger = logging.getLogger(__name__)

# Initialize the bot instance
bot = Bot(token=TELEGRAM_BOT_TOKEN)

async def start_command(update: Update, context: CallbackContext) -> None:
    try:
        chat_id = update.effective_chat.id
        logger.info(f"Received /start from chat {chat_id}")

        welcome_message = (
            "👋 أهلاً! مرحباً بك في بوت أخبار الكريبتو من إنفترون داو.\n\n"
            "سأقوم بنشر أخبار الكريبتو تلقائياً في هذه المحادثة.\n\n"
            "الأوامر المتاحة:\n"
            "/start - عرض هذه الرسالة\n"
            "/help - عرض معلومات المساعدة\n"
            "/about - معلومات عن البوت\n"
        )

        # ✅ Force completion of send_message BEFORE moving on
        sent_message = await context.bot.send_message(chat_id=chat_id, text=welcome_message)
        logger.info(f"✅ Message sent: {sent_message.message_id}")

        # Optional: Add a small delay to ensure no connection drop
        await asyncio.sleep(1)

    except Exception as e:
        logger.error(f"Error in /start command: {e}", exc_info=True)
    
    welcome_message = (
        "👋 أهلاً! مرحباً بك في بوت أخبار الكريبتو من إنفترون داو.\n\n"
        "سأقوم بنشر أخبار الكريبتو تلقائياً في هذه المحادثة.\n\n"
        "الأوامر المتاحة:\n"
        "/start - عرض هذه الرسالة\n"
        "/help - عرض معلومات المساعدة\n"
        "/about - معلومات عن البوت\n"
    )
    
    chat_type = update.effective_chat.type
    if chat_type == "private":
        welcome_message += (
            "\nأضفني إلى مجموعة لنشر الأخبار هناك!\n"
            "تأكد من منحي صلاحيات إرسال الرسائل."
        )
    
    # Store the chat in the database
    chat_title = update.effective_chat.title or f"Chat {chat_id}"  # Fallback title if none
    database.add_chat(chat_id, chat_title, chat_type)
    
    await update.message.reply_text(welcome_message)

logger.info("✅ Test message sent to chat")
async def help_command(update: Update, context: CallbackContext) -> None:
    """Handle the /help command."""
    help_text = (
        "📢 *مساعدة بوت أخبار الكريبتو - مقدم من إنفترون داو*\n\n"
        "هذا البوت مصمم لنشر أخبار العملات الرقمية تلقائياً داخل مجموعات تيليجرام، مع تحديث الأسعار لحظة بلحظة.\n\n"
        "الأوامر المتاحة:\n"
        "/start - بدء استخدام البوت\n"
        "/help - عرض رسالة المساعدة\n"
        "/about - معلومات عن البوت\n"
        "/status - التحقق من حالة البوت\n"
        "/price - عرض أحدث أسعار العملات الرقمية\n\n"
        "💡 *نصائح الاستخدام:*\n"
        "• أضف البوت إلى مجموعتك ليصلك كل جديد في عالم الكريبتو\n"
        "• استخدم /price في أي وقت لمتابعة أسعار العملات الرقمية مباشرة\n\n"
        "🔗 *انضم إلى مجتمعنا العربي:*\n"
        "https://t.me/+CMoM9cPlV5syNGE0\n"
        "إنفترون داو - نبحث عن الجواهر ونموّلها"
    )
    
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

# bot.py - Corrected Functions

async def about_command(update: Update, context: CallbackContext) -> None:
    """Handle the /about command."""
    about_text = (
        "💎 *بوت أخبار الكريبتو - من تطوير وإنفاذ إنفترون داو* 💎\n\n"
        "🔹 منصة ذكية مدعومة من إنفترون داو – رائدة الاستثمار والتمويل اللامركزي عبر البلوك تشين 🔹\n\n"
        "تم تصميم هذا البوت خصيصاً ليكون امتداداً لرؤية إنفترون داو في تمكين المجتمعات الرقمية من الوصول إلى أحدث أخبار العملات الرقمية والأسواق المالية بكل سهولة واحترافية داخل مجموعات تيليجرام.\n\n"
        "✨ *مميزات البوت:*\n"
        "✅ نشر أخبار العملات الرقمية بشكل تلقائي من مصادر موثوقة\n"
        "✅ عرض أسعار العملات الرقمية محدثة لحظة بلحظة\n"
        "✅ متابعة أداء وتفاعل المجموعات بشكل ذكي\n"
        "✅ تنسيق احترافي وجذاب للمنشورات\n"
        "✅ دعم كامل للغة العربية\n\n"
        "🚀 *العملات المدعومة (والمزيد قادم):*\n"
        "• بيتكوين (BTC)\n"
        "• إيثريوم (ETH)\n"
        "• سولانا (SOL)\n"
        "• بينانس كوين (BNB)\n"
        "• كاردانو (ADA)\n"
        "... وأكثر من ذلك\n\n"
        "🌐 *لماذا تختار بوت إنفترون داو؟*\n"
        "لأن هذا البوت ليس مجرد أداة للنشر، بل هو جزء من منظومة إنفترون داو التي تقود مستقبل الاستثمار والتمويل اللامركزي عبر تقنيات البلوك تشين. هدفنا تعزيز الشفافية، تمكين المجتمعات، ونشر المعرفة المالية الدقيقة والمحدثة.\n\n"
        "📱 هذا البوت مقدم حصرياً من: *إنفترون داو* \"نبحث عن الجواهر... ونموّلها\""
    )
    await update.message.reply_text(about_text, parse_mode=ParseMode.MARKDOWN)  # Added await

async def status_command(update: Update, context: CallbackContext) -> None:
    """Handle the /status command to check if the bot is working."""
    await update.message.reply_text("✅ بوت أخبار الكريبتو يعمل بنجاح!")  # Added await

async def price_command(update: Update, context: CallbackContext) -> None:
    """Handle the /price command to show cryptocurrency prices."""
    try:
        # Fetch the latest prices from the database
        prices = database.get_market_prices()
        if not prices:
            await update.message.reply_text("⚠️ عذراً، لا توجد بيانات أسعار متاحة حالياً.")
            return

        # Build the price message
        price_message = "💰 *أسعار العملات الرقمية الآن:*\n\n"
        for coin, data in prices.items():
            change_emoji = "🟢" if data["change"] > 0 else "🔴"
            change_sign = "+" if data["change"] > 0 else ""
            price_message += (
                f"🔹 *{coin}*\n"
                f"   السعر: `${data['price']:,.2f}`\n"
                f"   التغيير (24 ساعة): {change_emoji} {change_sign}{data['change']:.2f}%\n\n"
            )

        price_message += "⚠️ *ملاحظة*: هذه الأسعار تقريبية لأغراض العرض فقط."

        # Send the price message
        await update.message.reply_text(price_message, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logger.error(f"Failed to fetch prices: {e}")
        # Ensure only one response is sent
        if not asyncio.get_event_loop().is_closed():
            await update.message.reply_text("⚠️ عذراً، حدث خطأ أثناء جلب الأسعار.")
            
async def market_command(update: Update, context: CallbackContext) -> None:
    """Handle the /market command to show cryptocurrency market information."""
    try:
        # Fetch the latest market summary from the database
        market_data = database.get_market_summary()
        if not market_data:
            await update.message.reply_text("⚠️ عذراً، لا توجد بيانات سوق متاحة حالياً.")
            return

        # Extract and format market data
        total_market_cap = market_data.get('total_market_cap', 0) / 1e12  # Convert to trillions
        total_volume = market_data.get('total_volume', 0) / 1e9            # Convert to billions
        btc_dominance = market_data.get('btc_dominance', 0)
        eth_dominance = market_data.get('eth_dominance', 0)

        # Determine market sentiment
        sentiment = '📈 *صاعد*' if total_market_cap > 2.5 else '📉 *هابط*'

        # Build the market information message
        market_info = (
            "📊 *حالة سوق الكريبتو*\n\n"
            f"💰 *القيمة السوقية الإجمالية:*\n   `${total_market_cap:.2f} تريليون`\n\n"
            f"📈 *حجم التداول (24 ساعة):*\n   `${total_volume:.1f} مليار`\n\n"
            f"🔶 *هيمنة بيتكوين:*\n   `{btc_dominance:.1f}%`\n\n"
            f"🔷 *هيمنة إيثريوم:*\n   `{eth_dominance:.1f}%`\n\n"
            f"📝 *اتجاه السوق:*\n   {sentiment}\n\n"
            "⚠️ *ملاحظة*: البيانات محدثة من قاعدة البيانات ويتم تحديثها كل دقيقة."
        )

        # Send the market information message
        await update.message.reply_text(market_info, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logger.error(f"Failed to fetch market summary: {e}")
        # Ensure only one response is sent
        if not asyncio.get_event_loop().is_closed():
            await update.message.reply_text("⚠️ عذراً، حدث خطأ أثناء جلب بيانات السوق.")

async def feedback_command(update: Update, context: CallbackContext) -> None:
    """Handle the /feedback command for receiving user feedback."""
    if context.args:
        feedback_message = ' '.join(context.args)
        user = update.effective_user
        chat = update.effective_chat
        logger.info(f"Feedback received from {user.id} ({user.username}): {feedback_message}")
        await update.message.reply_text("👍 شكراً لك على ملاحظاتك! تم استلامها وسيتم النظر فيها.")  # Added await
    else:
        instructions = (
            "🔄 *إرسال ملاحظات أو اقتراحات*\n\n"
            "لإرسال ملاحظاتك، استخدم الأمر على الشكل التالي:\n\n"
            "`/feedback أحب الأخبار التي يوفرها البوت، لكن أتمنى أن تكون هناك تنبيهات للأسعار`\n\n"
            "نحن نقدر ملاحظاتك ونسعى لتحسين البوت باستمرار!"
        )
        await update.message.reply_text(instructions, parse_mode=ParseMode.MARKDOWN)  # Added await

async def handle_group_migration(update: Update, context: CallbackContext) -> None:
    """Handle migration to a supergroup."""
    if update.message and update.message.migrate_from_chat_id:
        old_chat_id = update.message.migrate_from_chat_id
        new_chat_id = update.effective_chat.id
        
        # Remove old chat and add the new one
        database.remove_chat(old_chat_id)
        database.add_chat(new_chat_id, update.effective_chat.title, update.effective_chat.type)
        
        logger.info(f"Chat migrated from {old_chat_id} to {new_chat_id}")

async def chat_member_updated(update: Update, context: CallbackContext) -> None:
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
            await asyncio.sleep(0.5)
            
        except TelegramError as e:
            logger.error(f"Failed to send message to chat {chat_id}: {e}")
            error_count += 1
            
            # If bot was kicked, remove the chat
            if "bot was kicked" in str(e) or "chat not found" in str(e):
                database.remove_chat(chat_id)
                logger.info(f"Removed chat {chat_id} because bot was kicked or chat not found")
    
    logger.info(f"Broadcast completed. Success: {success_count}, Errors: {error_count}")
    return success_count, error_count

async def send_hourly_price_update(context: CallbackContext):
    """Send price updates to all chats."""
    from pycoingecko import CoinGeckoAPI
    cg = CoinGeckoAPI()
    chats = database.get_all_chats()
    
    try:
        # Fetch prices once for all chats
        prices_data = cg.get_price(
            ids=['bitcoin', 'ethereum', 'solana', 'binancecoin', 'cardano'],
            vs_currencies='usd',
            include_24hr_change=True
        )
        
        prices = {
            "BTC": {"price": prices_data['bitcoin']['usd'], "change": prices_data['bitcoin']['usd_24h_change']},
            "ETH": {"price": prices_data['ethereum']['usd'], "change": prices_data['ethereum']['usd_24h_change']},
            "SOL": {"price": prices_data['solana']['usd'], "change": prices_data['solana']['usd_24h_change']},
            "BNB": {"price": prices_data['binancecoin']['usd'], "change": prices_data['binancecoin']['usd_24h_change']},
            "ADA": {"price": prices_data['cardano']['usd'], "change": prices_data['cardano']['usd_24h_change']}
        }
        
        # Format message
        price_message = "💰 *تحديث الأسعار التلقائي كل ساعة:*\n\n"
        for coin, data in prices.items():
            change_emoji = "🟢" if data["change"] > 0 else "🔴"
            change_sign = "+" if data["change"] > 0 else ""
            price_message += f"{coin}: ${data['price']:,.2f} {change_emoji} {change_sign}{data['change']:.2f}%\n"
        
        price_message += "\n⚠️ *ملاحظة*: هذه الأسعار تقريبية لأغراض العرض فقط."
        
        # Send to all chats
        for chat in chats:
            try:
                context.bot.send_message(
                    chat_id=chat['chat_id'],
                    text=price_message,
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                logger.error(f"Failed to send price update to chat {chat['chat_id']}: {e}")
                
    except Exception as e:
        logger.error(f"Failed to fetch prices for hourly update: {e}")

from telegram.ext import Application, CommandHandler, MessageHandler

async def setup_bot():
    """Set up the bot with handlers and webhook."""
    global application  # Make the application instance globally accessible
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("price", price_command))
    application.add_handler(CommandHandler("market", market_command))
    application.add_handler(CommandHandler("feedback", feedback_command))
    async def handle_text(update: Update, context: CallbackContext) -> None:
        """Handle generic text messages."""
        await update.message.reply_text("🚀 شكراً لرسالتك! إذا كنت بحاجة إلى مساعدة، استخدم /help.")

    # Add a generic message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Schedule hourly price updates
    job_queue = application.job_queue
    job_queue.run_repeating(send_hourly_price_update, interval=3600, first=0)

# Track group migrations
    application.add_handler(MessageHandler(filters.StatusUpdate.MIGRATE, handle_group_migration))

# Track bot membership changes (when added to or removed from a group)
    from telegram.ext import ChatMemberHandler
    application.add_handler(ChatMemberHandler(chat_member_updated, ChatMemberHandler.MY_CHAT_MEMBER))

    async def get_application() -> Application:
        """Get the initialized application instance."""
    return application

async def get_bot_username():
    """Get the bot's username."""
    try:
        bot_info = await bot.get_me()
        return bot_info.username
    except Exception as e:
        logger.error(f"Error fetching bot username: {e}")
        return None
    return application

async def get_bot_username():
    """Get the bot's username."""
    try:
        bot_info = await bot.get_me()
        return bot_info.username
    except Exception as e:
        logging.error(f"Failed to get bot username: {e}")
        return None
