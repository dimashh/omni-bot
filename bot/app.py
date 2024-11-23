from telegram import Update
from telegram.ext import ContextTypes

user_data = {}


async def start_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    # Initialize the user's data storage
    user_data[user_id] = {}

    # Start asking for information
    await update.message.reply_text(
        "Let's collect your preferences. First, which city or destination are you planning to visit?"
    )
    context.user_data['current_step'] = 'city'


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_step = context.user_data.get('current_step')

    if current_step == 'city':
        user_data[user_id]['city'] = update.message.text
        context.user_data['current_step'] = 'budget'
        await update.message.reply_text("Got it! What's your budget for the trip?")

    elif current_step == 'budget':
        user_data[user_id]['budget'] = update.message.text
        context.user_data['current_step'] = 'dates'
        await update.message.reply_text("What are your preferred travel dates? (e.g., 2023-12-20 to 2023-12-25)")

    elif current_step == 'dates':
        user_data[user_id]['dates'] = update.message.text
        context.user_data['current_step'] = 'preferences'
        await update.message.reply_text(
            "Any other preferences? (e.g., diet preferences, wheelchair access, wishlist)"
        )

    elif current_step == 'preferences':
        user_data[user_id]['preferences'] = update.message.text
        context.user_data['current_step'] = None

        print(user_data)
        await update.message.reply_text(
            "Thanks! Here's what you've shared:\n\n"
            f"City/Destination: {user_data[user_id]['city']}\n"
            f"Budget: {user_data[user_id]['budget']}\n"
            f"Dates: {user_data[user_id]['dates']}\n"
            f"Preferences: {user_data[user_id]['preferences']}\n"
            "We'll use this information to plan your trip!"
        )