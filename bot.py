import logging
import asyncio
import telegram
from telegram import Update, Bot
from telegram.constants import ParseMode
from telegram.ext import Application, ContextTypes, CommandHandler, MessageHandler, filters, ChatMemberHandler
from telegram.error import TelegramError
from config import TELEGRAM_BOT_TOKEN, WEBHOOK_URL
import database
from models import News
import weakref
from state import shutting_down, shutdown_lock

BOT_LOOP = None

_app_states = weakref.WeakKeyDictionary()
logger = logging.getLogger(__name__)
application = None
bot = Bot(token=TELEGRAM_BOT_TOKEN)
initializing = False
init_lock = asyncio.Lock()
OFFICIAL_SITE = "https://invtron.com"
COMMUNITY_LINK = "https://t.me/+obSAMV8Mt8kzYTY0"

async def get_bot_username():
    """Get the bot's username."""
    try:
        bot_info = await bot.get_me()
        return bot_info.username
    except Exception as e:
        logger.error(f"Error fetching bot username: {e}")
        return None

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_message = ""  # ✅ ضمان وجود المتغير لتجنب UnboundLocalError
    try:
        chat_id = update.effective_chat.id
        chat_type = update.effective_chat.type
        logger.info(f"Received /start from chat {chat_id}")

        if chat_type == "private":
            message = (
                "👋 مرحباً بك في <b>بوت أخبار إنفترون داو الرسمي</b> 🚀\n\n"
                "📰 نقدم لك أحدث الأخبار والتحليلات في عالم العملات الرقمية.\n\n"
                "📌 <b>الأوامر المتاحة:</b>\n"
                "/start - بدء الاستخدام\n/help - المساعدة\n/about - من نحن؟\n"
                "/price - أسعار العملات\n/market - ملخص السوق\n/feedback - أرسل اقتراحاتك\n\n"
                f"🌐 اكتشف المزيد: <a href='{OFFICIAL_SITE}'>إنفترون داو</a>\n"
                f"📣 انضم إلى مجتمعنا: <a href=\"{COMMUNITY_LINK}\">رابط تلجرام</a>\n\n"
                "💎 <b>إنفترون داو</b> — \"نبحث عن الجواهر... ونموّلها\""
            )
        else:
            message = (
                "👥 أهلاً بكم! تم تفعيل <b>بوت أخبار إنفترون داو</b> في هذه المجموعة ✅\n\n"
                "📢 سأقوم بنشر الأخبار العاجلة وتحليلات السوق هنا.\n\n"
                "🔧 <b>الأوامر المتاحة:</b>\n"
                "/help - المساعدة\n/about - عن إنفترون داو\n/price - أسعار العملات\n/market - ملخص السوق\n\n"
                f"🌐 تعرف على مشروعنا: <a href=\"{OFFICIAL_SITE}\">إنفترون داو</a>\n"
                f"📣 قناة المجتمع: <a href=\"{COMMUNITY_LINK}\">انضم الآن</a>"
            )

        # ✅ إرسال الرسالة الأساسية
        await update.message.reply_text(message, parse_mode=ParseMode.HTML)

        # ✅ رسالة ترحيب إضافية خاصة
        welcome_message = (
            "👋 أهلاً! مرحباً بك في بوت أخبار الكريبتو من إنفترون داو.\n\n"
            "سأقوم بنشر أخبار الكريبتو تلقائياً هنا.\n\n"
            "📌 الأوامر المتاحة:\n"
            "/start - عرض هذه الرسالة\n/help - معلومات المساعدة\n/about - معلومات عن البوت\n"
        )
        sent_message = await context.bot.send_message(chat_id=chat_id, text=welcome_message)
        logger.info(f"✅ Message sent: {sent_message.message_id}")

        await asyncio.sleep(1)

    except Exception as e:
        logger.error(f"Error in /start command: {e}", exc_info=True)

    # ✅ تسجيل المجموعة أو الخاص في قاعدة البيانات
    chat_title = update.effective_chat.title or f"Chat {chat_id}"
    database.add_chat(chat_id, chat_title, chat_type)

    # ✅ إرسال رسالة الترحيب النهائية بشكل آمن
    if welcome_message:
        await update.message.reply_text(welcome_message, parse_mode=ParseMode.HTML)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global shutting_down  # Add this
    async with shutdown_lock:
        if shutting_down:
            logging.warning("Blocked help command during shutdown")
            return
    try:
        message = (
            f"💼 <b>مركز المساعدة - إنفترون داو</b> 💼\n\n"
            f"🤖 هذا البوت مصمم ليمنحك تجربة احترافية لأحدث أخبار وتحليلات سوق الكريبتو.\n\n"
            f"🔧 <b>الأوامر المتاحة:</b>\n"
            f"/start - بدء الاستخدام\n"
            f"/help - المساعدة\n"
            f"/about - من نحن؟\n"
            f"/price - أسعار العملات\n"
            f"/market - ملخص السوق\n"
            f"/feedback - أرسل ملاحظاتك\n\n"
            f"🌐 <a href=\"{OFFICIAL_SITE}\">موقعنا الرسمي</a>\n"
            f"📣 <a href=\"{COMMUNITY_LINK}\">مجتمع إنفترون داو</a>"
        )
        await update.message.reply_text(message, parse_mode=ParseMode.HTML)
    except asyncio.CancelledError:
        logging.warning("Help command cancelled during shutdown")
    except RuntimeError as e:
        if "Event loop is closed" in str(e):
            logging.warning("Blocked message send during shutdown")
        else:
            logging.error(f"Unexpected error: {e}")

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = (
        "✅ <b>البوت يعمل بكفاءة وجاهزية تامة</b>.\n\n"
        "💎 معك دائماً لأحدث أخبار وأسعار سوق الكريبتو.\n"
        "🌐 <a href=\"{OFFICIAL_SITE}\">إنفترون داو</a>"
    )
    await update.message.reply_text(message, parse_mode=ParseMode.HTML)

