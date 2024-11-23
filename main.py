from fastapi import FastAPI
from dotenv import load_dotenv
import os
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, InlineQueryHandler, ConversationHandler

import model
from bot.main import start, echo, caps, inline_caps, unknown, summarize, talk, collect_user_preference, plan_trip_from_store, cancel, PREFERENCES, PLAN_TRIP
import logger

load_dotenv()

app = FastAPI()

application = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

# summarize_handler = CommandHandler('summarize', summarize)
# talk_handler = CommandHandler('talk', talk)

# start_handler = CommandHandler('start', start)
# echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
# echo_handler = CommandHandler('echo', echo)
# inline_caps_handler = InlineQueryHandler(inline_caps)
# unknown_handler = MessageHandler(filters.COMMAND, unknown)


conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        PREFERENCES: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_user_preference), CommandHandler("plan_trip", plan_trip_from_store)],
        PLAN_TRIP: [],
        # LOCATION: [
        #     MessageHandler(filters.LOCATION, location),
        #     CommandHandler("skip", skip_location),
        # ],
        # BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, bio)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    per_chat=True, 
    per_user=False, 
    per_message=False
)

application.add_handler(conv_handler)
# application.add_handler(summarize_handler)
# application.add_handler(talk_handler)

application.run_polling(allowed_updates=Update.ALL_TYPES)
