# TF2_Markets_Scraper
This is a simplistic Python script that will take an item name for an input and spit back out the various prices across the Steam Community Market, Mannco.store, and Marketplace.tf marketplaces. The script also takes into account the various marketplace fees that are in place for each website. The point of this program was to find the best website to sell various TF2 items that I no longer wanted in order to maximize the returns. This was also a project that I worked on while learning how to code in Python, so there will likely be continued improvements over time.

# Packages Used:
* Requests (for basic web scraping)
* Re (for capturing/modifying all sorts of data)
* undetected_chromedriver (to work around Cloudflare on Mannco & Marketplace)

# Usage:
This program mostly follows the naming convention used by Steam Community, with exception to unusuals. The format is as follows: "[Unusual Effect][Quality][Killstreaker][Item Name]". Each word in the name of the item should be capitalized just like how it is in Valve's ecosystem.
