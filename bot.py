import logging
import asyncio
from telegram import Update, Bot
from telegram.constants import ParseMode
from telegram.ext import Application, ContextTypes, CommandHandler, MessageHandler, filters, ChatMemberHandler
from telegram.error import TelegramError
from config import TELEGRAM_BOT_TOKEN, WEBHOOK_URL
import database
from models import News
import weakref
import shared
    
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
        user = update.effective_user
        message = update.message.text if update.message else "/start"
        logger.info(f"📨 Command: {message} | From: {user.full_name} (@{user.username}, ID: {user.id})")

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

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    message = update.message.text if update.message else "<no message>"
    logger.info(f"📨 Command: {message} | From: {user.full_name} (@{user.username}, ID: {user.id})")

    global shutting_down
    async with shared.shutdown_lock:
        if shared.is_shutting_down:
            logger.warning("⛔ Blocked status command during shutdown")
            return

    try:
        help_text = (
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
        if update.message:
            await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)
    except asyncio.CancelledError:
        logger.warning("⛔ Help command cancelled during shutdown")
    except RuntimeError as e:
        if "Event loop is closed" in str(e):
            logger.warning("⚠️ Blocked help message send during shutdown")
        else:
            logger.error(f"❌ Unexpected error in /help: {e}")

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    message = update.message.text if update.message else "<no message>"
    logger.info(f"📨 Command: {message} | From: {user.full_name} (@{user.username}, ID: {user.id})")

    global shutting_down
    async with shared.shutdown_lock:
        if shared.is_shutting_down:
            logger.warning("⛔ Blocked status command during shutdown")
            return

    try:
        about_text = (
            "💎 <b>بوت أخبار الكريبتو - من تطوير وإنفاذ إنفترون داو</b> 💎\n\n"
            "🔹 منصة ذكية مدعومة من <b>إنفترون داو</b> – رائدة الاستثمار والتمويل اللامركزي عبر البلوك تشين 🔹\n\n"
            "تم تصميم هذا البوت خصيصاً ليكون امتداداً لرؤية إنفترون داو في تمكين المجتمعات الرقمية من الوصول إلى أحدث أخبار العملات الرقمية والأسواق المالية بكل سهولة واحترافية داخل مجموعات تيليجرام.\n\n"
            "✨ <b>مميزات البوت:</b>\n"
            "✅ نشر أخبار العملات الرقمية بشكل تلقائي من مصادر موثوقة\n"
            "✅ عرض أسعار العملات الرقمية محدثة لحظة بلحظة\n"
            "✅ متابعة أداء وتفاعل المجموعات بشكل ذكي\n"
            "✅ تنسيق احترافي وجذاب للمنشورات\n"
            "✅ دعم كامل للغة العربية\n\n"
            "🚀 <b>العملات المدعومة (والمزيد قادم):</b>\n"
            "• بيتكوين (BTC)\n"
            "• إيثريوم (ETH)\n"
            "• سولانا (SOL)\n"
            "• بينانس كوين (BNB)\n"
            "• كاردانو (ADA)\n"
            "... وأكثر من ذلك\n\n"
            "🌐 <b>لماذا تختار بوت إنفترون داو؟</b>\n"
            "لأن هذا البوت ليس مجرد أداة للنشر، بل هو جزء من منظومة إنفترون داو التي تقود مستقبل الاستثمار والتمويل اللامركزي عبر تقنيات البلوك تشين. هدفنا تعزيز الشفافية، تمكين المجتمعات، ونشر المعرفة المالية الدقيقة والمحدثة.\n\n"
            "📱 هذا البوت مقدم حصرياً من: <b>إنفترون داو</b> — \"نبحث عن الجواهر... ونموّلها\""
        )
        if update.message:
            await update.message.reply_text(about_text, parse_mode=ParseMode.HTML)

    except asyncio.CancelledError:
        logger.warning("⛔ About command cancelled during shutdown")
    except RuntimeError as e:
        if "Event loop is closed" in str(e):
            logger.warning("⚠️ Blocked about message send during shutdown")
        else:
            logger.error(f"❌ Unexpected error in /about: {e}")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    message_text = update.message.text if update.message else "<no message>"
    logger.info(f"📨 Command: {message_text} | From: {user.full_name} (@{user.username}, ID: {user.id})")

    global shutting_down
    async with shared.shutdown_lock:
        if shared.is_shutting_down:
            logger.warning("⛔ Blocked status command during shutdown")
            return
    try:
        status_message = (
            f"✅ <b>البوت يعمل بكفاءة وجاهزية تامة</b>.\n\n"
            f"💎 معك دائماً لأحدث أخبار وأسعار سوق الكريبتو.\n"
            f"🌐 <a href=\"{OFFICIAL_SITE}\">إنفترون داو</a>"
        )
        if update.message:
            await update.message.reply_text(status_message, parse_mode=ParseMode.HTML)

    except asyncio.CancelledError:
        logger.warning("⛔ Status command cancelled during shutdown")
    except RuntimeError as e:
        if "Event loop is closed" in str(e):
            logger.warning("⚠️ Blocked status message send during shutdown")
        else:
            logger.error(f"❌ Unexpected error in /status: {e}")

