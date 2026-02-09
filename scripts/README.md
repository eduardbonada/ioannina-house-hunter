# Ioannina House Hunter Scripts

## Main Scripts

### `scrape.py` - Main Scraper
Checks all enabled websites for new listings and generates reports.

```bash
python3 scripts/scrape.py
```

**What it does:**
1. Checks all enabled sites in `sites_config.json`
2. Extracts listings and compares with `state/seen_listings.json`
3. Filters new listings based on criteria in `criteria_config.json`
4. Generates markdown report in `reports/` directory
5. Updates state files
6. **Automatically generates HTML visualization** of all reported listings

---

### `generate_html_report.py` - HTML Report Generator
Creates a beautiful HTML visualization of all reported listings.

```bash
python3 scripts/generate_html_report.py
```

**Features:**
- Reads from `state/reported_listings.json`
- Creates `reports/all_listings.html`
- Images in 4:3 ratio on the left
- Property details on the right
- Responsive design
- Sorted by date (newest first)
- "New Today" badge for today's listings
- Automatically opens in browser

**Custom output path:**
```bash
python3 scripts/generate_html_report.py /path/to/custom/output.html
```

---

### `view_history.py` - View State History
View all seen and reported listings.

```bash
python3 scripts/view_history.py
```

---

## Scrapers

Located in `scripts/scrapers/`:
- `greek_estate.py` - Greek Estate scraper
- `vrespiti.py` - Vrespiti scraper

Each scraper extracts:
- Price, location, size, bedrooms, bathrooms
- Property type, photos, descriptions
- Property ID and URL

---

## Utilities

Located in `scripts/utils/`:

### `filters.py`
- Filters listings based on criteria
- No location filtering (accepts all areas)
- Price, size, bedrooms, property type filters
- Highlights preferred features

### `reporter.py`
- Generates markdown reports for new listings
- Provides function to generate HTML reports
- Groups listings by website

### `state_manager.py`
- Manages `state/seen_listings.json`
- Manages `state/reported_listings.json`
- Tracks listing hashes to detect new/changed listings
- Detects price changes

---

## Workflow

1. **Scrape websites:**
   ```bash
   python3 scripts/scrape.py
   ```
   This automatically generates the HTML report.

2. **View HTML report:**
   The HTML is automatically opened in your browser, or manually:
   ```bash
   open reports/all_listings.html
   ```

3. **Regenerate HTML anytime:**
   ```bash
   python3 scripts/generate_html_report.py
   ```

---

## Configuration Files

- `sites_config.json` - Website URLs and settings
- `criteria_config.json` - Search criteria (price, size, bedrooms, etc.)
- `state/seen_listings.json` - All listings ever encountered
- `state/reported_listings.json` - Listings that matched criteria

---

## Notes

- All JSON files use UTF-8 encoding for Greek characters
- Scripts are resumable (won't crash if one site fails)
- HTML report is regenerated after every scrape
- Location filtering is disabled to avoid missing area name variations
