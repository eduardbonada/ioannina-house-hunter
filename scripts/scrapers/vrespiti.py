"""
Vrespiti scraper
Website: https://www.vrespiti.gr
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


def scrape_vrespiti(url, max_pages=10):
    """
    Scrape listings from Vrespiti website using Selenium
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

        # Scrape multiple pages
        page = 1
        while page <= max_pages:
            # Update URL with current page number
            if '&p=' in url or '?p=' in url:
                # Replace existing page parameter
                page_url = re.sub(r'[&?]p=\d+', f'&p={page}', url)
            else:
                # Add page parameter
                page_url = url + f'&p={page}'

            print(f"   Scraping page {page}...")
            driver.get(page_url)

            # Wait for listings to load
            time.sleep(5)  # Give time for content to load

            # Get the rendered HTML
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            # Find all listing divs
            property_cards = soup.find_all('div', class_='divlink')

            if not property_cards:
                print(f"   No listings found on page {page}. Stopping pagination.")
                break

            print(f"   Found {len(property_cards)} listings on page {page}")

            # Extract listings from current page
            page_listings = []
            for card in property_cards:
                try:
                    listing = extract_listing_data(card)
                    if listing and listing.get('url'):
                        page_listings.append(listing)
                except Exception as e:
                    print(f"   ⚠️  Error extracting listing: {e}")
                    continue

            all_listings.extend(page_listings)

            # Check if there's a next page by looking for pagination links
            # If current page has fewer than expected results, it's probably the last page
            if len(property_cards) < 10:  # Vrespiti typically shows 10 per page
                print(f"   Page {page} has fewer results. Likely the last page.")
                break

            page += 1

        driver.quit()
        print(f"   Total listings scraped: {len(all_listings)}")

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

    # Extract URL from link with pdetails
    link = card.find('a', href=re.compile(r'pdetails\?'))
    if link and link.get('href'):
        url = link['href']
        if url.startswith('/'):
            url = 'https://www.vrespiti.gr' + url
        elif not url.startswith('http'):
            url = 'https://www.vrespiti.gr/' + url
        listing['url'] = url

        # Extract property ID from URL (id parameter)
        id_match = re.search(r'[&?]id=([^&]+)', url)
        if id_match:
            from urllib.parse import unquote
            listing['property_id'] = unquote(id_match.group(1))
        else:
            listing['property_id'] = extract_property_id(url)
    else:
        return None

    # Extract photo URL
    photo_elem = card.find('div', class_='photo')
    if photo_elem:
        img = photo_elem.find('img', src=True)
        if img:
            photo_url = img['src']
            if photo_url and not photo_url.startswith('http'):
                if photo_url.startswith('/'):
                    photo_url = 'https://www.vrespiti.gr' + photo_url
                else:
                    photo_url = 'https://www.vrespiti.gr/' + photo_url
            listing['photo_url'] = photo_url

    if not listing.get('photo_url'):
        listing['photo_url'] = None

    # Extract title and property type from h3
    title_elem = card.find('h3')
    if title_elem:
        title_text = title_elem.get_text(strip=True)
        listing['title'] = title_text

        # Extract property type from title (e.g., "ΔΙΑΜΕΡΙΣΜΑ 99 τ.μ. προς Πώληση")
        type_match = re.match(r'^([Α-Ωα-ωA-Za-z/]+)', title_text)
        if type_match:
            listing['property_type'] = type_match.group(1)
        else:
            listing['property_type'] = 'Unknown'
    else:
        listing['title'] = ''
        listing['property_type'] = 'Unknown'

    # Extract location from h4
    location_elem = card.find('h4')
    if location_elem:
        listing['location'] = location_elem.get_text(strip=True)
    else:
        listing['location'] = 'Unknown'

    # Extract price from p.price
    price_elem = card.find('p', class_='price')
    if price_elem:
        price_text = price_elem.get_text(strip=True)
        listing['price'] = parse_price(price_text)
    else:
        listing['price'] = None

    # Extract details from infoline
    infoline = card.find('p', class_='infoline')
    if infoline:
        text = infoline.get_text()

        # Extract bedrooms (e.g., "3 Υπν.")
        bedrooms_match = re.search(r'(\d+)\s*Υπν', text)
        if bedrooms_match:
            listing['bedrooms'] = int(bedrooms_match.group(1))
        else:
            listing['bedrooms'] = None

        # Extract bathrooms (e.g., "1 Μπ.")
        bathrooms_match = re.search(r'(\d+)\s*Μπ', text)
        if bathrooms_match:
            listing['bathrooms'] = int(bathrooms_match.group(1))
        else:
            listing['bathrooms'] = None

        # Extract size (e.g., "99 τ.μ.")
        size_match = re.search(r'(\d+)\s*τ\.μ', text)
        if size_match:
            listing['size_sqm'] = int(size_match.group(1))
        else:
            listing['size_sqm'] = None

        # Extract property code (e.g., "κωδ. Κ-20494")
        code_match = re.search(r'κωδ\.\s*([^\s]+)', text)
        if code_match:
            listing['reference_code'] = code_match.group(1)
    else:
        listing['bedrooms'] = None
        listing['bathrooms'] = None
        listing['size_sqm'] = None

    # Extract description from p.ad
    description_elem = card.find('p', class_='ad')
    if description_elem:
        listing['description'] = description_elem.get_text(' ', strip=True)
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


def extract_property_id(url):
    """Extract property ID from URL"""
    # Try to extract ID from URL parameters
    patterns = [
        r'[&?]id=([^&]+)',
        r'/property/(\d+)',
        r'/(\d+)$'
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            from urllib.parse import unquote
            return unquote(match.group(1))

    # If no ID found, generate from URL hash
    return hashlib.md5(url.encode()).hexdigest()[:8]


def parse_price(text):
    """Parse price from text like '280.000€' """
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


def generate_listing_hash(listing):
    """Generate unique hash for listing based on URL and property ID only"""
    # Don't include price in hash - we want to detect price changes, not create new entries
    hash_string = f"{listing.get('url', '')}_{listing.get('property_id', '')}"
    return hashlib.md5(hash_string.encode()).hexdigest()
