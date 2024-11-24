# WanderWise
WanderWise is a personal travel assistant bot designed to help users plan their trips. The bot assists users through every stage of their travel planning, including finding flights, recommending restaurants, and creating detailed itineraries based on user preferences.

# Features
Trip Planning: Users can input their travel preferences, including dates, budget, dietary restrictions, and accessibility needs. The bot generates a detailed itinerary that satisfies as many preferences as possible.
Flight Search: The bot can search for flights between specified destinations and dates, providing detailed information about each flight, including duration, airline, and carbon emissions.
Restaurant Recommendations: The bot can recommend restaurants based on user preferences, such as wheelchair accessibility or dietary restrictions.
Itinerary Management: Users can view and update their latest itinerary, ensuring they have the most up-to-date travel plans.
ESG Score: The bot provides an ESG (Environmental, Social, and Governance) score for the trip, helping users make more sustainable travel choices.

# Technologies Used
Python: The main programming language used for the bot.
Telegram Bot API: For interacting with users through Telegram.
SerpAPI: For searching flights and other travel-related information.
dotenv: For managing environment variables.
Logging: For tracking bot activities and debugging.

# Setup
- python3 -m venv omni-bot
- source omni-bot/bin/activate
- pip3 install -r requirements.txt
- Create a .env file in the root directory and add the following environment variables
- - TELEGRAM_BOT_TOKEN=your_telegram_bot_token
- - MISTRAL_API_KEY=your_mistral_api_key
- - SERP_API_KEY=your_serp_api_key

# Run the app
- python main.py
- Open Telegram and search for the bot using the username provided by BotFather
- Start interacting with the bot
- /start to initiate the conversation
- /summarize to get a summary of the user preferences
- Use the inline keyboard to interact with the bot