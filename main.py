from fastapi import FastAPI
from dotenv import load_dotenv
import os
from telegram import Update, BotCommand
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, InlineQueryHandler, ConversationHandler, CallbackQueryHandler

from bot.app import start_info, handle_message
from bot.main import start, collect_user_preference, \
 cancel, PREFERENCES, PLAN_TRIP, itinerary_handler, flights, \
    summarise_trip_from_store
import logger

load_dotenv()

app = FastAPI()

application = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

application.add_handler(CallbackQueryHandler(itinerary_handler))

flights_handler = CommandHandler('flights', flights)
application.add_handler(flights_handler)


conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        PREFERENCES: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, collect_user_preference),
            # CommandHandler("plan_trip", plan_trip_from_store),
            CommandHandler("summarize", summarise_trip_from_store)
        ],
        PLAN_TRIP: [],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    per_chat=True,
    per_user=False,
    per_message=False
)

application.add_handler(conv_handler)
application.run_polling(allowed_updates=Update.ALL_TYPES)
