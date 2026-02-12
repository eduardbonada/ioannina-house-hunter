"""
Gartzonikas Home scraper
Website: https://gartzonikashome.com
Note: This site requires JavaScript rendering (Houzez theme)
"""

import hashlib
import re
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


def scrape_gartzonikas(url):
    """
    Scrape listings from Gartzonikas Home website using Selenium

    Args:
        url: The search URL with filters applied

    Returns:
        List of listing dictionaries
    """
    listings = []

    try:
        # Set up Selenium with Chrome in headless mode
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)

        # Wait for listings to load
        print("   Waiting for page to load...")
        time.sleep(4)  # Give time for initial load and JavaScript

        # Wait for property listing items to appear (Houzez theme uses various patterns)
        try:
            # Try common Houzez class names
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".item-listing-wrap, .property-item, article.item-listing, .listing-item"))
            )
            time.sleep(2)  # Additional wait for content to populate
        except Exception as e:
            print(f"   ⚠️  Timeout waiting for listings: {e}")

        # Get the rendered HTML
        html = driver.page_source
        driver.quit()

        # Parse with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        # Find all listing items (try multiple patterns)
        property_cards = (
            soup.find_all('article', class_=re.compile(r'item-listing')) or
            soup.find_all('div', class_=re.compile(r'property-item')) or
            soup.find_all('div', class_=re.compile(r'item-listing-wrap'))
        )

        print(f"   Found {len(property_cards)} property cards")

        for card in property_cards:
            try:
                listing = extract_listing_data(card)
                if listing and listing.get('url'):
                    listings.append(listing)
            except Exception as e:
                print(f"   ⚠️  Error extracting listing: {e}")
                continue

    except Exception as e:
        print(f"   ❌ Selenium error: {e}")
        print(f"   Make sure Chrome and chromedriver are installed")
        raise

    return listings


