"""
Script to download images and upload to Firebase Storage, then update news items
Run: python upload_news_images.py
"""
import firebase_admin
from firebase_admin import credentials, firestore, storage
import requests
import os
import tempfile
from datetime import datetime

# Initialize Firebase
cred = credentials.Certificate('musaffo-33cf5-firebase-adminsdk-fbsvc-9215754308.json')
try:
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'musaffo-33cf5.appspot.com'
    })
except ValueError:
    # Already initialized - need to delete and reinitialize with storage
    firebase_admin.delete_app(firebase_admin.get_app())
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'musaffo-33cf5.appspot.com'
    })

db = firestore.client()
bucket = storage.bucket()

# Image URLs to download (high quality eco/air quality related images)
image_sources = [
    {
        "name": "fog_city.jpg",
        "url": "https://images.unsplash.com/photo-1485236715568-ddc5ee6ca227?auto=format&fit=crop&w=1200&q=80",
        "description": "Foggy city - for fog/PM2.5 news"
    },
    {
        "name": "industrial_inspection.jpg",
        "url": "https://images.unsplash.com/photo-1611273426858-450d8e3c9fce?auto=format&fit=crop&w=1200&q=80",
        "description": "Industrial facility - for pollution control news"
    },
    {
        "name": "home_heating.jpg",
        "url": "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=1200&q=80",
        "description": "Home interior - for heating safety news"
    },
    {
        "name": "construction_site.jpg",
        "url": "https://images.unsplash.com/photo-1504307651254-35680f356dfd?auto=format&fit=crop&w=1200&q=80",
        "description": "Construction site - for construction pollution news"
    },
    {
        "name": "football_stadium.jpg",
        "url": "https://images.unsplash.com/photo-1574629810360-7efbbe195018?auto=format&fit=crop&w=1200&q=80",
        "description": "Football stadium - for FC Andijan news"
    },
    {
        "name": "foggy_weather.jpg",
        "url": "https://images.unsplash.com/photo-1534088568595-a066f410bcda?auto=format&fit=crop&w=1200&q=80",
        "description": "Foggy weather - for weather forecast news"
    },
    {
        "name": "smoggy_atmosphere.jpg",
        "url": "https://images.unsplash.com/photo-1532178910-7815d6919875?auto=format&fit=crop&w=1200&q=80",
        "description": "Smoggy atmosphere - for pollution accumulation news"
    }
]


def download_image(url: str) -> bytes:
    """Download image from URL and return bytes"""
    print(f"  Downloading from {url[:50]}...")
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.content


def upload_to_firebase(image_bytes: bytes, filename: str) -> str:
    """Upload image to Firebase Storage and return public URL"""
    blob = bucket.blob(f"news-images/{filename}")

    # Upload the image
    blob.upload_from_string(
        image_bytes,
        content_type='image/jpeg'
    )

    # Make the blob publicly accessible
    blob.make_public()

    print(f"  Uploaded to Firebase: {blob.public_url}")
    return blob.public_url


def update_news_with_firebase_urls():
    """Download images, upload to Firebase, and update news items"""

    # First, download and upload all images
    firebase_urls = []

    print("Step 1: Downloading and uploading images to Firebase Storage...")
    for i, img in enumerate(image_sources):
        print(f"\n[{i+1}/{len(image_sources)}] {img['name']}")
        try:
            # Download image
            image_bytes = download_image(img['url'])

            # Upload to Firebase
            firebase_url = upload_to_firebase(image_bytes, img['name'])
            firebase_urls.append(firebase_url)

        except Exception as e:
            print(f"  Error: {e}")
            firebase_urls.append(img['url'])  # Fallback to original URL

    print("\n\nStep 2: Updating news items in Firestore...")

    # Get all news items sorted by timestamp
    news_ref = db.collection('news').order_by('timestamp', direction=firestore.Query.DESCENDING)
    docs = list(news_ref.stream())

    if len(docs) != len(firebase_urls):
        print(f"Warning: {len(docs)} news items but {len(firebase_urls)} images")

    # Update each news item with corresponding Firebase URL
    for i, doc in enumerate(docs):
        if i < len(firebase_urls):
            news_data = doc.to_dict()
            old_url = news_data.get('imageUrl', '')
            new_url = firebase_urls[i]

            doc.reference.update({'imageUrl': new_url})
            print(f"  Updated news {i+1}: {news_data['translations']['ru']['title'][:40]}...")

    print(f"\n✅ Successfully updated {len(docs)} news items with Firebase Storage URLs!")


if __name__ == "__main__":
    update_news_with_firebase_urls()
