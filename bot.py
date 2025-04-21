import random
import string
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from datetime import datetime, timedelta



PAYMENT_PER_ACCOUNT = 6.00  # 6.00 BDT per Gmail registration


# Initialize Database
def init_db():
    conn = sqlite3.connect('gmail_accounts.db')
    cursor = conn.cursor()

    # Ensure the accounts table has the correct schema
    cursor.execute('''CREATE TABLE IF NOT EXISTS accounts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT,
                        password TEXT,
                        status TEXT,
                        user_id INTEGER,
                        registration_time TEXT,
                        verification_time TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        balance REAL,
                        referrals INTEGER)''')

    conn.commit()
    conn.close()

# Function to generate a random email and password
def generate_credentials():
    email = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10)) + "@gmail.com"
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    return email, password

# Floating Keyboard layout
keyboard = [
    ["📥 Register New Gmail", "📂 My Accounts"],
    ["💰 Balance", "👥 My Referrals"],
    ["⚙️ Settings", "❓ Help"]
]
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Original Start message
start_message = (
    "Gmail অ্যাকাউন্ট রেজিস্টার করে টাকা উপার্জন করুন।\n"
    "প্রতিটি অ্যাকাউন্টের জন্য আপনি পাবেন: $০.০৯\n\n"
    "এটা খুব সহজ:\n"
    "১. বট আপনাকে Gmail অ্যাকাউন্টের ডাটা দেবে\n"
    "২. আপনি সেগুলো কপি করে Google-এ যাবেন\n"
    "৩. সেখানে Gmail অ্যাকাউন্ট তৈরি করবেন\n"
    "৪. নিশ্চিত করতে বটে ফিরে আসবেন"
)

# Start function (with the original message)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(start_message, reply_markup=reply_markup)

