import os
import requests
from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Load environment variables from .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
HIBP_KEY = os.getenv("HIBP_KEY")

# /start command handler
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "👋 Welcome to *BreachWatcher Bot*.\n\n"
        "Send me your *email address* and I’ll check if it’s been exposed in any known data breaches.",
        parse_mode='Markdown'
    )

# Email scan handler
def check_breach(update: Update, context: CallbackContext):
    email = update.message.text.strip()
    print(f"[DEBUG] Received email: {email}")

    if "@" not in email or "." not in email:
        update.message.reply_text(f"❌ Invalid email: {email}")
        return

    url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
    headers = {
        "hibp-api-key": HIBP_KEY,
        "User-Agent": "BreachWatcherProBot"
    }

    try:
        response = requests.get(url, headers=headers)
        print(f"[DEBUG] Response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            reply = f"⚠️ *{len(data)} breaches found for* `{email}`:\n\n"

            for breach in data:
                name = breach.get('Name', 'Unknown')
                date = breach.get('BreachDate', 'Unknown Date')
                classes = ", ".join(breach.get('DataClasses', []))
                domain = breach.get('Domain', 'Unknown site')
                verified = "✅ Verified" if breach.get("IsVerified") else "⚠️ Unverified"

                reply += (
                    f"🔐 *{name}* ({domain})\n"
                    f"📅 Breach Date: `{date}`\n"
                    f"📂 Exposed: `{classes}`\n"
                    f"{verified}\n\n"
                )
        elif response.status_code == 404:
            reply = f"✅ Good news! No breaches found for `{email}`."
        else:
            reply = f"❌ Error: {response.status_code} — {response.text}"

        update.message.reply_text(reply, parse_mode='Markdown')

    except Exception as e:
        print(f"[ERROR] Exception: {str(e)}")
        update.message.reply_text("❌ Something went wrong while checking the breach.")

# Start the bot
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, check_breach))

    print("🚀 BreachWatcherPro_bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
