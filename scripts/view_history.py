#!/usr/bin/env python3
"""
Visualize all reported listings from most recent to oldest
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict


def load_reported_listings():
    """Load reported listings from state file"""
    state_path = Path(__file__).parent.parent / "state" / "reported_listings.json"

    if not state_path.exists():
        print("❌ No reported listings found. Run a scan first!")
        return {}

    with open(state_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_markdown_report(listings_data):
    """Generate markdown report of all reported listings"""

    if not listings_data:
        return "# Listing History\n\nNo listings reported yet. Run a scan first!\n"

    # Convert to list and sort by reported_date (most recent first)
    listings = []
    for hash_key, listing in listings_data.items():
        listing['hash'] = hash_key
        listings.append(listing)

    # Sort by reported_date descending
    listings.sort(key=lambda x: x.get('reported_date', '0000-00-00'), reverse=True)

    # Group by date
    listings_by_date = defaultdict(list)
    for listing in listings:
        date = listing.get('reported_date', 'Unknown Date')
        listings_by_date[date].append(listing)

    # Generate markdown
    lines = []
    lines.append("# Reported Listings History")
    lines.append("")
    lines.append(f"**Total Listings Reported:** {len(listings)}")
    lines.append("")
    lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Generate listings by date
    for date in sorted(listings_by_date.keys(), reverse=True):
        date_listings = listings_by_date[date]
        lines.append(f"## {date} ({len(date_listings)} listing{'s' if len(date_listings) != 1 else ''})")
        lines.append("")

        for listing in date_listings:
            # Price and location header
            price = listing.get('price')
            price_str = f"€{price:,}" if price else "Price not listed"
            location = listing.get('location', 'Unknown')

            lines.append(f"### {price_str} - {location}")
            lines.append("")

            # URL
            url = listing.get('url', 'N/A')
            if url != 'N/A' and not url.startswith('http'):
                url = f"https://greekestate.eu/{url}"
            lines.append(f"🔗 **[View Listing]({url})**")
            lines.append("")

            # Property ID
            if listing.get('property_id'):
                lines.append(f"- **Property ID:** {listing['property_id']}")

            # Size and price per sqm
            size = listing.get('size_sqm')
            if size and price:
                price_per_sqm = price / size
                lines.append(f"- **Size:** {size} sqm (€{price_per_sqm:.0f}/sqm)")
            elif size:
                lines.append(f"- **Size:** {size} sqm")

            # Specs (bedrooms, bathrooms)
            specs = []
            if listing.get('bedrooms'):
                specs.append(f"{listing['bedrooms']} bed")
            if listing.get('bathrooms'):
                specs.append(f"{listing['bathrooms']} bath")
            if listing.get('parking'):
                specs.append(f"{listing['parking']} parking")

            if specs:
                lines.append(f"- **Specs:** {', '.join(specs)}")

            # Property type
            if listing.get('property_type') and listing['property_type'] != 'Unknown':
                lines.append(f"- **Type:** {listing['property_type']}")

            # First seen
            if listing.get('first_seen'):
                lines.append(f"- **First Seen:** {listing['first_seen']}")

            # Highlights
            if listing.get('highlights'):
                highlights = listing['highlights']
                if highlights:
                    lines.append(f"- **Highlights:** {', '.join(highlights)}")

            # Price change info
            if listing.get('price_change'):
                change = listing['price_change']
                old_price = change.get('old')
                new_price = change.get('new')
                diff = change.get('difference')
                if diff:
                    arrow = "📉" if diff < 0 else "📈"
                    lines.append(f"- **Price Change:** {arrow} €{old_price:,} → €{new_price:,} (€{abs(diff):,})")

            lines.append("")
            lines.append("---")
            lines.append("")

    return '\n'.join(lines)


def generate_html_report(listings_data):
    """Generate HTML report of all reported listings"""

    if not listings_data:
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Listing History</title>
</head>
<body>
    <h1>No listings reported yet</h1>
    <p>Run a scan first!</p>
</body>
</html>
"""

    # Convert to list and sort by reported_date (most recent first)
    listings = []
    for hash_key, listing in listings_data.items():
        listing['hash'] = hash_key
        listings.append(listing)

    listings.sort(key=lambda x: x.get('reported_date', '0000-00-00'), reverse=True)

    # Group by date
    listings_by_date = defaultdict(list)
    for listing in listings:
        date = listing.get('reported_date', 'Unknown Date')
        listings_by_date[date].append(listing)

    # Generate HTML
    html = []
    html.append("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ioannina House Hunter - Listing History</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        h1 {
            margin: 0 0 10px 0;
        }
        .stats {
            font-size: 14px;
            opacity: 0.9;
        }
        .date-section {
            margin-bottom: 40px;
        }
        .date-header {
            background-color: #667eea;
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .date-header h2 {
            margin: 0;
            font-size: 20px;
        }
        .listing-card {
            background: white;
            border-radius: 8px;
            padding: 0;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
            overflow: hidden;
            display: flex;
            flex-direction: row;
        }
        .listing-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        .listing-photo {
            width: 400px;
            min-width: 400px;
            height: 300px;
            object-fit: cover;
            background-color: #f0f0f0;
        }
        .listing-content {
            padding: 25px;
            flex: 1;
        }
        @media (max-width: 768px) {
            .listing-card {
                flex-direction: column;
            }
            .listing-photo {
                width: 100%;
                min-width: 100%;
                height: 250px;
            }
        }
        .listing-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }
        .price {
            font-size: 28px;
            font-weight: bold;
            color: #667eea;
        }
        .location {
            font-size: 18px;
            color: #666;
        }
        .view-btn {
            display: inline-block;
            background-color: #667eea;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            margin-bottom: 15px;
            font-weight: 500;
        }
        .view-btn:hover {
            background-color: #5568d3;
        }
        .details {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .detail-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .detail-label {
            font-weight: 600;
            color: #333;
        }
        .detail-value {
            color: #666;
        }
        .highlights {
            background-color: #f8f9ff;
            border-left: 4px solid #667eea;
            padding: 12px;
            margin-top: 15px;
            border-radius: 4px;
        }
        .highlight-tag {
            display: inline-block;
            background-color: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            margin: 4px;
            font-size: 13px;
        }
        .price-change {
            background-color: #fff3cd;
            border: 1px solid #ffc107;
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
        }
        .price-drop {
            background-color: #d4edda;
            border-color: #28a745;
        }
    </style>
</head>
<body>
    <header>
        <h1>🏠 Ioannina House Hunter</h1>
        <div class="stats">
            <strong>Total Listings Reported:</strong> """ + str(len(listings)) + """<br>
            <strong>Generated:</strong> """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """
        </div>
    </header>
""")

    # Generate listings by date
    for date in sorted(listings_by_date.keys(), reverse=True):
        date_listings = listings_by_date[date]
        html.append(f'    <div class="date-section">')
        html.append(f'        <div class="date-header">')
        html.append(f'            <h2>{date} ({len(date_listings)} listing{"s" if len(date_listings) != 1 else ""})</h2>')
        html.append(f'        </div>')

        for listing in date_listings:
            price = listing.get('price')
            price_str = f"€{price:,}" if price else "Price not listed"
            location = listing.get('location', 'Unknown')

            url = listing.get('url', '#')
            if url != '#' and not url.startswith('http'):
                url = f"https://greekestate.eu/{url}"

            html.append(f'        <div class="listing-card">')

            # Add photo if available
            photo_url = listing.get('photo_url')
            if photo_url:
                html.append(f'            <img src="{photo_url}" alt="Property" class="listing-photo">')

            html.append(f'            <div class="listing-content">')
            html.append(f'                <div class="listing-header">')
            html.append(f'                    <div>')
            html.append(f'                        <div class="price">{price_str}</div>')
            html.append(f'                        <div class="location">{location}</div>')
            html.append(f'                    </div>')
            html.append(f'                </div>')

            html.append(f'                <a href="{url}" target="_blank" class="view-btn">🔗 View Listing</a>')

            html.append(f'                <div class="details">')

            if listing.get('property_id'):
                html.append(f'                    <div class="detail-item">')
                html.append(f'                        <span class="detail-label">ID:</span>')
                html.append(f'                        <span class="detail-value">{listing["property_id"]}</span>')
                html.append(f'                    </div>')

            size = listing.get('size_sqm')
            if size:
                if price:
                    price_per_sqm = price / size
                    html.append(f'                    <div class="detail-item">')
                    html.append(f'                        <span class="detail-label">Size:</span>')
                    html.append(f'                        <span class="detail-value">{size} sqm (€{price_per_sqm:.0f}/sqm)</span>')
                    html.append(f'                    </div>')
                else:
                    html.append(f'                    <div class="detail-item">')
                    html.append(f'                        <span class="detail-label">Size:</span>')
                    html.append(f'                        <span class="detail-value">{size} sqm</span>')
                    html.append(f'                    </div>')

            if listing.get('bedrooms'):
                html.append(f'                    <div class="detail-item">')
                html.append(f'                        <span class="detail-label">Bedrooms:</span>')
                html.append(f'                        <span class="detail-value">{listing["bedrooms"]}</span>')
                html.append(f'                    </div>')

            if listing.get('bathrooms'):
                html.append(f'                    <div class="detail-item">')
                html.append(f'                        <span class="detail-label">Bathrooms:</span>')
                html.append(f'                        <span class="detail-value">{listing["bathrooms"]}</span>')
                html.append(f'                    </div>')

            if listing.get('property_type') and listing['property_type'] != 'Unknown':
                html.append(f'                    <div class="detail-item">')
                html.append(f'                        <span class="detail-label">Type:</span>')
                html.append(f'                        <span class="detail-value">{listing["property_type"]}</span>')
                html.append(f'                    </div>')

            if listing.get('first_seen'):
                html.append(f'                    <div class="detail-item">')
                html.append(f'                        <span class="detail-label">First Seen:</span>')
                html.append(f'                        <span class="detail-value">{listing["first_seen"]}</span>')
                html.append(f'                    </div>')

            html.append(f'                </div>')  # Close details

            # Price change
            if listing.get('price_change'):
                change = listing['price_change']
                old_price = change.get('old')
                new_price = change.get('new')
                diff = change.get('difference')
                if diff:
                    css_class = "price-drop" if diff < 0 else ""
                    arrow = "📉" if diff < 0 else "📈"
                    html.append(f'                <div class="price-change {css_class}">')
                    html.append(f'                    <strong>Price Change:</strong> {arrow} €{old_price:,} → €{new_price:,} (€{abs(diff):,})')
                    html.append(f'                </div>')

            # Highlights
            if listing.get('highlights'):
                highlights = listing['highlights']
                if highlights:
                    html.append(f'                <div class="highlights">')
                    for highlight in highlights:
                        html.append(f'                    <span class="highlight-tag">{highlight}</span>')
                    html.append(f'                </div>')

            html.append(f'            </div>')  # Close listing-content
            html.append(f'        </div>')  # Close listing-card

        html.append(f'    </div>')

    html.append("""
</body>
</html>
""")

    return '\n'.join(html)


def main():
    """Main function"""
    print("📊 Loading reported listings...")

    listings = load_reported_listings()

    if not listings:
        print("❌ No listings to display")
        sys.exit(1)

    print(f"✅ Found {len(listings)} reported listings")
    print()

    # Generate markdown report
    print("📝 Generating markdown report...")
    markdown_content = generate_markdown_report(listings)

    output_dir = Path(__file__).parent.parent / "reports"
    output_dir.mkdir(exist_ok=True)

    markdown_path = output_dir / "listing_history.md"
    with open(markdown_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    print(f"✅ Markdown report saved: {markdown_path}")

    # Generate HTML report
    print("🌐 Generating HTML report...")
    html_content = generate_html_report(listings)

    html_path = output_dir / "listing_history.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ HTML report saved: {html_path}")
    print()
    print("🎉 Done! Open the HTML file in your browser for a nice view:")
    print(f"   open {html_path}")


if __name__ == "__main__":
    main()
