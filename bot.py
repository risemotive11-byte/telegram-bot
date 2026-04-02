import os
TOKEN = os.getenv("BOT_TOKEN")
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ================= CONFIG =================
ADMIN_ID = 7572666431  # your Telegram user ID
WALLET = "0xd9F1CE2e56D7f32EED384833C6537347574E1440"

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💰 Buy Plan", callback_data="buy")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🔥 Welcome to Premium Bot!\n\nClick below to purchase a plan:",
        reply_markup=reply_markup
    )

# ================= BUY =================
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("💜 Platinum – $50 (1M)", callback_data="plan_50")],
        [InlineKeyboardButton("🟡 Gold – $100 (1M)", callback_data="plan_100")],
        [InlineKeyboardButton("💎 Diamond – $150 (2M)", callback_data="plan_150")],
        [InlineKeyboardButton("🚀 Platinum Pro – $200 (3M)", callback_data="plan_200")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_text("💰 Select Your Plan:", reply_markup=reply_markup)

# ================= PLAN =================
async def plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data.split("_")
    amount = data[1]

    # Plan details
    if amount == "50":
        plan_name = "💜 Platinum"
        value = "1M"
    elif amount == "100":
        plan_name = "🟡 Gold"
        value = "1M"
    elif amount == "150":
        plan_name = "💎 Diamond"
        value = "2M"
    elif amount == "200":
        plan_name = "🚀 Platinum Pro"
        value = "3M"

    keyboard = [
        [InlineKeyboardButton("✅ I Paid", callback_data=f"paid_{amount}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_document(
    chat_id=query.message.chat_id,
    document=open("qr.png", "rb"),
    caption=f"""

{plan_name}

💰 Amount: ${amount} USDT (TRC20)
📦 You Get: {value}

📍 Wallet Address:
{WALLET}

⚠️ Send exact amount & click below after payment 👇
        """,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

# ================= PAID =================
async def paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["awaiting_txid"] = True
    context.user_data["amount"] = query.data.split("_")[1]

    await query.message.reply_text("📩 Please send your Transaction ID (TXID):")

# ================= HANDLE TXID =================
async def handle_txid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_txid"):
        txid = update.message.text
        amount = context.user_data.get("amount")

        # Send to admin
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"""
💰 New Payment Request

👤 User ID: {update.message.from_user.id}
💵 Amount: ${amount}
🔗 TXID: {txid}
            """
        )

        await update.message.reply_text("✅ Payment submitted! Please wait for admin approval.")

        context.user_data["awaiting_txid"] = False

# ================= MAIN =================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buy, pattern="buy"))
app.add_handler(CallbackQueryHandler(plan, pattern="plan_"))
app.add_handler(CallbackQueryHandler(paid, pattern="paid_"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_txid))

print("🤖 Bot is running...")
app.run_polling()