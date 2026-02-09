"""
Filtering logic for listings based on criteria
"""

import json
import re
from pathlib import Path


# Load criteria from config file
def load_criteria():
    """Load search criteria from criteria_config.json"""
    config_path = Path(__file__).parent.parent.parent / "criteria_config.json"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return {
                'must_have': config['must_have'],
                'preferred': config['preferred'],
                'location_blacklist': config.get('location_blacklist', [])
            }
    except FileNotFoundError:
        print("⚠️  criteria_config.json not found, using default criteria")
        # Fallback to default criteria
        return {
            'must_have': {
                'locations': [],  # No location filtering - accept all areas
                'property_types': ['flat', 'apartment', 'διαμέρισμα', 'maisonette', 'μεζονέτα', 'duplex'],
                'price_min': 150000,
                'price_max': 350000,
                'size_min': 90,
                'bedrooms_min': 2,
                'year_built_min': 2005,
            },
            'preferred': {
                'keywords': ['storage', 'αποθήκη', 'garden', 'κήπος', 'view', 'θέα', 'parking', 'θέση', 'πάρκινγκ']
            },
            'location_blacklist': []
        }


# Load criteria once at module import
CRITERIA = load_criteria()


def matches_criteria(listing):
    """
    Check if a listing matches the required criteria

    Args:
        listing: Dictionary with listing data

    Returns:
        Boolean indicating if listing matches criteria
        Also adds 'highlights' field to listing
    """
    highlights = []
    meets_requirements = True

    # Check location blacklist - reject listings in blacklisted areas
    location = listing.get('location', '')
    if location and location != 'unknown':
        location_normalized = normalize_greek_text(location)
        blacklist = CRITERIA.get('location_blacklist', [])
        for blacklisted_area in blacklist:
            blacklisted_normalized = normalize_greek_text(blacklisted_area)
            if blacklisted_normalized in location_normalized:
                # Listing is in a blacklisted location - reject it
                return False

    # Check price
    price = listing.get('price')
    if price:
        if price < CRITERIA['must_have']['price_min'] or price > CRITERIA['must_have']['price_max']:
            return False
    else:
        # No price info, can't filter out yet
        highlights.append("⚠️ Price not listed")

    # Check size
    size = listing.get('size_sqm')
    if size:
        if size < CRITERIA['must_have']['size_min']:
            return False
        highlights.append(f"{size} sqm")
    else:
        highlights.append("⚠️ Size not listed")

    # Check bedrooms
    bedrooms = listing.get('bedrooms')
    if bedrooms:
        if bedrooms < CRITERIA['must_have']['bedrooms_min']:
            return False
        if bedrooms >= 3:
            highlights.append(f"{bedrooms} bedrooms (preferred!)")
        else:
            highlights.append(f"{bedrooms} bedrooms")
    else:
        highlights.append("⚠️ Bedrooms not listed")

    # Location info (blacklist check already done above)
    if location and location != 'unknown':
        # Just add location as info
        highlights.append(f"📍 {location}")
    elif location == 'unknown':
        highlights.append("⚠️ Location unknown - needs verification")

    # Display property type from scraped data
    property_type = listing.get('property_type', '')
    if property_type and property_type != 'Unknown':
        # Just show the property type that was scraped
        highlights.append(f"🏠 {property_type}")

    # Check for preferred features
    title = listing.get('title', '')
    description_text = f"{title} {listing.get('description', '')}".lower()
    for keyword in CRITERIA['preferred']['keywords']:
        if keyword.lower() in description_text:
            highlights.append(f"✨ Has {keyword}")

    # Check for price changes
    if listing.get('price_change'):
        change = listing['price_change']
        diff = change['difference']
        if diff < 0:
            highlights.append(f"💰 Price dropped by €{abs(diff):,}")
        else:
            highlights.append(f"⬆️ Price increased by €{diff:,}")

    # Add price per sqm if available
    if price and size:
        price_per_sqm = price / size
        highlights.append(f"€{price_per_sqm:.0f}/sqm")

    listing['highlights'] = highlights

    return meets_requirements


def normalize_greek_text(text):
    """Normalize Greek text for comparison"""
    # Remove accents and convert to lowercase
    replacements = {
        'ά': 'α', 'έ': 'ε', 'ή': 'η', 'ί': 'ι', 'ό': 'ο', 'ύ': 'υ', 'ώ': 'ω',
        'ΐ': 'ι', 'ΰ': 'υ', 'ς': 'σ'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.lower()
