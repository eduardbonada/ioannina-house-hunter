# Ioannina House Hunter

Automated real estate monitoring system for finding properties in Ioannina, Greece.

## Overview

This tool automatically scrapes configured real estate websites, filters listings based on your criteria, and generates beautiful HTML reports of interesting properties.

## Quick Start

### 1. Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

### 2. Run the Scraper

```bash
python3 scripts/scrape.py
```

### 3. View Results

The scraper will automatically open an HTML report in your browser, or you can manually open:

```bash
open docs/all_listings.html
```

That's it! The tool will find new listings matching your criteria and show them in a beautiful, visual format.

## Features

- **Multi-site scraping**: Monitors 7+ Greek real estate websites:
  - Greek Estate, Vrespiti, Oikia, Skouras, Estateland, Gartzonikas, Gikaispiti
- **Smart filtering**: Automatically filters by price, size, location, bedrooms, etc.
- **Beautiful HTML reports**: Visual reports with property photos and details
- **Duplicate detection**: Tracks seen listings to avoid repeats
- **Price change alerts**: Notifies you when prices drop
- **Location blacklist**: Exclude unwanted neighborhoods
- **State persistence**: Remembers what you've already seen

## Installation

### Requirements

- **Python 3.8+** - Check with: `python3 --version`
- **Google Chrome** - Required for some websites (Selenium auto-manages ChromeDriver)

### Setup

1. **Clone or download this repository**

2. **Install Python packages:**
   ```bash
   pip3 install -r requirements.txt
   ```
   This installs: requests, beautifulsoup4, lxml, selenium

3. **Done!** You're ready to run your first scan.

## Usage

### Basic Usage

**Run a scan:**
```bash
python3 scripts/scrape.py
```

**View the HTML report:**
```bash
open docs/all_listings.html
```

**View listing history:**
```bash
python3 scripts/view_history.py
```

### Advanced Usage

**Generate HTML report manually:**
```bash
python3 scripts/generate_html_report.py
```

**Clean up utilities:**
```bash
# Remove listings from blacklisted locations
python3 scripts/clean_blacklisted.py

# Remove duplicate entries
python3 scripts/cleanup_duplicates.py

# Refresh highlights for all listings
python3 scripts/refresh_highlights.py
```

## Configuration

### Customize Your Search Criteria

**Edit `criteria_config.json`** to match your preferences:

```json
{
  "must_have": {
    "price_min": 150000,        // Minimum price in EUR
    "price_max": 350000,        // Maximum price in EUR
    "size_min": 90,             // Minimum size in sqm
    "bedrooms_min": 2,          // Minimum bedrooms
    "year_built_min": 2005      // Minimum construction year
  },
  "location_blacklist": [       // Areas to exclude (Greek & English)
    "stavraki", "σταυρακι",
    "katsika", "κατσικα"
  ]
}
```

**Common changes:**
- **Lower budget?** Change `"price_min": 120000`
- **Need 3 bedrooms?** Change `"bedrooms_min": 3`
- **Exclude a neighborhood?** Add to `location_blacklist`

After editing, just run `python3 scripts/scrape.py` again!

### Enable/Disable Websites

**Edit `sites_config.json`** to control which sites to scrape:

```json
{
  "sites": [
    {
      "name": "Greek Estate",
      "enabled": true,           // Set to false to skip this site
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
└── docs/
    └── report_YYYYMMDD_HHMMSS.md  # Generated reports
```

## State Management

The system maintains two state files:

- **seen_listings.json**: All listings ever encountered (prevents re-reporting)
- **reported_listings.json**: Listings that have been reported to you

Listings are identified by a hash of their URL, property ID, and price. If the price changes, the listing is treated as new and reported again.

## Reports

Reports are saved as markdown files in the `docs/` directory with format:
- `report_YYYYMMDD_HHMMSS.md`

Each report includes:
- Property URL and ID
- Price and price per sqm
- Size, bedrooms, bathrooms, parking
- Property type
- Location
- Highlights based on your criteria

## Automation (Optional)

Run the scraper automatically every day using cron:

```bash
# Edit your crontab
crontab -e

# Add this line to run daily at 9 AM (adjust path to your installation)
0 9 * * * cd /path/to/ioannina-house-hunter && python3 scripts/scrape.py
```

## Troubleshooting

### "Module not found" errors

**Solution:** Install dependencies:
```bash
pip3 install -r requirements.txt
```

### Chrome/Selenium errors

**Solution:**
1. Make sure Google Chrome is installed
2. Update Selenium: `pip3 install --upgrade selenium`
3. Selenium 4+ automatically downloads and manages ChromeDriver

### No new listings found

**Possible reasons:**
- All current listings have already been seen (check `state/seen_listings.json`)
- Website structure may have changed (scrapers need updating)
- Your criteria may be too restrictive

**Debug:** Look at the console output for errors or check individual scrapers

### Greek characters displaying incorrectly

**Solution:** Ensure UTF-8 encoding:
```bash
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
```


## How It Works

1. **Scraping**: Each enabled website is scraped (HTTP or Selenium for JavaScript sites)
2. **Filtering**: Listings are filtered against your criteria in `criteria_config.json`
3. **Deduplication**: Each listing gets a unique hash to prevent duplicates
4. **State tracking**:
   - `state/seen_listings.json` - All listings ever encountered
   - `state/reported_listings.json` - Listings shown to you
5. **Reporting**:
   - New listings are reported in markdown format
   - Beautiful HTML visualization with photos
   - Price changes trigger new reports

## Default Search Criteria

The default configuration searches for:
- **Property Type**: Flats, apartments, maisonettes, duplexes
- **Price**: €150,000 - €350,000
- **Size**: Minimum 90 sqm
- **Bedrooms**: Minimum 2
- **Built**: After 2005
- **Features**: Prefers parking, storage, garden, views

Customize these in `criteria_config.json` to match your needs!

## Contributing

Want to add a new real estate website?

1. Create a new scraper in `scripts/scrapers/new_site.py`
2. Follow the pattern from existing scrapers (e.g., `greek_estate.py`)
3. Add the site to `sites_config.json`
4. Import and call it in `scripts/scrape.py`

## License

Personal use project
