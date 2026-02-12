#!/usr/bin/env python3
"""
Generate HTML visualization of all reported listings
Reads from state/reported_listings.json and creates an interactive HTML report
"""

import json
from pathlib import Path
from datetime import datetime


def generate_html_report(output_path=None):
    """
    Generate HTML report from reported listings

    Args:
        output_path: Optional custom output path. Defaults to reports/all_listings.html
    """
    # Load reported listings
    reported_path = Path(__file__).parent.parent / "state" / "reported_listings.json"
    seen_path = Path(__file__).parent.parent / "state" / "seen_listings.json"

    try:
        with open(reported_path, 'r', encoding='utf-8') as f:
            reported_data = json.load(f)
    except FileNotFoundError:
        print("❌ No reported listings found.")
        return None

    # Load seen listings to get latest data
    try:
        with open(seen_path, 'r', encoding='utf-8') as f:
            seen_data = json.load(f)
    except FileNotFoundError:
        seen_data = {}

    if not reported_data:
        print("❌ No listings to display.")
        return None

    # Convert to list and merge with latest data from seen_listings
    listings = []
    for listing_hash, reported_listing in reported_data.items():
        # Start with reported listing
        listing = reported_listing.copy()
        listing['hash'] = listing_hash

        # Merge with latest data from seen_listings if available
        if listing_hash in seen_data:
            seen_listing = seen_data[listing_hash]
            # Update with latest data, keeping reported_date from reported_listing
            listing.update({
                'price': seen_listing.get('price') or listing.get('price'),
                'location': seen_listing.get('location') or listing.get('location'),
                'size_sqm': seen_listing.get('size_sqm') or listing.get('size_sqm'),
                'bedrooms': seen_listing.get('bedrooms') or listing.get('bedrooms'),
                'bathrooms': seen_listing.get('bathrooms') or listing.get('bathrooms'),
                'property_type': seen_listing.get('property_type') or listing.get('property_type'),
                'title': seen_listing.get('title') or listing.get('title'),
                'photo_url': seen_listing.get('photo_url') or listing.get('photo_url'),
                'last_checked': seen_listing.get('last_checked'),
            })

        listings.append(listing)

    # Sort by first_seen date (newest first)
    listings.sort(key=lambda x: x.get('first_seen', ''), reverse=True)

    total_listings = len(listings)

    # Count new listings (today)
    today = datetime.now().strftime('%Y-%m-%d')
    new_today = sum(1 for listing in listings if listing.get('first_seen') == today)

    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>All Reported Listings - Ioannina</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #0d1117;
            color: #c9d1d9;
            line-height: 1.6;
        }}

        .header {{
            background: #161b22;
            color: white;
            padding: 2rem;
            text-align: center;
            border-bottom: 1px solid #30363d;
        }}

        .header h1 {{
            font-size: 2rem;
            margin-bottom: 0.5rem;
            color: #c9d1d9;
        }}

        .header .subtitle {{
            opacity: 0.7;
            font-size: 1.1rem;
            color: #8b949e;
        }}

        .container {{
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 1rem;
        }}

        .stats {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}

        .stat-item {{
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 1.5rem;
            text-align: center;
        }}

        .stat-item h2 {{
            font-size: 2.5rem;
            color: #58a6ff;
            margin-bottom: 0.5rem;
        }}

        .stat-item.new-today h2 {{
            color: #3fb950;
        }}

        .stat-item p {{
            color: #8b949e;
            font-size: 1.1rem;
        }}

        .listing {{
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            overflow: hidden;
            margin-bottom: 2rem;
            transition: transform 0.2s ease, border-color 0.2s ease;
        }}

        .listing:hover {{
            transform: translateY(-2px);
            border-color: #58a6ff;
        }}

        .listing-content {{
            display: flex;
            flex-direction: row;
        }}

        .listing-image {{
            flex: 0 0 400px;
            aspect-ratio: 4 / 3;
            overflow: hidden;
            background: #0d1117;
        }}

        .listing-image img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}

        .listing-details {{
            flex: 1;
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
        }}

        .listing-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 1rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid #21262d;
        }}

        .price {{
            font-size: 2rem;
            font-weight: bold;
            color: #58a6ff;
        }}

        .property-id {{
            display: inline-block;
            background: transparent;
            border: 1px solid #30363d;
            padding: 0.4rem 0.8rem;
            border-radius: 6px;
            font-size: 0.85rem;
            color: #8b949e;
            font-weight: 500;
            margin-right: 0.5rem;
            margin-bottom: 0.25rem;
        }}

        .location {{
            font-size: 1.1rem;
            color: #8b949e;
            margin-bottom: 0.5rem;
            font-weight: 500;
        }}

        .location::before {{
            content: "📍 ";
        }}

        .property-type {{
            display: inline-block;
            background: transparent;
            color: #58a6ff;
            border: 1px solid #58a6ff;
            padding: 0.3rem 0.8rem;
            border-radius: 6px;
            font-size: 0.9rem;
            margin-bottom: 1rem;
        }}

        .specs {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1rem;
            margin: 1rem 0;
            padding: 1rem;
            background: transparent;
            border-top: 1px solid #21262d;
            border-radius: 0;
        }}

        .spec {{
            text-align: center;
        }}

        .spec-icon {{
            font-size: 1.5rem;
            margin-bottom: 0.25rem;
        }}

        .spec-label {{
            font-size: 0.75rem;
            color: #8b949e;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .spec-value {{
            font-weight: bold;
            font-size: 1.1rem;
            color: #c9d1d9;
        }}

        .highlights {{
            margin-top: auto;
            padding-top: 1rem;
        }}

        .highlight-tag {{
            display: inline-block;
            background: transparent;
            border: 1px solid #58a6ff;
            color: #58a6ff;
            padding: 0.4rem 0.8rem;
            border-radius: 15px;
            margin: 0.25rem;
            font-size: 0.85rem;
        }}

        .view-link {{
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 1px solid #21262d;
        }}

        .view-button {{
            display: inline-block;
            background: transparent;
            color: #58a6ff;
            border: 1px solid #58a6ff;
            padding: 0.6rem 1.2rem;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 600;
            transition: background 0.2s ease, color 0.2s ease;
            font-size: 0.95rem;
        }}

        .view-button:hover {{
            background: #58a6ff;
            color: #0d1117;
        }}

        .first-seen {{
            font-size: 0.85rem;
            color: #8b949e;
            margin-top: 0.5rem;
        }}

        .section-divider {{
            text-align: center;
            margin: 3rem 0 2rem;
            padding: 1rem;
            background: transparent;
            border: 1px solid #30363d;
            border-radius: 8px;
        }}

        .section-divider h2 {{
            color: #c9d1d9;
            font-size: 1.5rem;
            margin: 0;
            font-weight: 600;
        }}

        .new-badge {{
            background: transparent;
            color: #3fb950;
            border: 1px solid #3fb950;
            padding: 0.3rem 0.8rem;
            border-radius: 6px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-left: 1rem;
        }}

        .source-badge {{
            display: inline-block;
            padding: 0.4rem 0.8rem;
            border-radius: 6px;
            font-size: 0.85rem;
            font-weight: 600;
            background: transparent;
            border: 1px solid;
        }}

        @media (max-width: 968px) {{
            .stats {{
                grid-template-columns: 1fr;
                gap: 1.5rem;
            }}

            .listing-content {{
                flex-direction: column;
            }}

            .listing-image {{
                flex: 0 0 auto;
                width: 100%;
                aspect-ratio: 4 / 3;
            }}

            .specs {{
                grid-template-columns: repeat(2, 1fr);
            }}

            .header h1 {{
                font-size: 1.5rem;
            }}

            .price {{
                font-size: 1.5rem;
            }}

            .stat-item h2 {{
                font-size: 2rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏠 All Reported Listings</h1>
        <p class="subtitle">Ioannina Property Search</p>
    </div>

    <div class="container">
        <div class="stats">
            <div class="stat-item">
                <h2>{total_listings}</h2>
                <p>Total Reported Listings</p>
            </div>
            <div class="stat-item new-today">
                <h2>{new_today}</h2>
                <p>New Listings</p>
            </div>
        </div>
"""

    # Generate listing cards
    showing_earlier_section = False
    showing_new_section = False

    for idx, listing in enumerate(listings):
        price = listing.get('price') or 0
        price_formatted = f"€{price:,}" if price else "Price not listed"
        location = listing.get('location', 'Unknown location')
        property_id = listing.get('property_id', 'N/A')
        size = listing.get('size_sqm', 0)
        bedrooms = listing.get('bedrooms', 0)
        bathrooms = listing.get('bathrooms', 0)
        photo_url = listing.get('photo_url', '')
        first_seen = listing.get('first_seen', 'Unknown')
        url = listing.get('url', '#')
        property_type = listing.get('property_type', '')

        # Calculate price per sqm
        price_per_sqm = int(price / size) if (price and size and size > 0) else 0

        # Determine source from URL
        if 'greekestate' in url.lower():
            source_name = 'Greek Estate'
            source_color = '#3498db'
        elif 'vrespiti' in url.lower():
            source_name = 'Vrespiti'
            source_color = '#e74c3c'
        elif 'oikiarealestate' in url.lower():
            source_name = 'Oikia'
            source_color = '#9b59b6'
        elif 'skourashome' in url.lower():
            source_name = 'Skouras'
            source_color = '#2ecc71'
        elif 'estateland' in url.lower():
            source_name = 'Estateland'
            source_color = '#f39c12'
        elif 'gartzonikashome' in url.lower():
            source_name = 'Gartzonikas'
            source_color = '#1abc9c'
        elif 'gikaispiti' in url.lower():
            source_name = 'Gikaispiti'
            source_color = '#e67e22'
        else:
            source_name = 'Unknown'
            source_color = '#95a5a6'

        # Check if listing is new (today)
        today = datetime.now().strftime('%Y-%m-%d')
        is_new = first_seen == today
        new_badge = '<span class="new-badge">New</span>' if is_new else ''

        # Get highlights
        highlights = listing.get('highlights', [])
        highlights_html = ''.join([f'<span class="highlight-tag">{h}</span>' for h in highlights])

        # Add section dividers
        section_html = ""
        if is_new and not showing_new_section:
            section_html = """
        <div class="section-divider new-today">
            <h2>🌟 New Listings</h2>
        </div>
"""
            showing_new_section = True
        elif not is_new and not showing_earlier_section:
            section_html = """
        <div class="section-divider earlier">
            <h2>📋 Earlier Listings</h2>
        </div>
"""
            showing_earlier_section = True

        # Fallback image SVG
        fallback_svg = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 300'%3E%3Crect fill='%23e9ecef' width='400' height='300'/%3E%3Ctext x='50%25' y='50%25' text-anchor='middle' fill='%23adb5bd' font-size='18' dy='.3em'%3ENo Image%3C/text%3E%3C/svg%3E"

        listing_html = section_html + f"""
        <div class="listing">
            <div class="listing-content">
                <div class="listing-image">
                    <img src="{photo_url}"
                         alt="Property {property_id}"
                         onerror="this.src='{fallback_svg}'">
                </div>
                <div class="listing-details">
                    <div class="listing-header">
                        <div class="price">{price_formatted}{new_badge}</div>
                        <div>
                            <span class="source-badge" style="border-color: {source_color}; color: {source_color};">{source_name}</span>
                        </div>
                    </div>

                    <div class="location">{location}</div>
                    <div class="property-type">{property_type}</div>

                    <div class="specs">
                        <div class="spec">
                            <div class="spec-icon">📐</div>
                            <div class="spec-label">Size</div>
                            <div class="spec-value">{size} m²</div>
                        </div>
                        <div class="spec">
                            <div class="spec-icon">💶</div>
                            <div class="spec-label">Per m²</div>
                            <div class="spec-value">€{price_per_sqm:,}</div>
                        </div>
                        <div class="spec">
                            <div class="spec-icon">🛏️</div>
                            <div class="spec-label">Bedrooms</div>
                            <div class="spec-value">{bedrooms}</div>
                        </div>
                        <div class="spec">
                            <div class="spec-icon">🚿</div>
                            <div class="spec-label">Bathrooms</div>
                            <div class="spec-value">{bathrooms}</div>
                        </div>
                    </div>

                    <div class="highlights">
                        {highlights_html}
                    </div>

                    <div class="view-link">
                        <a href="{url}"
                           target="_blank"
                           class="view-button">View Property Details →</a>
                        <div class="first-seen">First seen: {first_seen}</div>
                    </div>
                </div>
            </div>
        </div>
"""
        html += listing_html

    # Close HTML
    html += """
    </div>
</body>
</html>
"""

    # Save to file
    if output_path is None:
        reports_dir = Path(__file__).parent.parent / "reports"
        reports_dir.mkdir(exist_ok=True)
        output_path = reports_dir / "all_listings.html"

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ HTML report generated: {output_path}")
    return output_path


def main():
    """Main function for command line usage"""
    import sys

    output_path = None
    if len(sys.argv) > 1:
        output_path = Path(sys.argv[1])

    result_path = generate_html_report(output_path)

    if result_path:
        print(f"\n📊 Open the report at: {result_path}")

        # Optionally open in browser
        import subprocess
        import platform

        system = platform.system()
        try:
            if system == 'Darwin':  # macOS
                subprocess.run(['open', str(result_path)])
            elif system == 'Windows':
                subprocess.run(['start', str(result_path)], shell=True)
            elif system == 'Linux':
                subprocess.run(['xdg-open', str(result_path)])
            print("🌐 Opening in browser...")
        except Exception as e:
            print(f"⚠️  Could not auto-open browser: {e}")


if __name__ == "__main__":
    main()
