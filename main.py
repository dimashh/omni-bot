from fastapi import FastAPI
from dotenv import load_dotenv
import os
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, InlineQueryHandler

import model
from bot.main import start, echo, caps, inline_caps, unknown

load_dotenv()

app = FastAPI()

application = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

start_handler = CommandHandler('start', start)
echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
caps_handler = CommandHandler('caps', caps)
inline_caps_handler = InlineQueryHandler(inline_caps)
unknown_handler = MessageHandler(filters.COMMAND, unknown)

application.add_handler(start_handler)
application.add_handler(echo_handler)
application.add_handler(caps_handler)
application.add_handler(inline_caps_handler)
application.add_handler(unknown_handler)

application.run_polling()
