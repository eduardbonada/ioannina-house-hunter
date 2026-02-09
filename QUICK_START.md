# Quick Start Guide

## Changing Your Preferences

Simply edit `criteria_config.json` - no code changes needed!

### Common Changes

#### 1. Change Price Range

```json
"price_min": 120000,  // Lower minimum to €120k
"price_max": 400000   // Raise maximum to €400k
```

#### 2. Change Minimum Bedrooms

```json
"bedrooms_min": 1  // Accept 1-bedroom flats
```

or

```json
"bedrooms_min": 3  // Only 3+ bedrooms
```

#### 3. Change Minimum Size

```json
"size_min": 70  // Accept smaller flats (70 sqm)
```

or

```json
"size_min": 120  // Only larger properties
```

#### 5. Change Property Types

To add houses:

```json
"property_types": [
  "flat", "apartment", "διαμέρισμα",
  "maisonette", "μεζονέτα", "duplex",
  "house", "μονοκατοικία"          // Add houses
]
```

#### 6. Add Preferred Keywords

To highlight listings with "elevator" or "balcony":

```json
"keywords": [
  "storage", "αποθήκη",
  "garden", "κήπος",
  "view", "θέα",
  "parking", "θέση", "πάρκινγκ",
  "elevator", "ασανσέρ",    // Add elevator
  "balcony", "μπαλκόνι"     // Add balcony
]
```

### Full Example: Budget Hunter Setup

Looking for affordable 1-2 bedroom flats, any location:

```json
{
  "must_have": {
    "property_types": ["flat", "apartment", "διαμέρισμα"],
    "price_min": 80000,
    "price_max": 180000,
    "size_min": 50,
    "bedrooms_min": 1,
    "year_built_min": 2005
  },
  "preferred": {
    "keywords": ["parking", "θέση", "ασανσέρ", "elevator"]
  }
}
```

### Full Example: Premium Hunter Setup

Looking for spacious 3+ bedroom properties in prime areas:

```json
{
  "must_have": {
    "property_types": ["flat", "διαμέρισμα", "maisonette", "μεζονέτα"],
    "price_min": 250000,
    "price_max": 500000,
    "size_min": 120,
    "bedrooms_min": 3,
    "year_built_min": 2010
  },
  "preferred": {
    "keywords": [
      "storage", "αποθήκη",
      "garden", "κήπος",
      "view", "θέα",
      "parking", "θέση",
      "elevator", "ασανσέρ",
      "luxury", "πολυτελές"
    ]
  }
}
```

## After Making Changes

Just run the scraper again:

```bash
python3 scripts/scrape.py
```

The new criteria will be loaded automatically!

## Resetting Seen Listings

If you change criteria significantly and want to see all listings again (even ones you've seen before):

```bash
rm state/*.json
python3 scripts/scrape.py
```

This clears the memory and starts fresh.

## Tips

1. **Always save valid JSON** - Use a JSON validator if unsure
2. **Include Greek terms** - Most listings use Greek text
3. **Be specific with locations** - Use neighborhood names, not just "Ioannina"
4. **Test incrementally** - Make one change at a time to see the effect
5. **Keep a backup** - Save your working config before major changes
