# TF2_Markets_Scraper
This is a simplistic Python script that will take an item name for an input and spit back out the various prices across the Steam Community Market, Mannco.store, and Marketplace.tf marketplaces without having to provide any form of authentication. The script also takes into account the various marketplace fees that are in place for each website, providing the net profit that the seller is receiving. The point of this program was to find the best website to sell various TF2 items that I no longer wanted. This was also a project that I worked on while learning how to code in Python, so there will likely be continued improvements over time.

# Packages Used:
* Requests (for basic web scraping)
* Re (for capturing/modifying all sorts of data)
* undetected_chromedriver (to work around Cloudflare on Mannco & Marketplace)

# Usage:
This program mostly follows the naming convention used by Steam Community, with exception to unusuals.
The format is as follows: "[Unusual Effect] [Quality (Strange goes first)] [Festivized] [Killstreaker] [Item Name w/ skin & wear]". Each word in the name of the item should be capitalized.
Example: Isotope Strange Unusual Festivized Professional Killstreak Quack Canvassed Black Box (Field-Tested) *NOTE: there were no results

You should just be able to copy and paste the names straight from the item details in your steam backpack/community market listings (with exception to specifying unusual effects).