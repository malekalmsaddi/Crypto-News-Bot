import logging
import asyncio
<<<<<<< HEAD
from telegram.ext import filters  # Correctly import filters
from telegram import Bot, Update
from telegram.constants import ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler
from telegram.ext.filters import MessageFilter
from telegram.error import TelegramError
from config import TELEGRAM_BOT_TOKEN
from config import WEBHOOK_URL
=======
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,  # Use ApplicationBuilder
    CommandHandler,
    MessageHandler,
    ChatMemberHandler,
    ContextTypes,
    filters
)
from telegram.error import TelegramError
from pycoingecko import CoinGeckoAPI

from config import TELEGRAM_BOT_TOKEN
>>>>>>> upstream/main
import database
from models import News

logger = logging.getLogger(__name__)
cg = CoinGeckoAPI()

# Initialize application globally
application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

<<<<<<< HEAD
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
    
=======
# Helper functions
def format_percentage(value: float) -> str:
    """Format percentage values with 2 decimal places."""
    return f"{value:.2f}"

async def get_bot_username() -> str:
    """Get the bot's Telegram username."""
    try:
        bot_user = await application.bot.get_me()
        return bot_user.username
    except Exception as e:
        logger.error(f"Failed to get bot username: {e}")
        return None

# Command handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    chat_id = update.effective_chat.id
    chat_title = update.effective_chat.title or f"Private chat with {update.effective_user.first_name}"
    chat_type = update.effective_chat.type

>>>>>>> upstream/main
    welcome_message = (
        "👋 أهلاً! مرحباً بك في بوت أخبار الكريبتو من إنفترون داو.\n\n"
        "سأقوم بنشر أخبار الكريبتو تلقائياً في هذه المحادثة.\n\n"
        "الأوامر المتاحة:\n"
        "/start - عرض هذه الرسالة\n"
        "/help - عرض معلومات المساعدة\n"
        "/about - معلومات عن البوت\n"
    )
<<<<<<< HEAD
    
    chat_type = update.effective_chat.type
=======

>>>>>>> upstream/main
    if chat_type == "private":
        welcome_message += (
            "\nأضفني إلى مجموعة لنشر الأخبار هناك!\n"
            "تأكد من منحي صلاحيات إرسال الرسائل."
        )
<<<<<<< HEAD
    
    # Store the chat in the database
    chat_title = update.effective_chat.title or f"Chat {chat_id}"  # Fallback title if none
    database.add_chat(chat_id, chat_title, chat_type)
    
    await update.message.reply_text(welcome_message)

logger.info("✅ Test message sent to chat")
async def help_command(update: Update, context: CallbackContext) -> None:
=======

    database.add_chat(chat_id, chat_title, chat_type)
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
>>>>>>> upstream/main
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
<<<<<<< HEAD
    
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

# bot.py - Corrected Functions

async def about_command(update: Update, context: CallbackContext) -> None:
=======
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
>>>>>>> upstream/main
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
<<<<<<< HEAD
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
=======
    await update.message.reply_text(about_text, parse_mode=ParseMode.MARKDOWN)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /status command."""
    await update.message.reply_text("✅ بوت أخبار الكريبتو يعمل بنجاح!")

async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /price command."""
    prices = await get_crypto_prices()
    if not prices:
        await update.message.reply_text("⚠️ عذراً، حدث خطأ أثناء جلب الأسعار. الرجاء المحاولة لاحقاً.")
        return

    price_message = "💰 *أسعار العملات الرقمية الآن:*\n\n"
    for coin, data in prices.items():
        change_emoji = "🟢" if data["change"] > 0 else "🔴"
        change_sign = "+" if data["change"] > 0 else ""
        price_message += f"{coin}: ${data['price']:,.2f} {change_emoji} {change_sign}{format_percentage(data['change'])}%\n"

    price_message += "\n⚠️ *ملاحظة*: هذه الأسعار تقريبية لأغراض العرض فقط."
    await update.message.reply_text(price_message, parse_mode=ParseMode.MARKDOWN)

