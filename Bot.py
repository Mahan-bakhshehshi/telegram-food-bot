import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from samad_guilan import reserve_food
import logging

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Use environment variable for security
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set!")

ASK_USERNAME, ASK_PASSWORD = range(2)

async def start(update, context):
    user_id = update.effective_user.id
    username = update.effective_user.username
    logger.info(f"User {user_id} (@{username}) started the bot")
    
    await update.message.reply_text(
        "🍽️ سلام رفیق! به ربات رزرو غذا خوش اومدی\n"
        "شماره دانشجویی خودت رو وارد کن: 👇"
    )
    return ASK_USERNAME

async def get_username(update, context):
    context.user_data["username"] = update.message.text
    user_id = update.effective_user.id
    logger.info(f"User {user_id} entered username")
    
    await update.message.reply_text(
        "✅ شماره دانشجویی دریافت شد.\n"
        "حالا رمز عبور خود را وارد کنید:"
    )
    return ASK_PASSWORD

async def get_password(update, context):
    username = context.user_data["username"]
    password = update.message.text
    user_id = update.effective_user.id
    
    logger.info(f"User {user_id} attempting food reservation")
    
    await update.message.reply_text(
        "⏳ دارم غذا رزرو می‌کنم...\n"
        "ممکنه یه دقیقه طول بکشه، لطفاً صبر کن! 🤖"
    )

    try:
        result = reserve_food(username, password)
        await update.message.reply_text(f"✅ نتیجه:\n{result}")
        logger.info(f"User {user_id} reservation completed successfully")
        
    except Exception as e:
        error_msg = f"❌ خطا در رزرو غذا: {str(e)}"
        await update.message.reply_text(error_msg)
        logger.error(f"User {user_id} reservation failed: {e}")

    return ConversationHandler.END

async def cancel(update, context):
    await update.message.reply_text(
        "❌ عملیات لغو شد.\n"
        "برای شروع مجدد /start بزن"
    )
    return ConversationHandler.END

async def help_command(update, context):
    help_text = """
🤖 راهنمای ربات رزرو غذا:

📝 دستورات:
/start - شروع رزرو غذا
/help - نمایش این راهنما
/cancel - لغو عملیات جاری

⚠️ نکات مهم:
• فقط یه بار /start بزن و صبر کن
• شماره دانشجویی و رمز عبور رو درست وارد کن
• اگه خطا خورد، چند دقیقه بعد دوباره تلاش کن

🕐 این ربات 24 ساعته فعاله!
    """
    await update.message.reply_text(help_text)

async def error_handler(update, context):
    """Handle errors to prevent bot from crashing"""
    logger.error(f"Update {update} caused error {context.error}")

def main():
    if not BOT_TOKEN:
        print("❌ Error: BOT_TOKEN not found!")
        print("Make sure to set BOT_TOKEN environment variable")
        return

    # Create application
    app = Application.builder().token(BOT_TOKEN).build()

    # Create conversation handler
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_username)],
            ASK_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    # Add handlers
    app.add_handler(conv)
    app.add_handler(CommandHandler("help", help_command))
    app.add_error_handler(error_handler)

    logger.info("🤖 Bot is starting...")
    print("Bot is running 24/7...")
    print("Press Ctrl+C to stop")

    # Run the bot
    try:
        app.run_polling(drop_pending_updates=True)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")

if __name__ == "__main__":

    main()

