from telegram import Update, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from uuid import uuid4
from model import get_model_response
from persistence.user_preference import USER_PREFERENCES
from logger import log
from search.maps import search_maps, format_recommendation
from search.flights import search_flights, format_trip_details
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

ITINERARY_TEXT = """
<b>Day 1-4: London (for Germán)</b>
<strong>Germán's Itinerary:</strong>
• <b>Day 1 (December 4):</b> Arrival in London from Madrid. Check-in at a halal-friendly hotel like the Stern Hotel or Royal National Hotel.
• <b>Day 2 (December 5):</b> Visit iconic landmarks such as the British Museum and the Tower of London. Lunch at halal restaurants like The Yum Yum Tree or Halal Gourmet Kitchen.
• <b>Day 3 (December 6):</b> Explore the London Eye, Westminster Abbey, and Buckingham Palace. Have lunch at a halal restaurant like The Halal Guys or The Real Greek.
• <b>Day 4 (December 7):</b> Stroll through Hyde Park and visit the Victoria and Albert Museum. Enjoy a halal meal at The Halal Butcher or Maroush.

<b>Day 5-7: London (for Dimash)</b>
<strong>Dimash's Itinerary:</strong>
• <b>Day 5 (December 5):</b> Arrival in London from Astana. Check-in at a vegan-friendly hotel like The Hoxton or The Zetter Townhouse Marylebone.
• <b>Day 6 (December 6):</b> Visit the Natural History Museum and the Science Museum. Lunch at vegan restaurants like By CHLOE or Mildreds.
• <b>Day 7 (December 7):</b> Explore Camden Market for vegan street food and unique shops. In the evening, catch a show in the West End.

<b>Combined Day: London (for both)</b>
<strong>Shared Day (December 8):</strong>
• Both Germán and Dimash can meet in the morning and explore Hyde Park together. They can visit the Serpentine Lake and enjoy a vegan-friendly picnic with halal options available.
• In the afternoon, they can visit the Platform 9 ¾ at King's Cross Station and take a stroll through Covent Garden.

<b>Dietary Considerations:</b>
• <strong>Germán:</strong> Halal restaurants are plentiful in London, especially around areas like Brixton, Camden, and Southwark.
• <strong>Dimash:</strong> Vegan restaurants are abundant in London. Popular vegan areas include Camden, Shoreditch, and Brixton.

<b>Accessibility:</b>
• Both Germán and Dimash should ensure their hotels and attractions are wheelchair accessible. London has good public transportation with many wheelchair-accessible options.

<b>Budget Considerations:</b>
<strong>Germán's Budget:</strong>
• Accommodation: Approximately 250 pounds (62.5 pounds/night)
• Food: Approximately 200 pounds (50 pounds/day)
• Attractions: Approximately 300 pounds (75 pounds/day)
• Transportation: Approximately 250 pounds

<strong>Dimash's Budget:</strong>
• Accommodation: Approximately 240 pounds (34.3 pounds/night)
• Food: Approximately 200 pounds (28.6 pounds/day)
• Attractions: Approximately 300 pounds (42.9 pounds/day)
• Transportation: Approximately 60 pounds

<b>Wishlists:</b>
• <strong>Germán:</strong> Halal food, iconic landmarks, museums.
• <strong>Dimash:</strong> Vegan food, museums, unique shopping experiences.
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

    keyboard = [
        [InlineKeyboardButton("Latest Itinerary", callback_data="latest_itinerary")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        START_TEXT,
        reply_markup=reply_markup
    )

    return PREFERENCES

async def itinerary_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "latest_itinerary":
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=ITINERARY_TEXT,
            parse_mode='HTML'
        )

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


async def recommend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = ' '.join(context.args)
    # soho, london
    response = search_maps(user_text)

    if response:
        # Store restaurant names for the poll
        recommendation_names = []

        for place in response:
            formatted_message = format_recommendation(place)
            recommendation_names.append(place.get("title", "Unknown"))

            if "thumbnail" in place and place["thumbnail"]:
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=place["thumbnail"],
                    caption=formatted_message,
                    parse_mode="HTML"
                )
            else:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=formatted_message,
                    parse_mode="HTML"
                )

        # Create a poll with the restaurant names
        if recommendation_names:
            await context.bot.send_poll(
                chat_id=update.effective_chat.id,
                question="Which option do you prefer?",
                options=recommendation_names,
                is_anonymous=False,
                allows_multiple_answers=True,
            )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Sorry, no recommendations found.",
        )


async def flights(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = search_flights("LHR", "HND", "2024-12-12")
    print('response:', response)

    if response:
        for trip in response:
            formatted_message = format_trip_details(trip)
            print('formatted_message:', formatted_message)

            first_flight_logo = trip["flights"][0].get("logo", None)
            if first_flight_logo:
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=first_flight_logo
                )

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=formatted_message,
                parse_mode="HTML"
            )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Sorry, no flights found for your query."
        )