async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    message_text = update.message.text if update.message else "<no message>"
    logger.info(f"📨 Command: {message_text} | From: {user.full_name} (@{user.username}, ID: {user.id})")

    global shutting_down
    async with shared.shutdown_lock:
        if shared.is_shutting_down:
            logger.warning("⛔ Blocked status command during shutdown")
            return

    response_sent = False
    try:
        prices = database.get_market_prices()
        if not prices:
            if update.message:
                await update.message.reply_text("⚠️ عذراً، لا توجد بيانات أسعار متاحة حالياً.")
                response_sent = True
            return

        price_message = "💰 <b>أسعار العملات الرقمية الآن:</b>\n"
        for coin, data in prices.items():
            change_emoji = "🟢" if data["change"] > 0 else "🔴"
            change_sign = "+" if data["change"] > 0 else ""
            price_message += (
                f"🔹 <b>{coin}</b> — <code>${data['price']:,.2f}</code> "
                f"({change_emoji} {change_sign}{data['change']:.2f}%)\n"
            )

        price_message += "\n⚠️ <i>هذه الأسعار تقريبية لأغراض العرض فقط.</i>"

        if update.message:
            await update.message.reply_text(price_message, parse_mode=ParseMode.HTML)
            response_sent = True

    except asyncio.CancelledError:
        logger.warning("⛔ Price command cancelled during shutdown")
    except RuntimeError as e:
        if "Event loop is closed" in str(e):
            logger.warning("⚠️ Blocked price message send during shutdown")
        else:
            logger.error(f"❌ Unexpected error in /price: {e}")
    except Exception as e:
        logger.error(f"❌ Failed to fetch prices: {e}", exc_info=True)
        if not response_sent:
            try:
                if update.message and not asyncio.get_running_loop().is_closed():
                    await update.message.reply_text("⚠️ عذراً، حدث خطأ أثناء جلب الأسعار.")
            except Exception as inner_e:
                logger.error(f"Failed to send fallback error message: {inner_e}")
            
