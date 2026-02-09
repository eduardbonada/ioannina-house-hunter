#!/usr/bin/env python3
"""
Remove blacklisted locations from reported_listings.json
This is useful when you add new locations to the blacklist
"""

import json
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.utils.filters import load_criteria, normalize_greek_text


def clean_blacklisted_listings():
    """Remove listings from blacklisted locations from reported_listings.json"""

    # Load criteria to get blacklist
    criteria = load_criteria()
    blacklist = criteria.get('location_blacklist', [])

    if not blacklist:
        print("✅ No locations in blacklist. Nothing to clean.")
        return

    print(f"🔍 Blacklisted locations: {', '.join(blacklist)}")

    # Load reported listings
    reported_path = Path(__file__).parent.parent / "state" / "reported_listings.json"

    try:
        with open(reported_path, 'r', encoding='utf-8') as f:
            reported = json.load(f)
    except FileNotFoundError:
        print("❌ No reported_listings.json found.")
        return

    original_count = len(reported)
    print(f"\n📊 Total reported listings before cleanup: {original_count}")

    # Filter out blacklisted listings
    cleaned = {}
    removed_count = 0
    removed_listings = []

    for listing_hash, listing in reported.items():
        location = listing.get('location', '')

        if location and location != 'unknown':
            location_normalized = normalize_greek_text(location)
            is_blacklisted = False

            for blacklisted_area in blacklist:
                blacklisted_normalized = normalize_greek_text(blacklisted_area)
                if blacklisted_normalized in location_normalized:
                    is_blacklisted = True
                    removed_count += 1
                    removed_listings.append({
                        'id': listing.get('property_id', 'N/A'),
                        'location': location,
                        'price': listing.get('price', 0)
                    })
                    break

            if not is_blacklisted:
                cleaned[listing_hash] = listing
        else:
            # Keep listings with unknown location
            cleaned[listing_hash] = listing

    # Show removed listings
    if removed_count > 0:
        print(f"\n🗑️  Removing {removed_count} blacklisted listings:\n")
        for removed in removed_listings:
            print(f"   - {removed['id']}: {removed['location']} (€{removed['price']:,})")

        # Save cleaned listings
        with open(reported_path, 'w', encoding='utf-8') as f:
            json.dump(cleaned, f, ensure_ascii=False, indent=2)

        print(f"\n✅ Cleaned reported_listings.json")
        print(f"   Before: {original_count} listings")
        print(f"   After: {len(cleaned)} listings")
        print(f"   Removed: {removed_count} listings")
    else:
        print("\n✅ No blacklisted listings found in reported_listings.json")


def main():
    clean_blacklisted_listings()


if __name__ == "__main__":
    main()