async def get_crypto_prices():
    """Fetch cryptocurrency prices from CoinGecko."""
    try:
        coins = ["bitcoin", "ethereum", "solana", "binancecoin", "cardano"]
        prices = {}
        for coin in coins:
            data = cg.get_coin_market_chart_by_id(coin, vs_currency="usd", days="1")
            current_price = data["prices"][-1][1]
            previous_price = data["prices"][0][1]
            change = ((current_price - previous_price) / previous_price) * 100
            prices[coin.capitalize()] = {"price": current_price, "change": change}
        return prices
    except Exception as e:
        logger.error(f"Failed to fetch crypto prices: {e}")
        return None

# Group management handlers
async def handle_group_migration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle group migration to supergroup."""
>>>>>>> upstream/main
    if update.message and update.message.migrate_from_chat_id:
        old_chat_id = update.message.migrate_from_chat_id
        new_chat_id = update.effective_chat.id
        database.remove_chat(old_chat_id)
        database.add_chat(new_chat_id, update.effective_chat.title, update.effective_chat.type)
        logger.info(f"Chat migrated from {old_chat_id} to {new_chat_id}")

<<<<<<< HEAD
async def chat_member_updated(update: Update, context: CallbackContext) -> None:
    """Track when the bot is added to or removed from a chat."""
=======
async def chat_member_updated(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Track bot membership changes."""
>>>>>>> upstream/main
    result = update.my_chat_member
    if not result:
        return

    chat_id = result.chat.id
    chat_title = result.chat.title or f"Chat {chat_id}"
    chat_type = result.chat.type

    logger.info(f"Bot membership update in {chat_title} ({chat_id}): {result.old_chat_member.status} -> {result.new_chat_member.status}")

    if (result.old_chat_member.status in ['left', 'kicked'] and 
        result.new_chat_member.status in ['member', 'administrator']):
        database.add_chat(chat_id, chat_title, chat_type)
        logger.info(f"Bot was added to {chat_title} ({chat_id})")
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
                await context.bot.send_message(chat_id=chat_id, text=welcome_message)
            except Exception as e:
                logger.error(f"Failed to send welcome message to {chat_id}: {e}")

    elif (result.old_chat_member.status in ['member', 'administrator'] and 
          result.new_chat_member.status in ['left', 'kicked']):
        database.remove_chat(chat_id)
        logger.info(f"Bot was removed from {chat_title} ({chat_id})")

# Broadcast and scheduled tasks
async def broadcast_news(news: News) -> tuple[int, int]:
    """Broadcast news to all registered chats."""
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
            message = await application.bot.send_message(
                chat_id=chat_id,
                text=message_text,
                parse_mode=None,
                disable_web_page_preview=not bool(news.image_url)
            )
            database.log_message(news.news_id, chat_id, message.message_id)
            success_count += 1
<<<<<<< HEAD
            
            # Sleep briefly to avoid hitting rate limits
            await asyncio.sleep(0.5)
            
=======
            await asyncio.sleep(0.05)
>>>>>>> upstream/main
        except TelegramError as e:
            logger.error(f"Failed to send message to chat {chat_id}: {e}")
            error_count += 1
            if "bot was kicked" in str(e) or "chat not found" in str(e):
                database.remove_chat(chat_id)
                logger.info(f"Removed chat {chat_id} because bot was kicked or chat not found")

    logger.info(f"Broadcast completed. Success: {success_count}, Errors: {error_count}")
    return success_count, error_count

<<<<<<< HEAD
async def send_hourly_price_update(context: CallbackContext):
    """Send price updates to all chats."""
    from pycoingecko import CoinGeckoAPI
    cg = CoinGeckoAPI()
