"""
State management for tracking seen and reported listings
"""

import json
from pathlib import Path
from datetime import datetime


class StateManager:
    """Manages state files for tracking listings"""

    def __init__(self):
        self.state_dir = Path(__file__).parent.parent.parent / "state"
        self.state_dir.mkdir(exist_ok=True)

        self.seen_file = self.state_dir / "seen_listings.json"
        self.reported_file = self.state_dir / "reported_listings.json"

        self.seen_listings = self._load_state(self.seen_file)
        self.reported_listings = self._load_state(self.reported_file)

    def _load_state(self, file_path):
        """Load state from JSON file"""
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"⚠️  Error reading {file_path}, starting fresh")
                return {}
        return {}

    def _save_state(self, data, file_path):
        """Save state to JSON file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def is_new_listing(self, listing):
        """Check if listing is new (not seen before or price changed)"""
        listing_hash = listing['hash']

        if listing_hash not in self.seen_listings:
            return True

        # Check if price changed
        old_listing = self.seen_listings[listing_hash]
        if listing.get('price') and old_listing.get('price'):
            if listing['price'] != old_listing['price']:
                # Price changed, treat as new
                listing['price_change'] = {
                    'old': old_listing['price'],
                    'new': listing['price'],
                    'difference': listing['price'] - old_listing['price']
                }
                return True

        return False

    def add_listing(self, listing):
        """Add a new listing to seen listings"""
        listing_hash = listing['hash']
        self.seen_listings[listing_hash] = {
            'url': listing.get('url'),
            'property_id': listing.get('property_id'),
            'price': listing.get('price'),
            'location': listing.get('location'),
            'size_sqm': listing.get('size_sqm'),
            'bedrooms': listing.get('bedrooms'),
            'bathrooms': listing.get('bathrooms'),
            'property_type': listing.get('property_type'),
            'title': listing.get('title'),
            'photo_url': listing.get('photo_url'),
            'first_seen': listing.get('first_seen'),
            'last_checked': listing.get('last_checked'),
            'price_change': listing.get('price_change')
        }

    def update_last_checked(self, listing):
        """Update last_checked timestamp and other fields for existing listing"""
        listing_hash = listing['hash']
        if listing_hash in self.seen_listings:
            old_listing = self.seen_listings[listing_hash]

            # Always update last_checked
            old_listing['last_checked'] = datetime.now().strftime('%Y-%m-%d')

            # Update fields that were missing or have changed (but don't trigger "new" notification)
            # This handles cases where data extraction improved or fields were initially missing
            if listing.get('price') and not old_listing.get('price'):
                old_listing['price'] = listing.get('price')

            if listing.get('size_sqm') and not old_listing.get('size_sqm'):
                old_listing['size_sqm'] = listing.get('size_sqm')

            if listing.get('bedrooms') and not old_listing.get('bedrooms'):
                old_listing['bedrooms'] = listing.get('bedrooms')

            if listing.get('bathrooms') and not old_listing.get('bathrooms'):
                old_listing['bathrooms'] = listing.get('bathrooms')

            if listing.get('photo_url') and not old_listing.get('photo_url'):
                old_listing['photo_url'] = listing.get('photo_url')

            if listing.get('location') and not old_listing.get('location'):
                old_listing['location'] = listing.get('location')

            if listing.get('property_type') and not old_listing.get('property_type'):
                old_listing['property_type'] = listing.get('property_type')

    def mark_as_reported(self, listing):
        """Mark listing as reported"""
        listing_hash = listing['hash']
        self.reported_listings[listing_hash] = {
            'url': listing.get('url'),
            'property_id': listing.get('property_id'),
            'price': listing.get('price'),
            'location': listing.get('location'),
            'size_sqm': listing.get('size_sqm'),
            'bedrooms': listing.get('bedrooms'),
            'bathrooms': listing.get('bathrooms'),
            'property_type': listing.get('property_type'),
            'title': listing.get('title'),
            'photo_url': listing.get('photo_url'),
            'highlights': listing.get('highlights'),
            'first_seen': listing.get('first_seen'),
            'reported_date': datetime.now().strftime('%Y-%m-%d'),
            'price_change': listing.get('price_change')
        }

    def save(self):
        """Save all state files"""
        self._save_state(self.seen_listings, self.seen_file)
        self._save_state(self.reported_listings, self.reported_file)
