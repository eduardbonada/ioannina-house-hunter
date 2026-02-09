# Ioannina House Hunter

Automated real estate monitoring system for finding properties in Ioannina, Greece.

## Overview

This tool automatically scrapes configured real estate websites, filters listings based on your criteria, and generates reports of interesting properties.

## Features

- Scrapes multiple Greek real estate websites:
  - Greek Estate (greekestate.eu)
  - Vrespiti (vrespiti.gr)
- Uses Selenium for JavaScript rendering
- Extracts property photos from listings
- Filters properties by location, price, size, bedrooms, and other criteria
- Tracks seen and reported listings to avoid duplicates
- Detects price changes on existing listings
- Generates markdown and HTML reports with all property details and photos
- Calculates price per sqm for easy comparison

## Installation

### Requirements

- Python 3.8+
- Google Chrome browser
- pip (Python package manager)

### Setup

1. Install Python dependencies:
```bash
pip3 install -r requirements.txt
```

2. Ensure Google Chrome is installed (Selenium will auto-manage chromedriver)

## Usage

### Running a Scan

```bash
python3 scripts/scrape.py
```

This will:
1. Check all enabled websites in `sites_config.json`
2. Extract new listings
3. Filter based on criteria in `CLAUDE.md`
4. Generate a report in `reports/` directory
5. Update state files in `state/` directory

### Configuration

#### Search Criteria

**Edit `criteria_config.json`** to change your preferences without touching any code:

```json
{
  "must_have": {
    "price_min": 150000,        // Change minimum price
    "price_max": 350000,        // Change maximum price
    "size_min": 90,             // Change minimum sqm
    "bedrooms_min": 2,          // Change minimum bedrooms
    "locations": [              // Add/remove areas (Greek & English)
      "ioannina", "κέντρο", "botaniko", "βοτανικό", "anatoli", "ανατολή"
    ],
    "property_types": [         // Add/remove property types
      "flat", "διαμέρισμα", "maisonette", "μεζονέτα"
    ]
  },
  "preferred": {
    "keywords": [               // Add/remove preferred features
      "storage", "αποθήκη", "garden", "κήπος", "parking"
    ]
  }
}
```

**Example changes:**
- Lower price to €120k: Change `"price_min": 120000`
- Accept 1-bedroom: Change `"bedrooms_min": 1`
- Add new area Perama: Add `"perama", "περάμα"` to locations array

After changing the config, just run the scraper again - no code changes needed!

#### Websites

Edit `sites_config.json` to add or modify websites to monitor:
```json
{
  "sites": [
    {
      "name": "Greek Estate",
      "url": "https://greekestate.eu/el/properties?...",
      "enabled": true,
      "scraping_method": "http"
    }
  ]
}
```

## Project Structure

```
ioannina-house-hunter/
├── CLAUDE.md              # Project documentation and instructions
├── criteria_config.json   # ⭐ Your search criteria (edit this!)
├── sites_config.json      # Website configuration
├── requirements.txt       # Python dependencies
├── scripts/
│   ├── scrape.py         # Main scraping script
│   ├── scrapers/
│   │   └── greek_estate.py  # Greek Estate scraper
│   └── utils/
│       ├── state_manager.py  # State tracking
│       ├── filters.py        # Criteria filtering
│       └── reporter.py       # Report generation
├── state/
│   ├── seen_listings.json     # All seen listings
│   └── reported_listings.json # Reported listings
└── reports/
    └── report_YYYYMMDD_HHMMSS.md  # Generated reports
```

## State Management

The system maintains two state files:

- **seen_listings.json**: All listings ever encountered (prevents re-reporting)
- **reported_listings.json**: Listings that have been reported to you

Listings are identified by a hash of their URL, property ID, and price. If the price changes, the listing is treated as new and reported again.

## Reports

Reports are saved as markdown files in the `reports/` directory with format:
- `report_YYYYMMDD_HHMMSS.md`

Each report includes:
- Property URL and ID
- Price and price per sqm
- Size, bedrooms, bathrooms, parking
- Property type
- Location
- Highlights based on your criteria

## Automation

To run automatically on a schedule, set up a cron job:

```bash
# Edit crontab
crontab -e

# Add this line to run daily at 9 AM
0 9 * * * cd /Users/eduard/Development/ioannina-house-hunter && /usr/local/bin/python3 scripts/scrape.py
```

## Troubleshooting

### Selenium/Chrome Issues

If you get Chrome or chromedriver errors:
1. Ensure Chrome is installed
2. Update Selenium: `pip3 install --upgrade selenium`
3. Selenium 4+ auto-manages chromedriver

### No Listings Found

- Check if the website URL is still valid
- Verify the website structure hasn't changed
- Look at debug output for errors

### Dependencies Not Found

Reinstall requirements:
```bash
pip3 install -r requirements.txt
```

## Adding New Websites

To add a new real estate website:

1. Add configuration to `sites_config.json`
2. Create a new scraper in `scripts/scrapers/your_site.py`
3. Import and call it in `scripts/scrape.py`
4. Update `scripts/utils/reporter.py` to recognize the new site's URLs
5. Follow the pattern from `greek_estate.py` or `vrespiti.py`

## Current Criteria

**Must Have:**
- Location: Ioannina center, Botaniko, Anatoli
- Property Type: Flats or maisonette/duplex
- Price: €150,000 - €350,000
- Size: Minimum 90 sqm
- Bedrooms: Minimum 2 (3 preferred)
- Built after 2005
- Parking space
- Energy rating B+

**Preferred:**
- Storage space (αποθήκη)
- Garden/outdoor space
- Mountain or lake views
