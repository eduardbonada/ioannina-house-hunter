"""
Greek Estate scraper
Website: https://greekestate.eu
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


def scrape_greek_estate(url):
    """
    Scrape listings from Greek Estate website using Selenium

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
        time.sleep(3)  # Give time for initial load

        # Wait for geodir-category-listing elements to appear
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "geodir-category-listing"))
            )
            time.sleep(2)  # Additional wait for content to populate
        except Exception as e:
            print(f"   ⚠️  Timeout waiting for listings: {e}")

        # Get the rendered HTML
        html = driver.page_source
        driver.quit()

        # Parse with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        # Find all listing articles
        property_cards = soup.find_all('article', class_='geodir-category-listing')

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
        if url.startswith('/'):
            url = 'https://greekestate.eu/' + url
        elif not url.startswith('http'):
            url = 'https://greekestate.eu/' + url
        listing['url'] = url
        listing['property_id'] = extract_property_id(url)
    else:
        return None

    # Extract first photo URL
    photo_url = None
    img_elem = card.find('img', src=True)
    if img_elem:
        photo_url = img_elem['src']
        # Handle relative URLs
        if photo_url and not photo_url.startswith('http'):
            if photo_url.startswith('/'):
                photo_url = 'https://greekestate.eu' + photo_url
            else:
                photo_url = 'https://greekestate.eu/' + photo_url
    listing['photo_url'] = photo_url

    # Extract price from geodir-category-content_price span
    price_elem = card.find('div', class_='geodir-category-content_price')
    if price_elem:
        price_span = price_elem.find('span')
        if price_span:
            price_text = price_span.get_text(strip=True)
            listing['price'] = parse_price(price_text)
    else:
        listing['price'] = None

    # Extract location from h3.title-sin_item
    title_elem = card.find('h3', class_='title-sin_item')
    if title_elem:
        location_parts = [span.get_text(strip=True) for span in title_elem.find_all('span')]
        listing['location'] = ', '.join(filter(None, location_parts))
        listing['title'] = listing['location']
    else:
        listing['location'] = 'Unknown'
        listing['title'] = ''

    # Extract property type and size from the div with class "color1"
    details_div = card.find('div', class_='color1')
    if details_div:
        text = details_div.get_text(' ', strip=True)

        # Property type (first word usually)
        property_type_match = re.search(r'^(\S+)', text)
        if property_type_match:
            listing['property_type'] = property_type_match.group(1)
        else:
            listing['property_type'] = 'Unknown'

        # Size in sqm - look for pattern like "89 m2"
        size_match = re.search(r'(\d+)\s*m', text)
        if size_match:
            listing['size_sqm'] = int(size_match.group(1))
        else:
            listing['size_sqm'] = None
    else:
        listing['property_type'] = 'Unknown'
        listing['size_sqm'] = None

    # Extract bedrooms, bathrooms, parking from geodir-category-content-details ul
    details_ul = card.find('div', class_='geodir-category-content-details')
    if details_ul:
        list_items = details_ul.find_all('li')

        for idx, li in enumerate(list_items):
            # Check the icon class
            icon = li.find('i')
            if icon:
                icon_class = ' '.join(icon.get('class', []))
                # Get the number (text content of li, excluding icon)
                number_text = li.get_text(strip=True)
                number = parse_number(number_text)

                if 'bed' in icon_class:
                    listing['bedrooms'] = number
                elif 'bath' in icon_class:
                    listing['bathrooms'] = number
                elif 'garage' in icon_class or 'car' in icon_class:
                    listing['parking'] = number

    # Set defaults if not found
    if 'bedrooms' not in listing:
        listing['bedrooms'] = None
    if 'bathrooms' not in listing:
        listing['bathrooms'] = None
    if 'parking' not in listing:
        listing['parking'] = None

    # Extract code (property reference)
    code_div = card.find('div', class_='codeDiv')
    if code_div:
        code_text = code_div.get_text(strip=True)
        code_match = re.search(r'Κωδικός:\s*(\S+)', code_text)
        if code_match:
            listing['reference_code'] = code_match.group(1)

    # Extract full description
    content_div = card.find('div', class_='geodir-category-content')
    if content_div:
        listing['description'] = content_div.get_text(' ', strip=True)
    else:
        listing['description'] = ''

    # Generate unique hash for this listing
    listing['hash'] = generate_listing_hash(listing)

    # Add timestamps
    listing['first_seen'] = datetime.now().strftime('%Y-%m-%d')
    listing['last_checked'] = datetime.now().strftime('%Y-%m-%d')

    return listing


def extract_property_id(url):
    """Extract property ID from URL"""
    patterns = [
        r'/properties/(\d+)',
        r'/property/(\d+)',
        r'/(\d+)$',
        r'id=(\d+)'
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    # If no ID found, generate from URL hash
    return hashlib.md5(url.encode()).hexdigest()[:8]


def parse_price(text):
    """Parse price from text like '250.000 €' """
    # Remove € symbol, spaces, and dots used as thousands separator
    text = text.replace('€', '').replace(' ', '').replace('.', '')

    # Extract digits
    match = re.search(r'(\d+)', text)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return None
    return None


def parse_number(text):
    """Parse number from text"""
    match = re.search(r'(\d+)', text)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return None
    return None


def generate_listing_hash(listing):
    """Generate unique hash for listing based on URL and key attributes"""
    hash_string = f"{listing.get('url', '')}_{listing.get('property_id', '')}_{listing.get('price', '')}"
    return hashlib.md5(hash_string.encode()).hexdigest()