async def market_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /market command to show cryptocurrency market information."""
    user = update.effective_user
    message_text = update.message.text if update.message else "<no message>"
    logger.info(f"📨 Command: {message_text} | From: {user.full_name} (@{user.username}, ID: {user.id})")

    global shutting_down
    async with shared.shutdown_lock:
        if shared.is_shutting_down:
            logger.warning("⛔ Blocked status command during shutdown")
            return
    response_sent = False
    try:
        market_data = database.get_market_summary()
        if not market_data:
            logger.warning("Market summary data is empty. Ensure the database is being updated correctly.")
            if update.message:
                await update.message.reply_text("⚠️ عذراً، لا توجد بيانات سوق متاحة حالياً. يرجى المحاولة لاحقاً.")
                response_sent = True
            return

        total_market_cap = market_data.get('total_market_cap', 0) / 1e12  # in trillions
        total_volume = market_data.get('total_volume', 0) / 1e9            # in billions
        btc_dominance = market_data.get('btc_dominance', 0)
        eth_dominance = market_data.get('eth_dominance', 0)
        sentiment = '📈 <b>صاعد</b>' if total_market_cap > 2.5 else '📉 <b>هابط</b>'

        market_info = (
            "📊 <b>حالة سوق الكريبتو</b>\n"
            f"💰 <b>القيمة السوقية:</b> <code>{total_market_cap:.2f} تريليون $</code>\n"
            f"📈 <b>حجم التداول (24 ساعة):</b> <code>{total_volume:.1f} مليار $</code>\n"
            f"🔶 <b>هيمنة بيتكوين:</b> <code>{btc_dominance:.1f}%</code>\n"
            f"🔷 <b>هيمنة إيثريوم:</b> <code>{eth_dominance:.1f}%</code>\n"
            f"📝 <b>اتجاه السوق:</b> {sentiment}\n\n"
            "⚠️ <i>البيانات تقريبية وتُحدث دورياً.</i>"
        )

        if update.message:
            await update.message.reply_text(market_info, parse_mode=ParseMode.HTML)
            response_sent = True

    except asyncio.CancelledError:
        logger.warning("⛔ Market command cancelled during shutdown")
    except RuntimeError as e:
        if "Event loop is closed" in str(e):
            logger.warning("⚠️ Blocked market message send during shutdown")
        else:
            logger.error(f"❌ Unexpected error in /market: {e}")
    except Exception as e:
        logger.error(f"❌ Failed to fetch market summary: {e}", exc_info=True)
        if not response_sent:
            try:
                if update.message and not asyncio.get_running_loop().is_closed():
                    await update.message.reply_text("⚠️ عذراً، حدث خطأ أثناء جلب بيانات السوق. يرجى المحاولة لاحقاً.")
            except Exception as inner_e:
                logger.error(f"Failed to send fallback error message: {inner_e}")

async def feedback_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    message_text = update.message.text if update.message else "<no message>"
    logger.info(f"📨 Command: {message_text} | From: {user.full_name} (@{user.username}, ID: {user.id})")

    global shutting_down
    async with shared.shutdown_lock:
        if shared.is_shutting_down:
            logger.warning("⛔ Blocked status command during shutdown")
            return
    try:
        if context.args:
            feedback_message = ' '.join(context.args)
            logger.info(f"📩 Feedback from {user.id} (@{user.username}): {feedback_message}")
            if update.message:
                await update.message.reply_text("👍 شكراً لك على ملاحظاتك! تم استلامها وسيتم النظر فيها.")
        else:
            instructions = (
                "🔄 <b>إرسال ملاحظاتك أو اقتراحاتك:</b>\n\n"
                "لإرسال ملاحظاتك، استخدم الأمر بهذا الشكل:\n"
                "<code>/feedback أحب الأخبار التي يوفرها البوت، وأقترح إضافة تنبيهات للأسعار</code>\n\n"
                "🛠 نرحب بجميع ملاحظاتكم لتحسين خدماتنا."
            )
            if update.message:
                await update.message.reply_text(instructions, parse_mode=ParseMode.HTML)

    except asyncio.CancelledError:
        logger.warning("⛔ Feedback command cancelled during shutdown")
    except RuntimeError as e:
        if "Event loop is closed" in str(e):
            logger.warning("⚠️ Blocked feedback message send during shutdown")
        else:
            logger.error(f"❌ Unexpected error in /feedback: {e}")
    except Exception as e:
        logger.error(f"❌ Failed to handle feedback command: {e}", exc_info=True)
        try:
            if update.message and not asyncio.get_running_loop().is_closed():
                await update.message.reply_text("⚠️ حدث خطأ أثناء إرسال ملاحظاتك. يرجى المحاولة لاحقاً.")
        except Exception as inner_e:
            logger.error(f"Failed to send fallback error message: {inner_e}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message_text = update.message.text if update.message else "<no message>"
    logger.info(f"📨 Message: {message_text} | From: {user.full_name} (@{user.username}, ID: {user.id})")

    global shutting_down
    async with shared.shutdown_lock:
        if shared.is_shutting_down:
            logger.warning("⛔ Blocked status command during shutdown")
            return
    try:
        if not update.message:
            return

        chat_type = update.message.chat.type
        text = update.message.text

        if chat_type in ["group", "supergroup"]:
            if text.startswith('/'):
                # Command (handled elsewhere), do nothing
                return
            else:
                # You can optionally ignore normal group messages
                return

        # Private chat fallback reply
        await update.message.reply_text(
            "🚀 شكراً لرسالتك! إذا كنت بحاجة إلى مساعدة، استخدم الأمر /help.",
            parse_mode=ParseMode.HTML
        )

    except asyncio.CancelledError:
        logger.warning("⛔ Text handler cancelled during shutdown")
    except RuntimeError as e:
        if "Event loop is closed" in str(e):
            logger.warning("⚠️ Blocked text reply during shutdown")
        else:
            logger.error(f"❌ Unexpected error in handle_text: {e}")
    except Exception as e:
        logger.error(f"❌ Failed to handle text message: {e}", exc_info=True)
        try:
            if update.message and not asyncio.get_running_loop().is_closed():
                await update.message.reply_text("⚠️ حدث خطأ أثناء معالجة رسالتك.")
        except Exception as inner_e:
            logger.error(f"❌ Failed to send fallback error message: {inner_e}")

async def overview_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /overview command to send a market update to the user who triggered it."""
    user = update.effective_user
    message_text = update.message.text if update.message else "<no message>"
    logger.info(f"📨 Command: {message_text} | From: {user.full_name} (@{user.username}, ID: {user.id})")

    global shutting_down
    async with shared.shutdown_lock:
        if shared.is_shutting_down:
            logger.warning("⛔ Blocked status command during shutdown")
            return
    try:
        prices = database.get_market_prices()
        market_data = database.get_market_summary()

        if not prices or not market_data:
            if update.message:
                await update.message.reply_text("⚠️ لا توجد بيانات متاحة حالياً. يرجى المحاولة لاحقاً.")
            return

        # 📈 Build coin price summary
        price_message = "💰 <b>تحديث حالات سوق الكريبتو:</b>\n"
        for coin, data in prices.items():
            change_emoji = "🟢" if data["change"] > 0 else "🔴"
            change_sign = "+" if data["change"] > 0 else ""
            price_message += (
                f"🔹 <b>{coin}</b>: <code>${data['price']:,.2f}</code> ({change_emoji} {change_sign}{data['change']:.2f}%)\n"
            )

        # 📊 Build market summary
        total_market_cap = market_data.get('total_market_cap', 0) / 1e12
        total_volume = market_data.get('total_volume', 0) / 1e9
        btc_dominance = market_data.get('btc_dominance', 0)
        eth_dominance = market_data.get('eth_dominance', 0)
        sentiment = '📈 <b>صاعد</b>' if total_market_cap > 2.5 else '📉 <b>هابط</b>'

        price_message += (
            "\n📊 <b>ملخص السوق:</b>\n"
            f"💰 <b>القيمة السوقية:</b> <code>{total_market_cap:.2f} تريليون $</code>\n"
            f"📈 <b>حجم التداول (24 ساعة):</b> <code>{total_volume:.1f} مليار $</code>\n"
            f"🔶 <b>هيمنة بيتكوين:</b> <code>{btc_dominance:.1f}%</code>\n"
            f"🔷 <b>هيمنة إيثريوم:</b> <code>{eth_dominance:.1f}%</code>\n"
            f"📝 <b>اتجاه السوق:</b> {sentiment}"
        )

        price_message += "\n\n⚠️ <i>الأسعار والبيانات تقريبية لأغراض العرض فقط.</i>"

        if update.message:
            await update.message.reply_text(price_message, parse_mode=ParseMode.HTML)

    except asyncio.CancelledError:
        logger.warning("⛔ Overview command cancelled during shutdown")
    except RuntimeError as e:
        if "Event loop is closed" in str(e):
            logger.warning("⚠️ Blocked overview message send during shutdown")
        else:
            logger.error(f"❌ Unexpected error in /overview: {e}")
    except Exception as e:
        logger.error(f"❌ Error in /overview command: {e}", exc_info=True)
        try:
            if update.message and not asyncio.get_running_loop().is_closed():
                await update.message.reply_text("⚠️ حدث خطأ أثناء إرسال التحديث.")
        except Exception as inner_e:
            logger.error(f"❌ Failed to send fallback error message: {inner_e}")

