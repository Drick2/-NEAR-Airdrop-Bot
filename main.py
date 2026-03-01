import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

users = {}  # user_id -> {'points': int, 'wallet': str, 'referrals': int, 'username': str}

MAIN_KEYBOARD = [
    [KeyboardButton("💰 Balance"), KeyboardButton("🔗 Referral Link")],
    [KeyboardButton("📤 Withdraw"), KeyboardButton("🆘 Support")],
    [KeyboardButton("🏠 Main Menu")],
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    first_name = user.first_name or "User"

    # Referral system: check for ?start=refXXXX
    referrer_id = None
    if context.args and len(context.args) > 0 and context.args[0].startswith('ref'):
        try:
            referrer_id = int(context.args[0][3:])
            if referrer_id != user_id and referrer_id in users:
                users[referrer_id]['points'] += 25
                users[referrer_id]['referrals'] += 1
                try:
                    await context.bot.send_message(
                        referrer_id,
                        f"🎉 New referral joined! +25 $NEAR added.\nYour total: {users[referrer_id]['points']}"
                    )
                except:
                    pass  # User may have privacy settings or blocked bot
        except:
            pass

    # Create user if new
    if user_id not in users:
        users[user_id] = {
            'points': 0,
            'wallet': None,
            'referrals': 0,
            'username': None
        }

    # Inline button
    keyboard = [[InlineKeyboardButton("✅ Join Airdrop", callback_data='join_airdrop')]]
    reply_markup_inline = InlineKeyboardMarkup(keyboard)

    # Rainbow orb image – REPLACE THIS URL with your direct Imgur link!
    orb_url = "https://i.imgur.com/YOUR_DIRECT_FILE_HERE.png"  # ← PASTE YOUR COPIED DIRECT LINK HERE

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

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'join_airdrop':
        await query.edit_message_text(
            text="Let's proceed:\n\n"
                 "◆ Join Our Telegram Group\n"
                 "◆ Join Our Telegram Channel\n\n"
                 "Now submit your Telegram username with @ to proceed:"
        )

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user_id = update.effective_user.id

    if user_id not in users:
        await update.message.reply_text("Please /start first!")
        return

    # Username submission
    if text.startswith('@') and not users[user_id]['username']:
        users[user_id]['username'] = text
        await update.message.reply_text(
            f"Username saved: {text}\n\n"
            "Now submit your BSC (BEP-20) wallet address.\n"
            "Copy from Trust Wallet or SafePal and paste here."
        )
        return

    # Wallet submission + tasks reward
    if not users[user_id]['wallet'] and text.startswith('0x') and len(text) == 42:
        users[user_id]['wallet'] = text
        users[user_id]['points'] += 100  # Reward for tasks
        await update.message.reply_text(
            f"Wallet saved: {text}\n\n"
            "Congratulations! 100 $NEAR credited to your balance.\n\n"
            "Share your referral link – get 25 $NEAR per friend!\n"
            "Need at least 5 referrals to qualify."
        )
        return

    # Menu actions
    if text == "💰 Balance":
        await update.message.reply_text(
            f"💰 $NEAR Balance\n"
            f"Points: {users[user_id]['points']}\n"
            f"Referrals: {users[user_id]['referrals']}\n"
            f"Wallet: {users[user_id]['wallet'] or 'Not set'}"
        )
    elif text == "🔗 Referral Link":
        ref_link = f"https://t.me/{context.bot.username}?start=ref{user_id}"
        await update.message.reply_text(f"Your referral link:\n{ref_link}\n+25 $NEAR per join!")
    elif text == "📤 Withdraw":
        await update.message.reply_text("Withdraw opens after $NEAR launch on BSC!\nNeed at least 5 referrals.")
    elif text == "🆘 Support":
        await update.message.reply_text("DM @drick_lil97996 for help!")
    elif text == "🏠 Main Menu":
        await update.message.reply_text("Main menu ready!", reply_markup=ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True, is_persistent=True))
    else:
        await update.message.reply_text("Use the menu buttons or /start to refresh!")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))
    app.run_polling()
