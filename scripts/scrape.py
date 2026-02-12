#!/usr/bin/env python3
"""
Main scraping script for Ioannina House Hunter
Checks configured real estate websites for new listings
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.scrapers.greek_estate import scrape_greek_estate
from scripts.scrapers.vrespiti import scrape_vrespiti
from scripts.scrapers.oikia import scrape_oikia
from scripts.scrapers.skouras import scrape_skouras
from scripts.scrapers.estateland import scrape_estateland
from scripts.scrapers.gartzonikas import scrape_gartzonikas
from scripts.scrapers.gikaispiti import scrape_gikaispiti
from scripts.utils.state_manager import StateManager
from scripts.utils.filters import matches_criteria
from scripts.utils.reporter import generate_report, generate_html_report_from_state


def load_config():
    """Load sites configuration"""
    config_path = Path(__file__).parent.parent / "sites_config.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    """Main scraping workflow"""
    print("🏠 Ioannina House Hunter - Starting scan...")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Load configuration
    config = load_config()
    state_manager = StateManager()

    all_new_listings = []

    # Process each enabled site
    for site in config['sites']:
        if not site.get('enabled', True):
            print(f"⏭️  Skipping {site['name']} (disabled)")
            continue

        print(f"🔍 Checking {site['name']}...")

        try:
            # Scrape based on site name
            if site['name'] == 'Greek Estate':
                listings = scrape_greek_estate(site['url'])
            elif site['name'] == 'Vrespiti':
                listings = scrape_vrespiti(site['url'])
            elif site['name'] == 'Oikia':
                listings = scrape_oikia(site['url'])
            elif site['name'] == 'Skouras':
                listings = scrape_skouras(site['url'])
            elif site['name'] == 'estateland':
                listings = scrape_estateland(site['url'])
            elif site['name'] == 'Gartzonikas':
                listings = scrape_gartzonikas(site['url'])
            elif site['name'] == 'Gikaispiti':
                listings = scrape_gikaispiti(site['url'])
            else:
                print(f"⚠️  No scraper implemented for {site['name']}")
                continue

            print(f"   Found {len(listings)} total listings")

            # Filter for new listings
            new_listings = []
            for listing in listings:
                if state_manager.is_new_listing(listing):
                    new_listings.append(listing)
                    state_manager.add_listing(listing)
                else:
                    state_manager.update_last_checked(listing)

            print(f"   {len(new_listings)} new listings")

            # Filter by criteria
            interesting_listings = [
                listing for listing in new_listings
                if matches_criteria(listing)
            ]

            print(f"   {len(interesting_listings)} match criteria ✨\n")

            if interesting_listings:
                all_new_listings.extend(interesting_listings)

        except Exception as e:
            print(f"❌ Error scraping {site['name']}: {e}\n")
            continue

    # Generate and save report
    if all_new_listings:
        report = generate_report(all_new_listings)

        # Save report
        reports_dir = Path(__file__).parent.parent / "reports"
        reports_dir.mkdir(exist_ok=True)
        report_path = reports_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"📊 Report saved to: {report_path}")
        print("\n" + "="*60)
        print(report)

        # Mark as reported
        for listing in all_new_listings:
            state_manager.mark_as_reported(listing)
    else:
        print("✅ Scan complete. No new interesting listings found.")

    # Save state
    state_manager.save()
    print("\n💾 State saved.")

    # Generate HTML visualization of all reported listings
    print("\n📄 Generating HTML visualization...")
    html_path = generate_html_report_from_state()
    if html_path:
        print(f"✅ HTML report available at: {html_path}")


if __name__ == "__main__":
    main()
