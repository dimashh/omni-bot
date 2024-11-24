import serpapi
import os
from dotenv import load_dotenv

load_dotenv()

client = serpapi.Client(api_key=os.getenv("SERP_API_KEY"))


def search_maps(query: str):
    try:
        return parse_response({})
        # response = client.search({
        #     'engine': 'google_maps',
        #     'type': 'search',
        #     "google_domain": "google.com",
        #     'q': query,
        #     'll': "@51.51331694865533, -0.13800987399427414, 14z",
        #     "hl": "en",
        #     "gl": "uk"
        # })
        # print(response)
        # if response['search_metadata']['status'] == 'Success':
        #     # take the top 3 results
        #     return parse_response(response['local_results'][:3])
        # else:
        #     return []
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
    # return results
    return [{'title': 'Black Sheep Coffee', 'type': 'Coffee shop', 'address': 'Unit 2, Kings Cross Square, Euston Rd., London N1C 4DE, United Kingdom', 'rating': 4.5, 'reviews': 624, 'price': None, 'hours': 'Closes soon ⋅ 10:30\u202fp.m. ⋅ Opens 5:45\u202fa.m. Sun', 'website': 'https://leavetheherdbehind.com/blogs/locations/kings-cross?utm_source=ExtNet&utm_medium=Yext', 'thumbnail': 'https://lh5.googleusercontent.com/p/AF1QipPtuDpWNU7jtZCxTqqPnh7ZcUQGqIeie5XhX36F=w80-h100-k-no'}, {'title': 'Starbucks Coffee', 'type': 'Coffee shop', 'address': 'Midland Rd, The Circle, London NW1 2QL, United Kingdom', 'rating': 3.9, 'reviews': 1313, 'price': None, 'hours': 'Open 24 hours', 'website': 'https://www.starbucks.co.uk/store-locator/12754', 'thumbnail': 'https://lh5.googleusercontent.com/p/AF1QipPDeK5RigBPg1q-602oxSZyhQ7MO8PyHon7ldox=w92-h92-k-no'}, {'title': 'Coffee Island', 'type': 'Coffee shop', 'address': "5 Upper St Martin's Ln, London, WC2H 9EA, United Kingdom", 'rating': 4.4, 'reviews': 1649, 'price': None, 'hours': 'Closed ⋅ Opens 9\u202fa.m. Sun', 'website': 'http://www.coffeeisland.co.uk/', 'thumbnail': 'https://lh5.googleusercontent.com/p/AF1QipNgpiG_g2GXkEoNaxD19lh6aOz4uYtKThgHBhGE=w80-h106-k-no'}, {'title': 'The Somers Town Coffee House', 'type': 'Coffee shop', 'address': '60 Chalton St, London, NW1 1HS, United Kingdom', 'rating': 4.2, 'reviews': 1934, 'price': None, 'hours': 'Closes soon ⋅ 11\u202fp.m. ⋅ Opens 10\u202fa.m. Sun', 'website': 'http://www.thesomerstowncoffeehouse.co.uk/', 'thumbnail': 'https://lh5.googleusercontent.com/p/AF1QipNKi1_ivVbJHHYn1bDKlqCNPUWmFh4wkkPUdKj2=w92-h92-k-no'}, {'title': 'Foundry Coffee', 'type': 'Coffee shop', 'address': '156 Blackfriars Rd, London, SE1 8EN, United Kingdom', 'rating': 4.9, 'reviews': 124, 'price': None, 'hours': 'Closed ⋅ Opens 8\u202fa.m. Mon', 'website': 'https://www.instagram.com/foundrycoffeese1/', 'thumbnail': 'https://lh5.googleusercontent.com/p/AF1QipMWaQeTbGy37-LOwFpHq9ODGVdBnLG1KqJ3VQCC=w80-h106-k-no'}]


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