async def handle_group_migration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle migration of a group to a supergroup."""
    user = update.effective_user
    logger.info(f"📨 Group migration event triggered by: {user.full_name} (@{user.username}, ID: {user.id})" if user else "📨 Group migration triggered.")

    global shutting_down
    async with shared.shutdown_lock:
        if shared.is_shutting_down:
            logger.warning("⛔ Blocked status command during shutdown")
            return
    try:
        if update.message and update.message.migrate_from_chat_id:
            old_chat_id = update.message.migrate_from_chat_id
            new_chat_id = update.effective_chat.id

            # Update database records
            database.remove_chat(old_chat_id)
            database.add_chat(new_chat_id, update.effective_chat.title, update.effective_chat.type)

            logger.info(f"🔁 Chat migrated from {old_chat_id} ➝ {new_chat_id} ({update.effective_chat.title})")

    except Exception as e:
        logger.error(f"❌ Error handling group migration: {e}", exc_info=True)

async def chat_member_updated(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Track when the bot is added to or removed from a chat."""
    result = update.my_chat_member
    if not result:
        return

    chat_id = result.chat.id
    chat_title = result.chat.title or f"Chat {chat_id}"
    chat_type = result.chat.type

    logger.info(f"🤖 Bot membership update in {chat_title} ({chat_id}): "
                f"{result.old_chat_member.status} → {result.new_chat_member.status}")

    global shutting_down
    async with shared.shutdown_lock:
        if shared.is_shutting_down:
            logger.warning("⛔ Blocked status command during shutdown")
            return
    try:
        # Bot was added to a chat
        if (result.old_chat_member.status in ['left', 'kicked'] and
                result.new_chat_member.status in ['member', 'administrator']):
            database.add_chat(chat_id, chat_title, chat_type)
            logger.info(f"✅ Bot added to {chat_title} ({chat_id})")

            if chat_type in ['group', 'supergroup']:
                welcome_message = (
                    "👋 أهلاً! تم إضافة <b>بوت أخبار الكريبتو</b> إلى هذه المجموعة.\n\n"
                    "سأقوم بنشر أخبار الكريبتو تلقائياً هنا.\n\n"
                    "<b>الأوامر المتاحة:</b>\n"
                    "/help - عرض معلومات المساعدة\n"
                    "/about - معلومات عن البوت\n"
                    "/price - عرض أسعار العملات الرقمية"
                )
                await context.bot.send_message(chat_id=chat_id, text=welcome_message, parse_mode=ParseMode.HTML)

        # Bot was removed
        elif (result.old_chat_member.status in ['member', 'administrator'] and
              result.new_chat_member.status in ['left', 'kicked']):
            database.remove_chat(chat_id)
            logger.info(f"❌ Bot removed from {chat_title} ({chat_id})")

        # Status changed (e.g., restricted → member)
        elif (result.old_chat_member.status != result.new_chat_member.status and
              result.new_chat_member.status in ['member', 'administrator']):
            database.add_chat(chat_id, chat_title, chat_type)
            logger.info(f"🔄 Bot status updated in {chat_title} ({chat_id}) → {result.new_chat_member.status}")

    except asyncio.CancelledError:
        logger.warning("⛔ chat_member_updated cancelled during shutdown")
    except RuntimeError as e:
        if "Event loop is closed" in str(e):
            logger.warning("⚠️ Blocked membership message during shutdown")
        else:
            logger.error(f"❌ Unexpected RuntimeError: {e}")
    except Exception as e:
        logger.error(f"❌ Error in chat_member_updated: {e}", exc_info=True)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    global shutting_down
    async with shared.shutdown_lock:
        if shared.is_shutting_down:
            logger.warning("⛔ Blocked status command during shutdown")
            return
    logger.error(f"❌ Exception in handler: {context.error}", exc_info=True)

    # Attempt to send user-friendly error message
    try:
        if isinstance(update, Update) and update.effective_chat:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="⚠️ حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى لاحقاً."
            )
    except Exception as e:
        logger.error(f"❌ Failed to send error message to user: {e}")

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


