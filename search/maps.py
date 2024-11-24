import serpapi
import os
from dotenv import load_dotenv

load_dotenv()

client = serpapi.Client(api_key=os.getenv("SERP_API_KEY"))


def search_maps(query: str):
    try:
        response = client.search({
            'engine': 'google_maps',
            'type': 'search',
            "google_domain": "google.com",
            'q': query,
            'll': "@51.51331694865533, -0.13800987399427414, 14z",
            "hl": "en",
            "gl": "uk"
        })
        print(response)
        if response['search_metadata']['status'] == 'Success':
            # take the top 3 results
            return parse_response(response['local_results'][:3])
        else:
            return []
    except Exception as e:
        raise e


def parse_response(response: dict):
    results = []
    for result in response:
        results.append({
            "title": result['title'] if 'title' in result else None,
            "type": result['type'] if 'type' in result else None,
            "address": result['address'] if 'address' in result else None,
            "rating": result['rating'] if 'rating' in result else None,
            "reviews": result['reviews'] if 'reviews' in result else None,
            "price": result['price'] if 'price' in result else None,
            "hours": result['hours'] if 'hours' in result else None,
            "website": result['website'] if 'website' in result else None,
            "thumbnail": result['thumbnail'] if 'thumbnail' in result else None,
        })
    print(results)
    return results


def format_recommendation(place):
    """Format the place details into a nicely formatted HTML message."""
    title = place.get("title", "Unknown")
    type_ = place.get("type", "Unknown type")
    address = place.get("address", "No address provided")
    rating = place.get("rating", "N/A")
    reviews = place.get("reviews", 0)
    price = place.get("price", "N/A")
    hours = place.get("hours", "Hours not available")
    website = place.get("website", "#")

    return (
        f"<b>{title}</b> ({type_})\n"
        f"<i>Rating:</i> {rating} ⭐ ({reviews} reviews)\n"
        f"<i>Price:</i> {price}\n"
        f"<i>Hours:</i> {hours}\n"
        f"<i>Address:</i> {address}\n"
        f'<a href="{website}">Website</a>'
    )