async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /price command to show cryptocurrency prices."""
    response_sent = False
    try:
        prices = database.get_market_prices()
        if not prices:
            await update.message.reply_text("⚠️ عذراً، لا توجد بيانات أسعار متاحة حالياً.")
            response_sent = True
            return

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

        await update.message.reply_text(price_message, parse_mode=ParseMode.MARKDOWN)
        response_sent = True

    except Exception as e:
        logger.error(f"Failed to fetch prices: {e}", exc_info=True)
        if not response_sent and not asyncio.get_running_loop().is_closed():
            await update.message.reply_text("⚠️ عذراً، حدث خطأ أثناء جلب الأسعار.")
            
async def market_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /market command to show cryptocurrency market information."""
    response_sent = False  # Flag to track if a response has been sent
    try:
        market_data = database.get_market_summary()
        if not market_data:
            logger.warning("Market summary data is empty. Ensure the database is being updated correctly.")
            await update.message.reply_text("⚠️ عذراً، لا توجد بيانات سوق متاحة حالياً. يرجى المحاولة لاحقاً.")
            response_sent = True
            return

        # Format market data
        total_market_cap = market_data.get('total_market_cap', 0) / 1e12  # Trillions
        total_volume = market_data.get('total_volume', 0) / 1e9            # Billions
        btc_dominance = market_data.get('btc_dominance', 0)
        eth_dominance = market_data.get('eth_dominance', 0)
        sentiment = '📈 *صاعد*' if total_market_cap > 2.5 else '📉 *هابط*'

        market_info = (
            "📊 *حالة سوق الكريبتو*\n\n"
            f"💰 *القيمة السوقية الإجمالية:*\n   `${total_market_cap:.2f} تريليون`\n\n"
            f"📈 *حجم التداول (24 ساعة):*\n   `${total_volume:.1f} مليار`\n\n"
            f"🔶 *هيمنة بيتكوين:*\n   `{btc_dominance:.1f}%`\n\n"
            f"🔷 *هيمنة إيثريوم:*\n   `{eth_dominance:.1f}%`\n\n"
            f"📝 *اتجاه السوق:*\n   {sentiment}\n\n"
            "⚠️ *ملاحظة*: البيانات محدثة من قاعدة البيانات ويتم تحديثها كل دقيقة."
        )

        await update.message.reply_text(market_info, parse_mode=ParseMode.MARKDOWN)
        response_sent = True

    except Exception as e:
        logger.error(f"Failed to fetch market summary: {e}", exc_info=True)
        if not response_sent and not asyncio.get_running_loop().is_closed():
            await update.message.reply_text("⚠️ عذراً، حدث خطأ أثناء جلب بيانات السوق. يرجى المحاولة لاحقاً.")

