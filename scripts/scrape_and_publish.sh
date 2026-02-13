#!/bin/bash

# Ioannina House Hunter - Scrape and Publish to GitHub Pages
# This script runs the scraper and pushes updates to GitHub

# Set up PATH for cron environment
export PATH="/Library/Frameworks/Python.framework/Versions/3.12/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

# Change to project directory
cd /Users/eduard/Development/ioannina-house-hunter || exit 1

# Run the scraper with full python path
/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 scripts/scrape.py

# Check if there are changes to commit
if git diff --quiet docs/all_listings.html; then
    echo "No changes to publish"
    exit 0
fi

# Add the updated HTML report
git add docs/all_listings.html

# Commit with timestamp
git commit -m "Auto-update listings - $(date '+%Y-%m-%d %H:%M')"

# Push to GitHub
git push origin main

echo "✅ Published to GitHub Pages"
