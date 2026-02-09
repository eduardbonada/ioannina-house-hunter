#!/usr/bin/env python3
"""
Refresh highlights for all reported listings
This re-runs the filtering logic to update property type detection and other highlights
"""

import json
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.utils.filters import matches_criteria


def refresh_highlights():
    """Refresh highlights for all reported listings"""

    # Load reported listings
    reported_path = Path(__file__).parent.parent / "state" / "reported_listings.json"

    try:
        with open(reported_path, 'r', encoding='utf-8') as f:
            reported = json.load(f)
    except FileNotFoundError:
        print("❌ No reported_listings.json found.")
        return

    print(f"📊 Refreshing highlights for {len(reported)} listings...\n")

    updated_count = 0
    for listing_hash, listing in reported.items():
        # Store old highlights for comparison
        old_highlights = listing.get('highlights', [])

        # Re-run the criteria matching to get updated highlights
        # This will update the highlights in-place
        matches = matches_criteria(listing)

        # Get new highlights
        new_highlights = listing.get('highlights', [])

        # Check if highlights changed
        if old_highlights != new_highlights:
            updated_count += 1
            print(f"✨ Updated: {listing.get('property_id', 'N/A')}")
            print(f"   Location: {listing.get('location', 'Unknown')}")
            print(f"   Old: {', '.join(old_highlights[:3])}...")
            print(f"   New: {', '.join(new_highlights[:3])}...")
            print()

    # Save updated listings
    with open(reported_path, 'w', encoding='utf-8') as f:
        json.dump(reported, f, ensure_ascii=False, indent=2)

    print(f"✅ Updated {updated_count} listings with refreshed highlights")
    print(f"💾 Saved to {reported_path}")


def main():
    refresh_highlights()


if __name__ == "__main__":
    main()