async def feedback_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.args:
        feedback_message = ' '.join(context.args)
        user = update.effective_user
        logger.info(f"📩 Feedback from {user.id} (@{user.username}): {feedback_message}")
        await update.message.reply_text("👍 شكراً لك على ملاحظاتك! تم استلامها وسيتم النظر فيها.")
    else:
        instructions = (
            "🔄 <b>إرسال ملاحظاتك أو اقتراحاتك:</b>\n\n"
            "لإرسال ملاحظاتك، استخدم الأمر بهذا الشكل:\n"
            "<code>/feedback أحب الأخبار التي يوفرها البوت، وأقترح إضافة تنبيهات للأسعار</code>\n\n"
            "🛠 نرحب بجميع ملاحظاتكم لتحسين خدماتنا."
        )
        await update.message.reply_text(instructions, parse_mode=ParseMode.HTML)

# ✅ Your handle_text remains clean and simple
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chat_type = update.message.chat.type
        if chat_type in ["group", "supergroup"]:
            if not update.message.text.startswith('/'):
                return

        await update.message.reply_text("🚀 شكراً لرسالتك! إذا كنت بحاجة إلى مساعدة، استخدم /help.")
    except Exception as e:
        logger.error(f"Failed to handle text message: {e}")

async def overview_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /overview command to send a market update to the user who triggered it."""
    try:
        # Fetch market data
        prices = database.get_market_prices()
        market_data = database.get_market_summary()

        if not prices or not market_data:
            await update.message.reply_text("⚠️ لا توجد بيانات متاحة حالياً. يرجى المحاولة لاحقاً.")
            return

        # Build the price section
        price_message = "💰 *تحديث حالات سوق الكريبتو:*\n\n"
        for coin, data in prices.items():
            change_emoji = "🟢" if data["change"] > 0 else "🔴"
            change_sign = "+" if data["change"] > 0 else ""
            price_message += (
                f"{coin}: ${data['price']:,.2f} {change_emoji} {change_sign}{data['change']:.2f}%\n"
            )

        # Extract market data and sentiment
        total_market_cap = market_data.get('total_market_cap', 0) / 1e12  # Trillions
        total_volume = market_data.get('total_volume', 0) / 1e9            # Billions
        btc_dominance = market_data.get('btc_dominance', 0)
        eth_dominance = market_data.get('eth_dominance', 0)
        sentiment = '📈 *صاعد*' if total_market_cap > 2.5 else '📉 *هابط*'

        # Append market summary
        price_message += (
            "\n📊 *ملخص السوق:*\n"
            f"💰 *القيمة السوقية:* ${total_market_cap:.2f} تريليون\n"
            f"📈 *حجم التداول (24 ساعة):* ${total_volume:.1f} مليار\n"
            f"🔶 *هيمنة بيتكوين:* {btc_dominance:.1f}%\n"
            f"🔷 *هيمنة إيثريوم:* {eth_dominance:.1f}%\n"
            f"📝 *اتجاه السوق:* {sentiment}\n"
        )

        price_message += "\n⚠️ *ملاحظة*: الأسعار والبيانات تقريبية لأغراض العرض فقط."

        # Send the message to the user who triggered the command
        await update.message.reply_text(price_message, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logger.error(f"Error in /overview command: {e}", exc_info=True)
        await update.message.reply_text("⚠️ حدث خطأ أثناء إرسال التحديث.")

async def handle_group_migration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle migration to a supergroup."""
    if update.message and update.message.migrate_from_chat_id:
        old_chat_id = update.message.migrate_from_chat_id
        new_chat_id = update.effective_chat.id
        
        # Remove old chat and add the new one
        database.remove_chat(old_chat_id)
        database.add_chat(new_chat_id, update.effective_chat.title, update.effective_chat.type)
        
        logger.info(f"Chat migrated from {old_chat_id} to {new_chat_id}")

