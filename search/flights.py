import re

import serpapi
import os
from dotenv import load_dotenv

load_dotenv()

client = serpapi.Client(api_key=os.getenv("SERP_API_KEY"))


def search_flights(from_destination: str, to_destination, date: str):
    try:
        response = client.search({
            "engine": "google_flights",
            "hl": "en",
            "gl": "gb",
            "departure_id": from_destination,
            "arrival_id": to_destination,
            "outbound_date": date,
            "currency": "GBP",
            "adults": "1",
            "type": "2"
        })
        if response['search_metadata']['status'] == 'Success':
            # take the top 3 results
            return parse_flights(response['best_flights'][:3])
        else:
            return []
    except Exception as e:
        raise e


def parse_flights(response: list):
    """Parse the search_flights response."""
    parsed_trips = []

    for trip in response:
        flights = []
        for flight in trip.get("flights", []):
            # Parse extensions for carbon emission
            if 'extensions' in flight and isinstance(flight['extensions'], list):
                extensions = " ".join(flight['extensions'])
                match = re.search(r"Carbon emissions estimate: (\d+ kg)", extensions)
                carbon_emission = match.group(1) if match else "N/A"
            else:
                carbon_emission = "N/A"

            # Append parsed flight details
            flights.append({
                "departure_airport": flight.get("departure_airport", {}).get("name", "Unknown"),
                "departure_code": flight.get("departure_airport", {}).get("id", "Unknown"),
                "departure_time": flight.get("departure_airport", {}).get("time", "Unknown"),
                "arrival_airport": flight.get("arrival_airport", {}).get("name", "Unknown"),
                "arrival_code": flight.get("arrival_airport", {}).get("id", "Unknown"),
                "arrival_time": flight.get("arrival_airport", {}).get("time", "Unknown"),
                "duration": flight.get("duration", "N/A"),
                "airline": flight.get("airline", "Unknown"),
                "logo": flight.get("airline_logo", ""),
                "travel_class": flight.get("travel_class", "Unknown"),
                "flight_number": flight.get("flight_number", "N/A"),
                "legroom": flight.get("legroom", "N/A"),
                "carbon_emission": carbon_emission,
                "often_delayed": flight.get("often_delayed_by_over_30_min", False),
            })

        # Parse top-level trip details
        parsed_trips.append({
            "price": trip.get("price", "N/A"),
            "total_duration": trip.get("total_duration", "N/A"),
            "layovers": [
                {
                    "name": layover.get("name", "Unknown"),
                    "duration": layover.get("duration", "N/A"),
                    "overnight": layover.get("overnight", False)
                }
                for layover in trip.get("layovers", [])
            ],
            "flights": flights
        })

    return parsed_trips


def format_trip_details(trip):
    """Format a single trip's details."""
    flights = trip["flights"]
    price = trip["price"]
    total_duration = trip["total_duration"]
    layovers = trip["layovers"]

    # Format total duration
    hours, minutes = divmod(total_duration, 60)
    total_duration_formatted = f"{hours}h {minutes}m"

    # Top-level trip summary
    message = (
        f"✈️ <b>Trip Summary</b>\n"
        f"💵 <i>Price:</i> ${price}\n"
        f"⏱️ <i>Total Duration:</i> {total_duration_formatted}\n"
    )

    # Add layovers
    if layovers:
        message += "<i>Layovers:</i>\n"
        for layover in layovers:
            duration = layover["duration"]
            hours, minutes = divmod(duration, 60)
            layover_duration = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
            overnight = " (Overnight)" if layover.get("overnight") else ""
            message += f" - {layover['name']} ({layover_duration}{overnight})\n"

        # Add detailed flight segments
    for i, flight in enumerate(flights, 1):
        duration = flight["duration"]
        hours, minutes = divmod(duration, 60)
        flight_duration = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
        delayed = "⚠️ Delayed Often" if flight.get("often_delayed") else "✅ On-Time"

        message += (
            f"\n<b>Flight {i}</b> ({flight['airline']})\n"
            f"🛫 <i>From:</i> {flight['departure_code']} ({flight['departure_time']})\n"
            f"🛬 <i>To:</i> {flight['arrival_code']} ({flight['arrival_time']})\n"
            f"⏱️ <i>Duration:</i> {flight_duration}\n"
            f"💺 <i>Class:</i> {flight['travel_class']}\n"
            f"📏 <i>Legroom:</i> {flight['legroom']}\n"
            f"🌱 <i>Carbon Emission:</i> {flight['carbon_emission']}\n"
            f"{delayed}\n"
        )

    return message

