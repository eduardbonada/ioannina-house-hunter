"""
Mesitikaioan scraper
Website: https://www.mesitikaioan.gr
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


def scrape_mesitikaioan(url):
    """
    Scrape listings from Mesitikaioan website using Selenium

    Args:
        url: The search URL with filters applied

    Returns:
        List of listing dictionaries
    """
    listings = []

    try:
        # Set up Selenium with Chrome in headless mode with better bot detection evasion
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        driver = webdriver.Chrome(options=chrome_options)

        # Execute CDP commands to hide webdriver
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.get(url)

        # Wait for listings to load
        print("   Waiting for page to load...")
        time.sleep(3)

        # Wait for listing elements to appear
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "listing-item"))
            )
            time.sleep(2)
        except Exception as e:
            print(f"   ⚠️  Timeout waiting for listings: {e}")

        # Get the rendered HTML
        html = driver.page_source
        driver.quit()

        # Parse with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        # Find all listing items
        property_cards = soup.find_all('div', class_='listing-item')

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
    link = card.find('a', class_='listing-title-link')
    if not link:
        link = card.find('a', href=True)

    if link and link.get('href'):
        url = link['href']
        if url.startswith('/'):
            url = 'https://www.mesitikaioan.gr' + url
        elif not url.startswith('http'):
            url = 'https://www.mesitikaioan.gr/' + url
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
                photo_url = 'https://www.mesitikaioan.gr' + photo_url
            else:
                photo_url = 'https://www.mesitikaioan.gr/' + photo_url
    listing['photo_url'] = photo_url

    # Extract title
    title_elem = card.find('h3', class_='listing-title') or card.find('h2', class_='listing-title')
    if title_elem:
        listing['title'] = title_elem.get_text(strip=True)
    else:
        listing['title'] = ''

    # Extract price
    price_elem = card.find('span', class_='listing-price') or card.find('div', class_='price')
    if price_elem:
        price_text = price_elem.get_text(strip=True)
        listing['price'] = parse_price(price_text)
    else:
        listing['price'] = None

    # Extract location
    location_elem = card.find('span', class_='listing-address') or card.find('div', class_='location')
    if location_elem:
        listing['location'] = location_elem.get_text(strip=True)
    else:
        listing['location'] = 'Unknown'

    # Extract property details (size, bedrooms, bathrooms)
    details_div = card.find('ul', class_='listing-details') or card.find('div', class_='property-details')

    listing['size_sqm'] = None
    listing['bedrooms'] = None
    listing['bathrooms'] = None
    listing['parking'] = None
    listing['property_type'] = 'Unknown'

    if details_div:
        details_text = details_div.get_text(' ', strip=True)

        # Extract size (m², sqm, τ.μ.)
        size_match = re.search(r'(\d+)\s*(?:m²|sqm|τ\.?μ\.?)', details_text, re.IGNORECASE)
        if size_match:
            listing['size_sqm'] = int(size_match.group(1))

        # Extract bedrooms (look for bedroom icon or text)
        bed_match = re.search(r'(\d+)\s*(?:bed|κρεβ|υπν)', details_text, re.IGNORECASE)
        if bed_match:
            listing['bedrooms'] = int(bed_match.group(1))

        # Extract bathrooms
        bath_match = re.search(r'(\d+)\s*(?:bath|μπάν|wc)', details_text, re.IGNORECASE)
        if bath_match:
            listing['bathrooms'] = int(bath_match.group(1))

        # Try to extract details from individual list items
        list_items = details_div.find_all('li')
        for li in list_items:
            text = li.get_text(strip=True)

            # Size
            if 'τ.μ' in text or 'm²' in text or 'sqm' in text:
                size_match = re.search(r'(\d+)', text)
                if size_match and not listing['size_sqm']:
                    listing['size_sqm'] = int(size_match.group(1))

            # Bedrooms
            elif 'υπνοδωμάτι' in text or 'κρεβ' in text or 'bedroom' in text.lower():
                bed_match = re.search(r'(\d+)', text)
                if bed_match and not listing['bedrooms']:
                    listing['bedrooms'] = int(bed_match.group(1))

            # Bathrooms
            elif 'μπάνι' in text or 'wc' in text.lower() or 'bath' in text.lower():
                bath_match = re.search(r'(\d+)', text)
                if bath_match and not listing['bathrooms']:
                    listing['bathrooms'] = int(bath_match.group(1))

    # Extract property type
    type_elem = card.find('span', class_='listing-type') or card.find('div', class_='property-type')
    if type_elem:
        listing['property_type'] = type_elem.get_text(strip=True)
    else:
        # Try to extract from title
        title_lower = listing.get('title', '').lower()
        if 'διαμέρισμα' in title_lower or 'apartment' in title_lower:
            listing['property_type'] = 'Διαμέρισμα'
        elif 'μεζονέτα' in title_lower or 'maisonette' in title_lower:
            listing['property_type'] = 'Μεζονέτα'
        elif 'μονοκατοικία' in title_lower or 'house' in title_lower:
            listing['property_type'] = 'Μονοκατοικία'

    # Extract property code/reference
    code_elem = card.find('span', class_='listing-code') or card.find('span', class_='property-id')
    if code_elem:
        listing['reference_code'] = code_elem.get_text(strip=True)

    # Extract description
    desc_elem = card.find('p', class_='listing-description') or card.find('div', class_='description')
    if desc_elem:
        listing['description'] = desc_elem.get_text(strip=True)
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
        r'/akinito/(\d+)',
        r'/property/(\d+)',
        r'/listing/(\d+)',
        r'/(\d+)$',
        r'id=(\d+)',
        r'-(\d+)$'
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
