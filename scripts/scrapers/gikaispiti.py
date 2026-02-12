"""
Gikaispiti scraper
Website: https://www.gikaispiti.gr
Note: Static HTML - uses simple HTTP requests
"""

import hashlib
import re
import requests
from datetime import datetime
from bs4 import BeautifulSoup


def scrape_gikaispiti(url):
    """
    Scrape listings from Gikaispiti website using HTTP requests

    Args:
        url: The search URL with filters applied

    Returns:
        List of listing dictionaries
    """
    listings = []

    try:
        print("   Scraping Gikaispiti...")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all property listing items
        # Each listing is in a <div class="property-list__item">
        property_items = soup.find_all('div', class_='property-list__item')

        print(f"   Found {len(property_items)} listings on Gikaispiti")

        for item in property_items:
            try:
                listing = extract_listing_data(item)
                if listing and listing.get('url'):
                    listings.append(listing)
            except Exception as e:
                print(f"   ⚠️  Error extracting listing: {e}")
                continue

        print(f"   Total listings scraped from Gikaispiti: {len(listings)}")

    except requests.RequestException as e:
        print(f"   ❌ HTTP error: {e}")
        raise
    except Exception as e:
        print(f"   ❌ Error: {e}")
        raise

    return listings


def extract_listing_data(item):
    """
    Extract data from a single listing item

    Args:
        item: BeautifulSoup element (<div class="property-list__item">) containing listing

    Returns:
        Dictionary with listing data
    """
    listing = {}

    # Extract URL from the title link
    title_div = item.find('div', class_='title')
    if title_div:
        link = title_div.find('a', href=True)
        if link and link.get('href'):
            href = link['href']
            if href.startswith('http'):
                listing['url'] = href
            else:
                listing['url'] = 'https://www.gikaispiti.gr/' + href
            listing['property_id'] = extract_property_id(listing['url'])

            # Extract title
            title = link.get_text(strip=True)
            listing['title'] = title

            # Extract property type from title
            if 'διαμέρισμα' in title.lower():
                listing['property_type'] = 'Διαμέρισμα'
            elif 'μεζονέτα' in title.lower():
                listing['property_type'] = 'Μεζονέτα'
            elif 'μονοκατοικία' in title.lower():
                listing['property_type'] = 'Μονοκατοικία'
            else:
                listing['property_type'] = 'Unknown'

        # Extract reference code from span
        code_span = title_div.find('span')
        if code_span:
            code_text = code_span.get_text(strip=True)
            code_match = re.search(r'(?:Κωδ:\s*)?([A-Z]\d+)', code_text)
            if code_match:
                listing['reference_code'] = code_match.group(1)
    else:
        return None

    # Extract photo URL
    img_div = item.find('div', class_='image')
    if img_div:
        img = img_div.find('img')
        if img:
            photo_url = img.get('src') or img.get('data-src')
            if photo_url:
                if not photo_url.startswith('http'):
                    if photo_url.startswith('/'):
                        photo_url = 'https://www.gikaispiti.gr' + photo_url
                    else:
                        photo_url = 'https://www.gikaispiti.gr/' + photo_url
                listing['photo_url'] = photo_url

    if 'photo_url' not in listing:
        listing['photo_url'] = None

    # Extract location
    location_div = item.find('div', class_='location')
    if location_div:
        listing['location'] = location_div.get_text(strip=True)
    else:
        listing['location'] = 'Unknown'

    # Extract description
    description_div = item.find('div', class_='description')
    if description_div:
        p_tag = description_div.find('p')
        if p_tag:
            listing['description'] = p_tag.get_text(strip=True)
        else:
            listing['description'] = description_div.get_text(strip=True)
    else:
        listing['description'] = ''

    # Extract price and details
    listing['price'] = None
    listing['size_sqm'] = None
    listing['bedrooms'] = None
    listing['bathrooms'] = None
    listing['parking'] = None

    price_details_div = item.find('div', class_='price-and-details')
    if price_details_div:
        # Extract price
        price_div = price_details_div.find('div', class_='price')
        if price_div:
            price_text = price_div.get_text(strip=True)
            listing['price'] = parse_price(price_text)

        # Extract details (size, price/sqm, bedrooms)
        details_div = price_details_div.find('div', class_='details')
        if details_div:
            spans = details_div.find_all('span')
            for span in spans:
                text = span.get_text(strip=True)

                # Size: "129.00 τ.μ."
                if 'τ.μ' in text and '€' not in text:
                    size_match = re.search(r'([\d.,]+)', text)
                    if size_match:
                        size_str = size_match.group(1).replace(',', '.')
                        try:
                            listing['size_sqm'] = int(float(size_str))
                        except ValueError:
                            pass

                # Bedrooms: "3 Υπνοδωμάτια"
                elif 'υπνοδωμάτι' in text.lower():
                    bed_match = re.search(r'(\d+)', text)
                    if bed_match:
                        listing['bedrooms'] = int(bed_match.group(1))

                # Bathrooms: "2 Μπάνια"
                elif 'μπάνι' in text.lower():
                    bath_match = re.search(r'(\d+)', text)
                    if bath_match:
                        listing['bathrooms'] = int(bath_match.group(1))

    # Check description for additional details
    desc = listing.get('description', '').lower()
    if 'parking' in desc or 'θέσ' in desc:
        park_match = re.search(r'(\d+)\s*θέσ', desc)
        if park_match:
            listing['parking'] = int(park_match.group(1))
        else:
            listing['parking'] = 1

    # Generate unique hash for this listing
    listing['hash'] = generate_listing_hash(listing)

    # Add timestamps
    listing['first_seen'] = datetime.now().strftime('%Y-%m-%d')
    listing['last_checked'] = datetime.now().strftime('%Y-%m-%d')

    return listing


def extract_property_id(url):
    """Extract property ID from URL"""
    # Pattern: property.php?id=5769
    match = re.search(r'id=(\d+)', url)
    if match:
        return match.group(1)

    # Fallback: generate from URL hash
    return hashlib.md5(url.encode()).hexdigest()[:8]


def parse_price(text):
    """Parse price from text like '€ 200.000' or '€200,000'"""
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
