#!/usr/bin/env python3
"""
Clean up duplicate listings in state files caused by hash generation including price
"""

import json
import hashlib
from pathlib import Path
from collections import defaultdict


def generate_new_hash(url, property_id):
    """Generate hash using new method (URL + property_id only)"""
    hash_string = f"{url}_{property_id}"
    return hashlib.md5(hash_string.encode()).hexdigest()


def merge_listings(duplicates):
    """Merge duplicate listings, keeping the most complete data"""
    # Sort by completeness - prefer entries with price, then by last_checked date
    def completeness_score(listing):
        score = 0
        if listing.get('price'):
            score += 100
        if listing.get('size_sqm'):
            score += 10
        if listing.get('bedrooms'):
            score += 5
        if listing.get('photo_url'):
            score += 5
        if listing.get('last_checked'):
            score += 1
        return score

    duplicates.sort(key=completeness_score, reverse=True)

    # Start with the most complete entry
    merged = duplicates[0].copy()

    # Fill in any missing fields from other entries
    for dup in duplicates[1:]:
        for key, value in dup.items():
            if value and not merged.get(key):
                merged[key] = value

    return merged


def cleanup_state_file(file_path):
    """Clean up duplicates in a state file"""
    print(f"\n🔍 Processing {file_path.name}...")

    with open(file_path, 'r', encoding='utf-8') as f:
        listings = json.load(f)

    print(f"   Found {len(listings)} total entries")

    # Group by URL
    by_url = defaultdict(list)
    for hash_key, listing in listings.items():
        url = listing.get('url', '')
        by_url[url].append((hash_key, listing))

    # Find duplicates
    duplicates_count = 0
    for url, entries in by_url.items():
        if len(entries) > 1:
            duplicates_count += len(entries) - 1

    print(f"   Found {duplicates_count} duplicate entries")

    # Create new listings dict with deduplicated data
    new_listings = {}
    removed_count = 0

    for url, entries in by_url.items():
        if len(entries) == 1:
            # No duplicates, just update the hash
            old_hash, listing = entries[0]
            new_hash = generate_new_hash(url, listing.get('property_id', ''))
            new_listings[new_hash] = listing
        else:
            # Merge duplicates
            listings_to_merge = [listing for _, listing in entries]
            merged_listing = merge_listings(listings_to_merge)

            # Generate new hash
            new_hash = generate_new_hash(url, merged_listing.get('property_id', ''))
            new_listings[new_hash] = merged_listing

            removed_count += len(entries) - 1

    print(f"   ✅ Removed {removed_count} duplicates")
    print(f"   📊 Result: {len(new_listings)} unique entries")

    # Save cleaned data
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(new_listings, f, ensure_ascii=False, indent=2)

    return removed_count


def main():
    """Main cleanup workflow"""
    print("🧹 Cleaning up duplicate listings...")

    state_dir = Path(__file__).parent.parent / "state"

    # Clean up both state files
    seen_file = state_dir / "seen_listings.json"
    reported_file = state_dir / "reported_listings.json"

    total_removed = 0

    if seen_file.exists():
        total_removed += cleanup_state_file(seen_file)

    if reported_file.exists():
        total_removed += cleanup_state_file(reported_file)

    print(f"\n✅ Cleanup complete! Removed {total_removed} total duplicates.")
    print("💡 You can now run the scraper again with the fixed hash generation.")


if __name__ == "__main__":
    main()
