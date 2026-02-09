"""
Report generation for new listings
"""

from datetime import datetime
from collections import defaultdict
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def generate_report(listings):
    """
    Generate a markdown report for interesting listings

    Args:
        listings: List of listing dictionaries

    Returns:
        String containing formatted markdown report
    """
    report_lines = []
    today = datetime.now().strftime('%Y-%m-%d')

    # Header
    report_lines.append(f"# House Hunting Report - {today}")
    report_lines.append("")
    report_lines.append(f"## New Listings Found: {len(listings)}")
    report_lines.append("")

    # Group by website
    listings_by_site = defaultdict(list)
    for listing in listings:
        # Extract site name from URL
        url = listing.get('url', '')
        if 'greekestate' in url:
            site_name = 'Greek Estate'
        elif 'vrespiti' in url:
            site_name = 'Vrespiti'
        elif 'oikiarealestate' in url:
            site_name = 'Oikia'
        else:
            site_name = 'Unknown Site'

        listings_by_site[site_name].append(listing)

    # Generate report for each site
    for site_name, site_listings in listings_by_site.items():
        report_lines.append(f"### Site: {site_name}")
        report_lines.append("")

        for listing in site_listings:
            # Title with price and location
            price = listing.get('price')
            price_str = f"€{price:,}" if price else "Price not listed"
            location = listing.get('location', 'Unknown')

            report_lines.append(f"**{price_str} - {location}**")
            report_lines.append("")

            # Photo
            if listing.get('photo_url'):
                report_lines.append(f"![Property Photo]({listing['photo_url']})")
                report_lines.append("")

            # URL and property ID
            report_lines.append(f"- URL: {listing.get('url', 'N/A')}")
            if listing.get('property_id'):
                report_lines.append(f"- Property ID: {listing['property_id']}")

            # Size and price per sqm
            size = listing.get('size_sqm')
            if size and price:
                price_per_sqm = price / size
                report_lines.append(f"- Size: {size} sqm (€{price_per_sqm:.0f}/sqm)")
            elif size:
                report_lines.append(f"- Size: {size} sqm")

            # Specs
            specs_parts = []
            if listing.get('bedrooms'):
                specs_parts.append(f"{listing['bedrooms']} bed")
            if listing.get('bathrooms'):
                specs_parts.append(f"{listing['bathrooms']} bath")
            if listing.get('parking'):
                specs_parts.append(f"{listing['parking']} parking")
            if listing.get('year_built'):
                specs_parts.append(f"built {listing['year_built']}")

            if specs_parts:
                report_lines.append(f"- Specs: {', '.join(specs_parts)}")

            # Property type
            if listing.get('property_type') and listing['property_type'] != 'Unknown':
                report_lines.append(f"- Type: {listing['property_type']}")

            # Title/Description
            if listing.get('title'):
                report_lines.append(f"- Title: {listing['title']}")

            # Highlights
            if listing.get('highlights'):
                report_lines.append(f"- Highlights: {', '.join(listing['highlights'])}")

            report_lines.append("")
            report_lines.append("---")
            report_lines.append("")

    return '\n'.join(report_lines)


def generate_html_report_from_state():
    """
    Generate HTML visualization of all reported listings
    Imports and calls the generate_html_report script

    Returns:
        Path to generated HTML file or None if failed
    """
    try:
        from scripts.generate_html_report import generate_html_report
        html_path = generate_html_report()
        return html_path
    except Exception as e:
        print(f"⚠️  Could not generate HTML report: {e}")
        return None