application: Application | None = None
init_lock = asyncio.Lock()
initializing = False

async def setup_bot():
    global application, initializing
    async with init_lock:
        if application or initializing:
            return
        initializing = True
        try:
            await shared.set_shutting_down(False)  # ✅ This is the correct fix clearly

            application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
            setup_handlers(application)

            application.job_queue.run_repeating(
                send_hourly_price_update,
                interval=3600,
                first=60,
                name="hourly_price_update"
            )

            logging.info("✅ Bot application initialized and hourly job scheduled")

        finally:
            initializing = False

async def get_application() -> Application:
    """Safely get or create the application instance."""
    global application
    if not application:
        if not initializing:
            await setup_bot()
        # Wait for setup to complete (but avoid infinite wait on failure)
        retries = 0
        while initializing and retries < 50:  # wait up to 5 seconds
            await asyncio.sleep(0.1)
            retries += 1

        if not application:
            logger.error("❌ Application failed to initialize.")
            raise RuntimeError("Bot application could not be initialized.")
            
    return application


# ======================
# BACKGROUND TASKS
# ======================
async def broadcast_news(news: News):
    """Broadcast news to all chats where the bot is a member."""
    global shutting_down
    async with shared.shutdown_lock:
        if shared.is_shutting_down:
            logger.warning("⛔ Blocked status command during shutdown")
            return
    
    chats = database.get_all_chats()
    if not chats:
        logger.warning("⚠️ No chats to broadcast to.")
        return 0, 0

    message_text = news.format_telegram_message()
    success_count = 0
    error_count = 0

    try:
        application = await get_application()
        bot = application.bot

        for chat in chats:
            chat_id = chat['chat_id']
            try:
                message = await bot.send_message(
                    chat_id=chat_id,
                    text=message_text,
                    parse_mode=None,  # Avoid formatting issues
                    disable_web_page_preview=False if news.image_url else True
                )
                database.log_message(news.news_id, chat_id, message.message_id)
                success_count += 1
                await asyncio.sleep(0.5)  # Prevent rate-limiting

            except TelegramError as e:
                logger.error(f"❌ Failed to send to {chat_id}: {e}")
                error_count += 1

                if "bot was kicked" in str(e).lower() or "chat not found" in str(e).lower():
                    database.remove_chat(chat_id)
                    logger.info(f"🧹 Removed chat {chat_id} (bot removed or chat deleted)")

            except asyncio.CancelledError:
                logger.warning("⛔ Broadcast cancelled mid-loop during shutdown")
                break

    except Exception as e:
        logger.error(f"❌ Broadcast error: {e}", exc_info=True)

    logger.info(f"📢 Broadcast complete. ✅ Sent: {success_count} ❌ Failed: {error_count}")
    return success_count, error_count