=======
async def send_hourly_price_update(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send scheduled price updates."""
    prices = await get_crypto_prices()
    if not prices:
        logger.error("Failed to fetch prices for hourly update.")
        return

    price_message = "💰 *تحديث الأسعار التلقائي كل ساعة:*\n\n"
    for coin, data in prices.items():
        change_emoji = "🟢" if data["change"] > 0 else "🔴"
        change_sign = "+" if data["change"] > 0 else ""
        price_message += f"{coin}: ${data['price']:,.2f} {change_emoji} {change_sign}{format_percentage(data['change'])}%\n"

    price_message += "\n⚠️ *ملاحظة*: هذه الأسعار تقريبية لأغراض العرض فقط."

>>>>>>> upstream/main
    chats = database.get_all_chats()
    for chat in chats:
        try:
            await context.bot.send_message(
                chat_id=chat['chat_id'],
                text=price_message,
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            logger.error(f"Failed to send price update to chat {chat['chat_id']}: {e}")
            # Remove the chat from the database if the bot is no longer a member
            if "Chat not found" in str(e) or "bot was kicked" in str(e):
                database.remove_chat(chat['chat_id'])
                logger.info(f"Removed chat {chat['chat_id']} from the database due to inaccessibility.")

async def market_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /market command."""
    try:
        global_data = cg.get_global()
        total_mcap = float(global_data['total_market_cap']['usd']) / 1e12
        total_volume = float(global_data['total_volume']['usd']) / 1e9
        btc_dominance = global_data['market_cap_percentage']['btc']
        eth_dominance = global_data['market_cap_percentage']['eth']

        market_info = (
            "📊 *حالة سوق الكريبتو*\n\n"
            f"القيمة السوقية الإجمالية: ${total_mcap:.2f} تريليون\n"
            f"حجم التداول (24 ساعة): ${total_volume:.1f} مليار\n"
            f"هيمنة بيتكوين: {btc_dominance:.1f}%\n"
            f"هيمنة إيثريوم: {eth_dominance:.1f}%\n\n"
            f"اتجاه السوق: {'📈 صاعد' if total_mcap > 2.5 else '📉 هابط'}\n\n"
            "⚠️ *ملاحظة*: البيانات من CoinGecko"
        )
        await update.message.reply_text(market_info, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.error(f"Failed to fetch market data: {e}")
        await update.message.reply_text("⚠️ عذراً، حدث خطأ أثناء جلب بيانات السوق. الرجاء المحاولة لاحقاً.")

<<<<<<< HEAD
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
=======
async def feedback_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /feedback command."""
    if context.args:
        feedback_message = ' '.join(context.args)
        user = update.effective_user
        logger.info(f"Feedback received from {user.id} ({user.username}): {feedback_message}")
        await update.message.reply_text("👍 شكراً لك على ملاحظاتك! تم استلامها وسيتم النظر فيها.", parse_mode=ParseMode.MARKDOWN)
    else:
        instructions = (
            "🔄 *إرسال ملاحظات أو اقتراحات*\n\n"
            "لإرسال ملاحظاتك، استخدم الأمر على الشكل التالي:\n\n"
            "`/feedback أحب الأخبار التي يوفرها البوت، لكن أتمنى أن تكون هناك تنبيهات للأسعار`\n\n"
            "نحن نقدر ملاحظاتك ونسعى لتحسين البوت باستمرار!"
        )
        await update.message.reply_text(instructions, parse_mode=ParseMode.MARKDOWN)


# Command handlers (keep all your existing command handlers here)

async def run_bot() -> None:
    """Configure and start the bot without closing the event loop."""
    # Register command handlers (same as your current setup)
    handlers = [
        CommandHandler("start", start_command),
        CommandHandler("help", help_command),
        CommandHandler("about", about_command),
        CommandHandler("status", status_command),
        CommandHandler("price", price_command),
        CommandHandler("market", market_command),
        CommandHandler("feedback", feedback_command),
        MessageHandler(filters.StatusUpdate.MIGRATE, handle_group_migration),
        ChatMemberHandler(chat_member_updated, ChatMemberHandler.MY_CHAT_MEMBER)
    ]
    for handler in handlers:
        application.add_handler(handler)

    # Schedule price updates
    application.job_queue.run_repeating(
        send_hourly_price_update,
        interval=3600,  # 1 hour
        first=10
    )

    # ✅ Start bot without managing the loop
    await application.initialize()
    await application.start()
>>>>>>> upstream/main
