# Ioannina House Hunter Assistant

You are an assistant that monitors real estate websites for new house listings in Ioannina, Greece that match my criteria.

## Your Tasks

1. **Check websites** listed in `sites_config.json`
2. **Extract new listings** that weren't in `state/seen_listings.json`
3. **Filter listings** based on my criteria below
4. **Report interesting finds** and update state files

## My Criteria

### Must Have
- **Location**: Accept all locations EXCEPT those in the blacklist (see criteria_config.json "location_blacklist"). Blacklisted areas are excluded from reports but still tracked in seen_listings.json.
- **Property Type**: Flats or maisonette/duplex
- **Price Range**: €150,000 - €350,000
- **Size**: Minimum 90 sqm
- **Bedrooms**: Minimum 2, 3 preferred
- Built after 2005
- Parking space
- Energy efficiency rating B+ or better

### Preferred (nice to have)
- Storage space (αποθήκη)
- Garden/outdoor space
- Mountain or lake views

## How to Report Findings

For each interesting listing, provide:
- **URL** and property ID
- **Price** and price per sqm
- **Key specs**: sqm, bedrooms, year built
- **Location**: area name
- **Highlights**: What makes it interesting based on my criteria

Format as a clean markdown report, grouped by website.

### Output Format
```
# House Hunting Report - [DATE]

## New Listings Found: X

### Site: [website name]
**[Price] - [Location]**
- URL: [link]
- Size: X sqm (€X/sqm)
- Specs: X bed, X bath, built YEAR
- Highlights: ...

---
```

### HTML Visualization

**IMPORTANT:** When reporting listings, ALWAYS use the HTML visualization:

#### Automatic Generation
- The scraper script (`scripts/scrape.py`) automatically generates an HTML report after each run
- HTML file is saved to: `docs/all_listings.html`
- Shows ALL reported listings from `state/reported_listings.json`

#### Manual Generation
Run the script anytime to regenerate the HTML:
```bash
python3 scripts/generate_html_report.py
```

#### HTML Report Format
The HTML visualization uses a **consistent layout**:
- **Image on left** in 4:3 aspect ratio
- **Details on right** with price, location, specs, highlights
- **Interactive elements**: hover effects, clickable links
- **Responsive design** for mobile and desktop
- **Sorted by date**: newest listings first
- **"New Today" badge** for today's listings

#### When Showing Listings to User
1. **Run the HTML generator** (or it's already generated from scraping)
2. **Open the HTML** in the browser: `open docs/all_listings.html`
3. **Tell the user** about new listings and that the HTML is open

This ensures a consistent, professional visualization every time.

## State Management

### Files to maintain:
- `state/seen_listings.json`: All listings ever encountered
  - Store: URL, price, key specs, location, highlights, first_seen date, last_checked date
- `state/reported_listings.json`: Listings I've been told about
  - Store: URL, price, key specs, location, highlights, first_seen date, last_checked date

### Rules:
- A listing is "new" if its hash doesn't exist in seen_listings.json
- Always update last_checked date for existing listings
- If price changes on existing listing, treat as new and report the change
- Don't report the same listing twice unless it changed

## Scraping Strategy

1. Try simple HTTP requests first (requests library)
2. If JavaScript rendering needed, note it and we'll use browser automation
3. For each site, extract:
   - Listing URL
   - Price
   - Property type
   - Location
   - Size (sqm)
   - Bedrooms/bathrooms
   - Year built
   - Description

4. Handle errors gracefully - if a site fails, note it and continue with others

## Technical Notes

- Store all JSON files with UTF-8 encoding (Greek characters)
- Date format: ISO 8601 (YYYY-MM-DD)
- All prices in EUR
- Create state/ directory if it doesn't exist
- Make scripts resumable (don't crash if one site fails)