async def send_hourly_price_update(context: ContextTypes.DEFAULT_TYPE):
    """Send hourly price and market updates to all chats from the database."""
    global shutting_down
    async with shared.shutdown_lock:
        if shared.is_shutting_down:
            logger.warning("⛔ Blocked status command during shutdown")
            return
    chats = database.get_all_chats()
    prices = database.get_market_prices()
    market_data = database.get_market_summary()

    if not prices or not market_data:
        logger.warning("⚠️ Missing price or market data for hourly update.")
        return

    # 📈 Build price section
    price_message = "💰 <b>تحديث سوق الكريبتو كل ست ساعات:</b>\n"
    for coin, data in prices.items():
        change_emoji = "🟢" if data["change"] > 0 else "🔴"
        change_sign = "+" if data["change"] > 0 else ""
        price_message += (
            f"🔹 <b>{coin}</b>: <code>${data['price']:,.2f}</code> ({change_emoji} {change_sign}{data['change']:.2f}%)\n"
        )

    # 📊 Append market summary
    total_market_cap = market_data.get('total_market_cap', 0) / 1e12
    total_volume = market_data.get('total_volume', 0) / 1e9
    btc_dominance = market_data.get('btc_dominance', 0)
    eth_dominance = market_data.get('eth_dominance', 0)
    sentiment = '📈 <b>صاعد</b>' if total_market_cap > 2.5 else '📉 <b>هابط</b>'

    price_message += (
        "\n📊 <b>ملخص السوق:</b>\n"
        f"💰 <b>القيمة السوقية:</b> <code>{total_market_cap:.2f} تريليون $</code>\n"
        f"📈 <b>حجم التداول (24 ساعة):</b> <code>{total_volume:.1f} مليار $</code>\n"
        f"🔶 <b>هيمنة بيتكوين:</b> <code>{btc_dominance:.1f}%</code>\n"
        f"🔷 <b>هيمنة إيثريوم:</b> <code>{eth_dominance:.1f}%</code>\n"
        f"📝 <b>اتجاه السوق:</b> {sentiment}"
    )

    price_message += "\n\n⚠️ <i>الأسعار والبيانات تقريبية لأغراض العرض فقط.</i>"

    # ✅ Send to all chats
    for chat in chats:
        chat_id = chat['chat_id']
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=price_message,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )
            await asyncio.sleep(0.5)  # To avoid rate limits

        except TelegramError as e:
            logger.error(f"❌ Failed to send price update to chat {chat_id}: {e}")
            if "bot was kicked" in str(e).lower() or "chat not found" in str(e).lower():
                database.remove_chat(chat_id)
                logger.info(f"🧹 Removed chat {chat_id} (bot removed or chat deleted)")

        except asyncio.CancelledError:
            logger.warning("⛔ Hourly price update cancelled during shutdown")
            break

        except Exception as e:
            logger.error(f"Unexpected error sending update to {chat_id}: {e}", exc_info=True)