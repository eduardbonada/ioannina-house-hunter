"""
Estateland scraper
Website: https://www.estateland.gr
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


def scrape_estateland(url, max_pages=10):
    """
    Scrape listings from Estateland website using Selenium
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

        print(f"   Scraping Estateland...")
        driver.get(url)

        # Wait for property listings to load
        time.sleep(5)  # Give time for JavaScript to load

        # Get the rendered HTML
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # Find all property listings - estateland uses 'listing-item' class
        property_cards = soup.find_all('div', class_='listing-item')

        print(f"   Found {len(property_cards)} listings on Estateland")

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
        print(f"   Total listings scraped from Estateland: {len(all_listings)}")

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

    # Extract URL - estateland uses /el/akinito/ pattern
    link = card.find('a', href=lambda x: x and '/akinito/' in str(x))
    if link and link.get('href'):
        url = link['href']
        if url.startswith('/'):
            url = 'https://www.estateland.gr' + url
        elif not url.startswith('http'):
            url = 'https://www.estateland.gr/' + url
        listing['url'] = url

        # Extract property ID from URL (last segment)
        id_match = re.search(r'/akinito/(\d+)', url)
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
        # Photos are already full URLs from spitogatos CDN
        listing['photo_url'] = photo_url if photo_url and not photo_url.startswith('data:') else None
    else:
        listing['photo_url'] = None

    # Extract title - in h4 tag
    title_elem = card.find('h4')
    if title_elem:
        listing['title'] = title_elem.get_text(strip=True)
    else:
        listing['title'] = ''

    # Extract property type from title (first word before "προς")
    if listing['title']:
        type_match = re.match(r'^([Α-Ωα-ω\s]+?)\s+προς', listing['title'])
        if type_match:
            listing['property_type'] = type_match.group(1).strip()
        else:
            listing['property_type'] = 'Unknown'
    else:
        listing['property_type'] = 'Unknown'

    # Extract location from title (text in parentheses)
    if listing['title']:
        location_match = re.search(r'\(([^)]+)\)', listing['title'])
        if location_match:
            listing['location'] = location_match.group(1).strip()
        else:
            listing['location'] = 'Unknown'
    else:
        listing['location'] = 'Unknown'

    # Extract price - in <b> tag with € symbol
    details_div = card.find('div', class_='col-sm-7') or card.find('div', class_='col-lg-8')
    if details_div:
        b_tag = details_div.find('b')
        if b_tag:
            price_text = b_tag.get_text(strip=True)
            # Price is before the span.pull-right
            price_span = b_tag.find('span', class_='pull-right')
            if price_span:
                # Remove the span content to get just the price
                price_text = price_text.replace(price_span.get_text(strip=True), '').strip()
            listing['price'] = parse_price(price_text)
        else:
            listing['price'] = None
    else:
        listing['price'] = None

    # Extract size - in span with class pull-right inside <b> tag
    if details_div and b_tag:
        size_span = b_tag.find('span', class_='pull-right')
        if size_span:
            size_text = size_span.get_text(strip=True)
            size_match = re.search(r'(\d+)\s*τ\.μ', size_text)
            if size_match:
                listing['size_sqm'] = int(size_match.group(1))
            else:
                listing['size_sqm'] = None
        else:
            listing['size_sqm'] = None
    else:
        listing['size_sqm'] = None

    # Extract details from ul list
    if details_div:
        ul_elem = details_div.find('ul')
        if ul_elem:
            list_items = ul_elem.find_all('li')
            for li in list_items:
                text = li.get_text(strip=True)

                # Bedrooms (Υπνοδωμάτια)
                if 'Υπνοδωμάτι' in text:
                    bedrooms_match = re.search(r'(\d+)', text)
                    if bedrooms_match:
                        listing['bedrooms'] = int(bedrooms_match.group(1))

                # Bathrooms (Μπάνιο)
                elif 'Μπάνι' in text:
                    bathrooms_match = re.search(r'(\d+)', text)
                    if bathrooms_match:
                        listing['bathrooms'] = int(bathrooms_match.group(1))

    # Set defaults if not found
    if 'bedrooms' not in listing:
        listing['bedrooms'] = None
    if 'bathrooms' not in listing:
        listing['bathrooms'] = None

    # Extract parking from description or details
    text_content = card.get_text()
    if re.search(r'parking|γκαράζ|garage|στάθμευσ', text_content, re.I):
        listing['parking'] = 1
    else:
        listing['parking'] = None

    # Extract property code - in p with class listing-item-code
    code_elem = card.find('p', class_='listing-item-code')
    if code_elem:
        code_text = code_elem.get_text(strip=True)
        code_match = re.search(r'Κωδ\.\s*(\d+)', code_text)
        if code_match:
            listing['reference_code'] = code_match.group(1)

    # Extract description - paragraph after ul
    if details_div:
        # Find all p tags, skip the ones with listing-item-code class
        description_p = None
        for p in details_div.find_all('p'):
            if not p.get('class') or 'listing-item-code' not in p.get('class', []):
                # Look for paragraph with actual description text
                text = p.get_text(strip=True)
                if len(text) > 50:  # Description should be substantial
                    description_p = p
                    break

        if description_p:
            listing['description'] = description_p.get_text(' ', strip=True)
        else:
            listing['description'] = ''
    else:
        listing['description'] = ''

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