# Function to handle Gmail Registration
async def register_gmail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email, password = generate_credentials()

    # Save these temporarily for button callbacks
    context.user_data["current_email"] = email
    context.user_data["current_password"] = password
    context.user_data["user_id"] = update.message.from_user.id  # Save the user_id

    message = (
    f"নির্দিষ্ট তথ্য ব্যবহার করে একটি Gmail অ্যাকাউন্ট রেজিস্টার করুন এবং ৬.০০ টাকা উপার্জন করুন\n\n"
    f"📧 ইমেইল: {email}\n"
    f"🔐 পাসওয়ার্ড: {password}\n\n"
    "🔐 নিশ্চিত করুন যে আপনি নির্দিষ্ট পাসওয়ার্ড ব্যবহার করছেন, অন্যথায় অ্যাকাউন্টের জন্য অর্থ প্রদান করা হবে না"
)

    keyboard = [
        [InlineKeyboardButton("✅ Done", callback_data=f"done_{email}_{password}"),
         InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_{email}_{password}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(message, reply_markup=reply_markup)



# Handle callback for Done
async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data.split('_')
    action = data[0]  # done or cancel
    email = data[1]
    password = data[2]

    # If it's done
    if action == "done":
        registration_time = datetime.now().isoformat()
        verification_time = (datetime.now() + timedelta(days=3)).isoformat()

        # Insert the Gmail registration data and user_id into the database
        conn = sqlite3.connect('gmail_accounts.db')
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO accounts (email, password, status, user_id, registration_time, verification_time)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (email, password, "pending", context.user_data["user_id"], registration_time, verification_time))
        conn.commit()
        conn.close()

        await query.message.edit_text(
        f"নির্দিষ্ট তথ্য ব্যবহার করে একটি Gmail অ্যাকাউন্ট রেজিস্টার করুন এবং ৬.০০ টাকা উপার্জন করুন\n\n"
        f"📧 ইমেইল: {email}\n"
        f"🔐 পাসওয়ার্ড: {password}\n\n"
        "🔐 নিশ্চিত করুন যে আপনি নির্দিষ্ট পাসওয়ার্ড ব্যবহার করছেন, অন্যথায় অ্যাকাউন্টের জন্য অর্থ প্রদান করা হবে না\n"
        "______________________________\n\n"
        "💰 ৬.০০ টাকা হোল্ডে জমা হয়েছে\n"
        "অর্থ ৩ দিনের হোল্ডের পর মেইন ব্যালেন্সে স্থানান্তরিত হবে"
    )
    else:
        # If it's cancel
       await query.message.edit_text(
    f"রেজিস্ট্রেশন বাতিল হয়েছে\n\n"
    f"📧 ইমেইল: {email}\n"
    f"🔐 পাসওয়ার্ড: {password}\n\n"
    "🔐 নিশ্চিত করুন যে আপনি নির্দিষ্ট পাসওয়ার্ড ব্যবহার করছেন, অন্যথায় অ্যাকাউন্টের জন্য অর্থ প্রদান করা হবে না"
)


# Handle callback for Cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data.split('_')
    action = data[0]  # done or cancel
    email = data[1]
    password = data[2]

    # If it's cancel
    if action == "cancel":
        await query.message.edit_text(
            f"রেজিস্ট্রেশন বাতিল হয়েছে\n\n"
            f"📧 ইমেইল: {email}\n"
            f"🔐 পাসওয়ার্ড: {password}\n\n"
            "🔐 নিশ্চিত করুন যে আপনি নির্দিষ্ট পাসওয়ার্ড ব্যবহার করছেন, অন্যথায় অ্যাকাউন্টের জন্য অর্থ প্রদান করা হবে না"
        )


# Handle My Accounts
async def my_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect('gmail_accounts.db')
    cursor = conn.cursor()
    cursor.execute("SELECT email, status FROM accounts")
    accounts = cursor.fetchall()
    conn.close()

    if accounts:
        accounts_message = "Your Gmail Accounts:\n\n"
        for account in accounts:
            accounts_message += f"📧 {account[0]} - Status: {account[1]}\n"
    else:
        accounts_message = "You have no registered Gmail accounts yet."

    await update.message.reply_text(accounts_message, reply_markup=reply_markup)

# Handle Balance
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect('gmail_accounts.db')
    cursor = conn.cursor()

    # Fetch all accounts for the current user
    cursor.execute("SELECT status, verification_time FROM accounts WHERE user_id = ?", (update.message.from_user.id,))
    accounts = cursor.fetchall()
    conn.close()

    main_balance = 0
    hold_balance = 0

    for status, verification_time in accounts:
        if status == "verified":
            main_balance += PAYMENT_PER_ACCOUNT
        elif status == "pending":
            if verification_time:
                verification_time_obj = datetime.fromisoformat(verification_time)
                if datetime.now() >= verification_time_obj:
                    main_balance += PAYMENT_PER_ACCOUNT
                else:
                    hold_balance += PAYMENT_PER_ACCOUNT
            else:
                hold_balance += PAYMENT_PER_ACCOUNT

    balance_msg = (
        f"💰 Balance Summary:\n\n"
        f"✅ Main Balance: {main_balance:.2f} BDT\n"
        f"⏳ Hold Balance: {hold_balance:.2f} BDT\n\n"
        "Funds in hold will be released 3 days after registration & verification."
    )

    # New floating keyboard for balance menu
    balance_keyboard = [
        ["🏧 Payout", "📜 Balance History"],
        ["🔙 Back"]
    ]
    reply_markup = ReplyKeyboardMarkup(balance_keyboard, resize_keyboard=True)

    await update.message.reply_text(balance_msg, reply_markup=reply_markup)

# Handle My Referrals
async def my_referrals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    conn = sqlite3.connect('gmail_accounts.db')
    cursor = conn.cursor()

    # Fetch number of referrals
    cursor.execute("SELECT referrals FROM users WHERE user_id = ?", (user_id,))
    referrals = cursor.fetchone()
    referrals_count = referrals[0] if referrals else 0

    # Fetch bot username
    bot_username = (await context.bot.get_me()).username
    referral_link = f"https://t.me/{bot_username}?start={user_id}"

    message = (
        f"👥 Total referrals: {referrals_count}\n\n"
        f"🔗 Your referral link:\n{referral_link}\n\n"
        "Invite your friends using this link. When they register Gmail accounts, you'll earn rewards!"
    )

    conn.close()
    await update.message.reply_text(message, reply_markup=reply_markup)

# Handle Settings
async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    settings_message = (
        "Settings:\n\n"
        "1. Configure notifications\n"
        "2. Set up payment method\n"
        "3. Change language\n\n"
        "Choose the setting you want to configure."
    )
    await update.message.reply_text(settings_message, reply_markup=reply_markup)

# Handle Help
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_message = (
        "Help:\n\n"
        "1. Register a Gmail account using the generated credentials to earn money.\n"
        "2. Check 'My Accounts' to see your registered Gmail accounts.\n"
        "3. View your balance and referrals.\n"
        "4. Use settings to configure your preferences."
    )
    await update.message.reply_text(help_message, reply_markup=reply_markup)


async def payout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔁 Your payout request feature will be implemented here.")

async def balance_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📜 Balance history is not available yet. Stay tuned!")

async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Select an action from the menu list.", reply_markup=reply_markup)

# Main bot function (handles the Register New Gmail)
async def main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "📥 Register New Gmail":
        await register_gmail(update, context)
    elif update.message.text == "📂 My Accounts":
        await my_accounts(update, context)
    elif update.message.text == "💰 Balance":
        await balance(update, context)
    elif update.message.text == "👥 My Referrals":
        await my_referrals(update, context)
    elif update.message.text == "⚙️ Settings":
        await settings(update, context)
    elif update.message.text == "❓ Help":
        await help(update, context)
    else:
        await update.message.reply_text("You clicked a button. Choose one from the available options.", reply_markup=reply_markup)

if __name__ == "__main__":
    init_db()  # Initialize the database

    app = ApplicationBuilder().token("7471551826:AAF-73to8B8jPQpMx9wOvobL5vD6fun3foQ").build()

    app.add_handler(CommandHandler("start", start))
    # Setting up handlers
    app.add_handler(CallbackQueryHandler(done, pattern="^done_"))
    app.add_handler(CallbackQueryHandler(cancel, pattern="^cancel_"))
    app.add_handler(MessageHandler(filters.Text("📥 Register New Gmail"), main))
    app.add_handler(MessageHandler(filters.Text("📂 My Accounts"), main))
    app.add_handler(MessageHandler(filters.Text("💰 Balance"), main))
    app.add_handler(MessageHandler(filters.Text("👥 My Referrals"), main))
    app.add_handler(MessageHandler(filters.Text("⚙️ Settings"), main))
    app.add_handler(MessageHandler(filters.Text("❓ Help"), main))
    app.add_handler(MessageHandler(filters.Text("🏧 Payout"), payout))
    app.add_handler(MessageHandler(filters.Text("📜 Balance History"), balance_history))
    app.add_handler(MessageHandler(filters.Text("🔙 Back"), back))

    print("Bot is running...")
    app.run_polling()


    

