import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

users = {}

MAIN_KEYBOARD = [
    [KeyboardButton("💰 Balance"), KeyboardButton("🔗 Referral Link")],
    [KeyboardButton("📤 Withdraw"), KeyboardButton("🆘 Support")],
    [KeyboardButton("🏠 Main Menu")],
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    first_name = user.first_name or "User"

    if user_id not in users:
        users[user_id] = {'points': 0, 'wallet': None, 'referrals': 0, 'username': None}

    keyboard = [[InlineKeyboardButton("✅ Join Airdrop", callback_data='join_airdrop')]]
    reply_markup_inline = InlineKeyboardMarkup(keyboard)

    # Rainbow orb image (change this URL to yours)
    orb_url = "https://i.imgur.com/8zXvK9P.png"   # ← REPLACE THIS WITH YOUR IMAGE LINK

    await update.message.reply_photo(photo=orb_url, caption="🌈 $NEAR Airdrop – Nearer Than We Think! 🌈")

    welcome_text = (
        f"Hello, {first_name} 👋! I am your friendly $NEAR Airdrop bot\n\n"
        f"◆ Earn 100 $NEAR for completing tasks\n"
        f"◆ Earn 25 $NEAR for each referral\n\n"
        "Airdrop Rules\n"
        "Mandatory Tasks:\n"
        "◆ Join our Telegram Group\n"
        "◆ Join our Telegram Channel\n"
        "◆ Refer at least 5 friends\n\n"
        "Click on \"✅ Join Airdrop\" to proceed!"
    )

    await update.message.reply_text(welcome_text, reply_markup=reply_markup_inline)

    reply_markup_reply = ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True, is_persistent=True)
    await update.message.reply_text("Tap buttons below anytime:", reply_markup=reply_markup_reply)

# ... (the rest of the code from previous message - button_handler and handle_messages stay the same)
# Paste the full previous code here (button_handler, handle_messages, app.run_polling())

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))
    app.run_polling()
