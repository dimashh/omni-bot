import time

from telegram import Update, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from uuid import uuid4
from model import get_model_response
from persistence.user_preference import USER_PREFERENCES
from logger import log
from search.maps import search_maps, format_recommendation
from search.flights import search_flights, format_trip_details
import json

LATEST_ITINERARY = ""

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


PREPROMPT_PLAN_TRIP = """
You are a professional trip planner. Your task is to create an optimized trip plan based on a group of individuals with specific preferences and requirements. Use the preferences provided to:

1. Plan a trip that satisfies as many of the group members' preferences as possible while considering:
   - Dietary requirements
   - Accessibility needs (e.g., wheelchair accessibility)
   - Individual wishlists
   - Budget constraints
   - Preferred travel dates

2. Ensure that the group can spend as much time together as possible. Staying in the same hotels, visiting the same attractions, and eating at the same places are ideal if they satisfy everyone's requirements.

3. Use each person's name (not their ID) to refer to them in the plan.

4. Format the response in **Telegram-friendly HTML**. Use only the following HTML tags:
   - `<b>` for bold text
   - `<i>` for italic text

### Example Format:
✈️ <b>Trip Plan</b>\n
<i>Destination:</i> London\n
<i>Group Members:</i> Dimash, German\n
\n
<b>Day 1</b>\n
...
<b>Day 2</b>\n
...
💵 <i>Total Estimated Cost Per Person:</i> 800 pounds\n
🌱 <i>Dietary Requirements Considered:</i> Vegan-friendly options\n
♿ <i>Accessibility:</i> Fully wheelchair accessible\n

Now, process the following `USER_PREFERENCES` to create a group trip plan. Be concise, ensure clarity, and include personalized elements for each traveler where needed.
Do NOT include **text** or *text* format in the response. Just use the HTML tags mentioned above.

USER_PREFERENCES:
"""

SUMMARIZE_TRIP_TEXT = """
You are given a JSON object with multiple users' trip preferences. Summarize each user's preferences in a structured format. Mention their name and include details about the destination, budget, dates, and any preferences they have. Format the response cleanly for direct messaging.

Example:
Input: {867633191: '(name: German) I want to go to London. I am in Madrid. I want December 5th to 8th. Budget 1000. Wheelchair accessibility', 463557933: '(name: Dimash) I want to go to London. I am based in Astana. I have 7 days for the trip, from 5th December. My budget is 800 pounds. I can only eat vegan food'}

Output:
Thank you all! Here's what you've shared:

Name: Dimash
City/Destination: London
Budget: 800 pounds
Dates: 5th December to 12th December
Preferences: Vegan food
We'll use this information to plan your trip!

Name: German
City/Destination: London
Budget: 1000 pounds
Dates: 5th December to 8th December
Preferences: Wheelchair accessibility
We'll use this information to plan your trip!

YOU MUST NOT include **text** or *text* format in the response. Just plain text.

Now, process the following JSON and provide the output in the same format:

{input_json}
"""

PREFERENCES, PLAN_TRIP, LOCATION, BIO = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log.info("Called start")

    await update.message.reply_text(
        START_TEXT
    )

    return PREFERENCES

async def itinerary_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    global LATEST_ITINERARY

    log.info("Itinerary handler")
    if query.data == "latest_itinerary":
        log.info("Sending latest itinerary")
        latest = LATEST_ITINERARY if LATEST_ITINERARY != "" else ITINERARY_TEXT

        keyboard = [
            [InlineKeyboardButton("Latest Itinerary", callback_data="latest_itinerary")],
            [InlineKeyboardButton("Recommend Restaraunts", callback_data="recommend")],
            [InlineKeyboardButton("Check flights", callback_data="flights")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=latest,
            parse_mode='HTML',
            reply_markup=reply_markup
        )

    if query.data == "plan_trip":
        log.info("Planning trip")
        user_preferences = json.dumps(USER_PREFERENCES)
        prompt = "".join([PREPROMPT_PLAN_TRIP, user_preferences])

        response = get_model_response(prompt)
        log.info("got response from model", response)

        LATEST_ITINERARY = response

        keyboard = [
            [InlineKeyboardButton("Latest Itinerary", callback_data="latest_itinerary")],
            [InlineKeyboardButton("Recommend Restaraunts", callback_data="recommend")],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=response,
            parse_mode='HTML',
            reply_markup=reply_markup
        )

    if query.data == "recommend":
        log.info("Recommending")
        response = search_maps("wheelchair access restaurant")

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

    if query.data == "flights":
        response = search_flights("HND", "LHR", "2024-12-12")
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

async def summarise_trip_from_store(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log.info("Starting to summarize trip preferences...")
    log.info(f"Current user preferences: {USER_PREFERENCES}")

    try:
        # Prepare the JSON input
        input_json = json.dumps(USER_PREFERENCES)
        log.info(f"Input JSON: {input_json}")

        # Combine prompt and JSON
        prompt = "".join([SUMMARIZE_TRIP_TEXT, input_json])
        log.info(f"Prompt: {prompt}")

        # Get response from the model
        response = get_model_response(prompt)
        log.info(f"Received response: {response}")

        keyboard = [
            [InlineKeyboardButton("Plan Trip", callback_data="plan_trip")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        # Send the response to the user
        await update.message.reply_text(
            response.strip(),
            parse_mode="HTML",
            reply_markup=reply_markup
        )
    except Exception as e:
        log.error(f"Error processing trip summary: {e}")
        await update.message.reply_text(
            "Sorry, there was an error generating the trip summary. Please try again later."
        )


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

