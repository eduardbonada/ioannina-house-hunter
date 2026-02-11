"""
Oikia Real Estate scraper
Website: https://oikiarealestate.gr
Note: This site requires JavaScript rendering
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


def scrape_oikia(url, max_pages=10):
    """
    Scrape listings from Oikia Real Estate website using Selenium
    Handles pagination to get all available listings

    Args:
        url: The search URL with filters applied
        max_pages: Maximum number of pages to scrape (default 10)

    Returns:
        List of listing dictionaries
    """
    all_listings = []

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

        # Scrape first page
        print(f"   Scraping Oikia...")
        driver.get(url)

        # Wait for property listings to load
        time.sleep(7)  # Give time for JavaScript to load

        # Get the rendered HTML
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # Find all property listings
        # Oikia uses WPL plugin which typically has specific classes
        property_cards = soup.find_all('div', class_=lambda x: x and ('wpl-property' in x or 'property-listing' in x or 'wpl_prp_cont' in x))

        if not property_cards:
            # Try alternative selectors
            property_cards = soup.find_all('article', class_=lambda x: x and 'property' in str(x).lower())

        if not property_cards:
            # Try finding by any article or div that might contain properties
            property_cards = soup.find_all(['article', 'div'], class_=re.compile(r'property|listing|item', re.I))

        print(f"   Found {len(property_cards)} listings on Oikia")

        # Extract listings from current page
        for card in property_cards:
            try:
                listing = extract_listing_data(card)
                if listing and listing.get('url'):
                    all_listings.append(listing)
            except Exception as e:
                print(f"   ⚠️  Error extracting listing: {e}")
                continue

        driver.quit()
        print(f"   Total listings scraped from Oikia: {len(all_listings)}")

    except Exception as e:
        print(f"   ❌ Selenium error: {e}")
        print(f"   Make sure Chrome and chromedriver are installed")
        raise

    return all_listings


def extract_listing_data(card):
    """
    Extract data from a single listing card

    Args:
        card: BeautifulSoup element containing listing

    Returns:
        Dictionary with listing data
    """
    listing = {}

    # Extract URL
    link = card.find('a', href=True)
    if link and link.get('href'):
        url = link['href']
        if not url.startswith('http'):
            url = 'https://oikiarealestate.gr' + url
        listing['url'] = url

        # Extract property ID from URL
        id_match = re.search(r'/([^/]+)/?$', url)
        if id_match:
            listing['property_id'] = id_match.group(1)
        else:
            listing['property_id'] = hashlib.md5(url.encode()).hexdigest()[:8]
    else:
        return None

    # Extract photo URL
    img = card.find('img', src=True)
    if img:
        photo_url = img['src']
        if photo_url and not photo_url.startswith('http') and not photo_url.startswith('data:'):
            if photo_url.startswith('/'):
                photo_url = 'https://oikiarealestate.gr' + photo_url
            else:
                photo_url = 'https://oikiarealestate.gr/' + photo_url
        listing['photo_url'] = photo_url
    else:
        listing['photo_url'] = None

    # Extract title
    title_elem = card.find(['h2', 'h3', 'h4'], class_=lambda x: x and ('title' in str(x).lower() or 'property' in str(x).lower()))
    if not title_elem:
        title_elem = card.find(['h2', 'h3', 'h4'])

    if title_elem:
        listing['title'] = title_elem.get_text(strip=True)
    else:
        listing['title'] = ''

    # Extract property type from title or specific field
    property_type_elem = card.find(class_=re.compile(r'property.?type|category', re.I))
    if property_type_elem:
        listing['property_type'] = property_type_elem.get_text(strip=True)
    elif listing['title']:
        # Try to extract from title
        type_match = re.match(r'^([Α-Ωα-ωA-Za-z/\s]+)', listing['title'])
        if type_match:
            listing['property_type'] = type_match.group(1).strip()
        else:
            listing['property_type'] = 'Unknown'
    else:
        listing['property_type'] = 'Unknown'

    # Extract location
    location_elem = card.find(class_=re.compile(r'location|area|address', re.I))
    if location_elem:
        listing['location'] = location_elem.get_text(strip=True)
    else:
        listing['location'] = 'Unknown'

    # Extract price
    price_elem = card.find(class_=re.compile(r'price|cost', re.I))
    if price_elem:
        price_text = price_elem.get_text(strip=True)
        listing['price'] = parse_price(price_text)
    else:
        listing['price'] = None

    # Extract details (bedrooms, bathrooms, size)
    text_content = card.get_text()

    # Extract bedrooms
    bedrooms_match = re.search(r'(\d+)\s*(?:υπν|δωμ|bed)', text_content, re.I)
    if bedrooms_match:
        listing['bedrooms'] = int(bedrooms_match.group(1))
    else:
        listing['bedrooms'] = None

    # Extract bathrooms
    bathrooms_match = re.search(r'(\d+)\s*(?:μπ|bath)', text_content, re.I)
    if bathrooms_match:
        listing['bathrooms'] = int(bathrooms_match.group(1))
    else:
        listing['bathrooms'] = None

    # Extract size
    size_match = re.search(r'(\d+)\s*(?:τ\.?μ|m²|sqm)', text_content, re.I)
    if size_match:
        listing['size_sqm'] = int(size_match.group(1))
    else:
        listing['size_sqm'] = None

    # Extract description
    desc_elem = card.find(class_=re.compile(r'description|excerpt|content', re.I))
    if desc_elem:
        listing['description'] = desc_elem.get_text(' ', strip=True)
    else:
        listing['description'] = ''

    # Parking is not explicitly shown, set to None
    listing['parking'] = None

    # Generate unique hash for this listing
    listing['hash'] = generate_listing_hash(listing)

    # Add timestamps
    listing['first_seen'] = datetime.now().strftime('%Y-%m-%d')
    listing['last_checked'] = datetime.now().strftime('%Y-%m-%d')

    return listing


def parse_price(text):
    """Parse price from text like '180.000€' or '€180,000'"""
    # Remove €, spaces, dots, and commas used as thousands separator
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
    # Don't include price in hash - we want to detect price changes, not create new entries
    hash_string = f"{listing.get('url', '')}_{listing.get('property_id', '')}"
    return hashlib.md5(hash_string.encode()).hexdigest()