async def chat_member_updated(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
        
    elif (result.old_chat_member.status in ['member', 'administrator'] and 
            result.new_chat_member.status in ['left', 'kicked']):
        database.remove_chat(chat_id)
        logger.info(f"Bot was removed from {chat_title} ({chat_id})")
    elif (result.old_chat_member.status != result.new_chat_member.status and
          result.new_chat_member.status in ['member', 'administrator']):
        database.add_chat(chat_id, chat_title, chat_type)
        logger.info(f"Bot status updated in {chat_title} ({chat_id}) to {result.new_chat_member.status}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global shutting_down  # Add this
    async with shutdown_lock:
        if shutting_down:
            return
                    
    logger.error(f"Exception in handler: {context.error}", exc_info=True)
    
    try:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى لاحقاً."
        )
    except Exception as e:
        logger.error(f"Failed to send error message: {e}")

def setup_handlers(app: Application) -> None:
    """Centralized handler configuration with proper ordering"""
    
    # 1. Command Handlers (Highest Priority)
    command_handlers = [
        CommandHandler("start", start_command),
        CommandHandler("help", help_command),
        CommandHandler("about", about_command),
        CommandHandler("status", status_command),
        CommandHandler("price", price_command),
        CommandHandler("market", market_command),
        CommandHandler("feedback", feedback_command),
        CommandHandler("overview", overview_command),
    ]
    for handler in command_handlers:
        app.add_handler(handler)

    # 2. Message Handlers
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_text
    ))

    # 3. Special Update Handlers
    app.add_handler(MessageHandler(
        filters.StatusUpdate.MIGRATE,
        handle_group_migration
    ))
    
    app.add_handler(ChatMemberHandler(
        chat_member_updated, 
        ChatMemberHandler.MY_CHAT_MEMBER
    ))

    # 4. Error Handler (Should be last)
    app.add_error_handler(error_handler)


async def setup_bot():
    """Initialize the bot application with proper setup."""
    global application, initializing
    async with init_lock:
        if application or initializing:
            return
        initializing = True
        try:
            # Your initialization logic here
            application = Application.Builder().token(TELEGRAM_BOT_TOKEN).build()
            setup_handlers(application)
            # Add other initialization steps
            logging.info("✅ Bot application initialized")
        finally:
            initializing = False

async def get_application() -> Application:
    """Safely get or create the application instance."""
    global application
    if not application:
        if not initializing:
            await setup_bot()
        # Wait for initialization to complete
        while initializing:
            await asyncio.sleep(0.1)
    return application


# ======================
# BACKGROUND TASKS
# ======================
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


async def send_hourly_price_update(context: ContextTypes.DEFAULT_TYPE):
    """Send hourly price and market updates to all chats from the database."""
    chats = database.get_all_chats()
    prices = database.get_market_prices()
    market_data = database.get_market_summary()

    if not prices or not market_data:
        logger.warning("Missing price or market data for hourly update.")
        return

    # Build the price section
    price_message = "💰 *تحديث حالات سوق الكريبتو كل ست ساعات:*\n\n"
    for coin, data in prices.items():
        change_emoji = "🟢" if data["change"] > 0 else "🔴"
        change_sign = "+" if data["change"] > 0 else ""
        price_message += (
            f"{coin}: `${data['price']:,.2f}` {change_emoji} {change_sign}{data['change']:.2f}%\n"
        )

    # Extract market data and sentiment
    total_market_cap = market_data.get('total_market_cap', 0) / 1e12  # Trillions
    total_volume = market_data.get('total_volume', 0) / 1e9            # Billions
    btc_dominance = market_data.get('btc_dominance', 0)
    eth_dominance = market_data.get('eth_dominance', 0)
    sentiment = '📈 *صاعد*' if total_market_cap > 2.5 else '📉 *هابط*'

    # Append market summary
    price_message += (
        "\n📊 *ملخص السوق:*\n"
        f"💰 *القيمة السوقية:* `${total_market_cap:.2f} تريليون`\n"
        f"📈 *حجم التداول (24 ساعة):* `${total_volume:.1f} مليار`\n"
        f"🔶 *هيمنة بيتكوين:* `{btc_dominance:.1f}%`\n"
        f"🔷 *هيمنة إيثريوم:* `{eth_dominance:.1f}%`\n"
        f"📝 *اتجاه السوق:* {sentiment}\n"
    )

    price_message += "\n⚠️ *ملاحظة*: الأسعار والبيانات تقريبية لأغراض العرض فقط."

    # Send to all chats
    for chat in chats:
        try:
            await context.bot.send_message(
                chat_id=chat['chat_id'],
                text=price_message,
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            logger.error(f"Failed to send price update to chat {chat['chat_id']}: {e}")
