import logging
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ContextTypes, ConversationHandler
from uuid import uuid4
from model import get_model_response
from persistence.user_preference import USER_PREFERENCES
from logger import log
import json


START_TEXT = """
Hi, I am Finna the OmniBot, your personal travel assistant!

Today we are going to plan your next trip. I will assist you through every stage of the way.

Each traveler in the group, please tell me:
1. When do you want to go?
2. Where are you travelling from?
3. Where do you want to go for your next trip?
4. What is your budget?
5. Any other preferences? (dietary restrictions, wheelchair access, wishlist)
"""

PREPROMPT_PLAN_TRIP = """You are a professional trip planner. You are planning a trip for a group of people with each having their individual needs and preferences.
Create the most optimal trip that would satisfy the group and consider any sort of dietary requirements, accessability, such as wheelchair, wishlists and other other preferences.
Make sure everyone on the trip can spend as much time together as possible. Staying in same hotels and eating in the same places would be ideal given they satisfy all the combined requirements.
Use name to refer to the traveler, not id.
Do not use variables in your responses (like USER_PREFERENCES).

I am going to provide you USER_PREFERENCES (preferences of each traveller) consisting of:
* prefered travel dates
* starting location
* prefered destination
* other preferences and restrictions (dietary, accessability, wishlists, etc.)

USER_PREFERENCES:
"""


# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await context.bot.send_message(chat_id=update.effective_chat.id, text=START_TEXT)


### General ###

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_caps = ' '.join(context.args).upper()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)

async def inline_caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    if not query:
        return
    results = []
    results.append(
        InlineQueryResultArticle(
            id=str(uuid4()),
            title='Caps',
            input_message_content=InputTextMessageContent(query.upper())
        )
    )
    await context.bot.answer_inline_query(update.inline_query.id, results)

async def summarize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = ' '.join(context.args)
    preprompt = "Summarize the text below: \n\n"
    
    summary = get_model_response(''.join([preprompt, user_text]))
    await context.bot.send_message(chat_id=update.effective_chat.id, text=summary)

async def talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = ' '.join(context.args)    
    summary = get_model_response(user_text)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=summary)


### Conversation ###

PREFERENCES, PLAN_TRIP, LOCATION, BIO = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log.info("Called start")

    await update.message.reply_text(
        START_TEXT,
    )

    return PREFERENCES

async def collect_user_preference(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log.info("Preference: ")
    log.info(USER_PREFERENCES)
    log.info("Update: ")
    log.info(update)
    log.info("Context: ")
    log.info(context)

    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    user_text = update.message.text

    USER_PREFERENCES[user_id] = f"(name: {user_name}) {user_text}"
    
async def plan_trip_from_store(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log.info("planning trip")
    log.info(USER_PREFERENCES)

    user_preferences = json.dumps(USER_PREFERENCES)
    prompt = "".join([PREPROMPT_PLAN_TRIP, user_preferences])

    response = get_model_response(prompt)
    log.info("got response from model")

    await update.message.reply_text(
        response
    )

    return PLAN_TRIP
    

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    log.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.",
    )

    return ConversationHandler.END


### Other ###

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")