def extract_listing_data(card):
    """
    Extract data from a single listing card (Houzez theme)

    Args:
        card: BeautifulSoup element containing listing

    Returns:
        Dictionary with listing data
    """
    listing = {}

    # Extract URL - try multiple patterns
    link = (
        card.find('a', class_=re.compile(r'listing-link|property-link')) or
        card.find('h2', class_='item-title').find('a') if card.find('h2', class_='item-title') else None or
        card.find('a', href=re.compile(r'/property/|/ακίνητα/'))
    )

    if link and link.get('href'):
        url = link['href']
        if url.startswith('/'):
            url = 'https://gartzonikashome.com' + url
        elif not url.startswith('http'):
            url = 'https://gartzonikashome.com/' + url
        listing['url'] = url
        listing['property_id'] = extract_property_id(url)
    else:
        return None

    # Extract first photo URL
    photo_url = None
    img_elem = card.find('img', src=True)
    if img_elem:
        photo_url = img_elem.get('src') or img_elem.get('data-src')
        # Handle relative URLs
        if photo_url and not photo_url.startswith('http'):
            if photo_url.startswith('/'):
                photo_url = 'https://gartzonikashome.com' + photo_url
            else:
                photo_url = 'https://gartzonikashome.com/' + photo_url
    listing['photo_url'] = photo_url

    # Extract title/location
    title_elem = (
        card.find('h2', class_='item-title') or
        card.find('h3', class_='item-title') or
        card.find(class_=re.compile(r'property-title|item-title'))
    )
    if title_elem:
        listing['title'] = title_elem.get_text(strip=True)
        listing['location'] = listing['title']  # Will refine below if address found
    else:
        listing['title'] = 'Unknown'
        listing['location'] = 'Unknown'

    # Extract address/location
    address_elem = (
        card.find('address', class_='item-address') or
        card.find('div', class_='item-address') or
        card.find(class_=re.compile(r'property-address|item-address'))
    )
    if address_elem:
        location_text = address_elem.get_text(strip=True)
        if location_text:
            listing['location'] = location_text

    # Extract price
    price_elem = (
        card.find('li', class_='item-price') or
        card.find('span', class_='item-price') or
        card.find(class_=re.compile(r'property-price|item-price'))
    )
    if price_elem:
        price_text = price_elem.get_text(strip=True)
        listing['price'] = parse_price(price_text)
    else:
        listing['price'] = None

    # Extract property details (size, bedrooms, bathrooms, etc.)
    details_list = card.find('ul', class_=re.compile(r'item-amenities|property-meta'))

    # Initialize defaults
    listing['size_sqm'] = None
    listing['bedrooms'] = None
    listing['bathrooms'] = None
    listing['parking'] = None
    listing['property_type'] = 'Unknown'

    if details_list:
        for li in details_list.find_all('li'):
            text = li.get_text(strip=True).lower()

            # Size/area
            if 'τ.μ' in text or 'm²' in text or 'sqm' in text:
                size_match = re.search(r'(\d+)', text)
                if size_match:
                    listing['size_sqm'] = int(size_match.group(1))

            # Bedrooms
            elif 'υπνοδωμάτι' in text or 'bedroom' in text or 'bed' in text:
                bed_match = re.search(r'(\d+)', text)
                if bed_match:
                    listing['bedrooms'] = int(bed_match.group(1))

            # Bathrooms
            elif 'μπάνι' in text or 'bathroom' in text or 'bath' in text:
                bath_match = re.search(r'(\d+)', text)
                if bath_match:
                    listing['bathrooms'] = int(bath_match.group(1))

            # Parking/garage
            elif 'parking' in text or 'garage' in text or 'θέσ' in text:
                park_match = re.search(r'(\d+)', text)
                if park_match:
                    listing['parking'] = int(park_match.group(1))
                else:
                    listing['parking'] = 1  # If mentioned but no number, assume at least 1

    # Extract property type from labels or status
    labels_div = card.find('div', class_=re.compile(r'labels|status'))
    if labels_div:
        label_text = labels_div.get_text(strip=True)
        if 'διαμέρισμα' in label_text.lower() or 'apartment' in label_text.lower():
            listing['property_type'] = 'Διαμέρισμα'
        elif 'μεζονέτα' in label_text.lower() or 'maisonette' in label_text.lower():
            listing['property_type'] = 'Μεζονέτα'

    # Extract full description/content
    content_div = card.find('div', class_=re.compile(r'item-body|property-content'))
    if content_div:
        listing['description'] = content_div.get_text(' ', strip=True)
    else:
        listing['description'] = listing.get('title', '')

    # Generate unique hash for this listing
    listing['hash'] = generate_listing_hash(listing)

    # Add timestamps
    listing['first_seen'] = datetime.now().strftime('%Y-%m-%d')
    listing['last_checked'] = datetime.now().strftime('%Y-%m-%d')

    return listing


def extract_property_id(url):
    """Extract property ID from URL"""
    patterns = [
        r'/property/([^/]+)',
        r'/ακίνητα/([^/]+)',
        r'/(\d+)/?$',
        r'property_id=(\d+)',
        r'/el/([^/]+)/?$'
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    # If no ID found, generate from URL hash
    return hashlib.md5(url.encode()).hexdigest()[:8]


def parse_price(text):
    """Parse price from text like '250.000 €' or '€250,000'"""
    # Remove € symbol, spaces, dots and commas used as separators
    text = text.replace('€', '').replace(' ', '').replace('.', '').replace(',', '')

    # Extract digits
    match = re.search(r'(\d+)', text)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return None
    return None


def generate_listing_hash(listing):
    """Generate unique hash for listing based on URL and property ID only"""
    # Don't include price in hash - we want to detect price changes
    hash_string = f"{listing.get('url', '')}_{listing.get('property_id', '')}"
    return hashlib.md5(hash_string.encode()).hexdigest()
