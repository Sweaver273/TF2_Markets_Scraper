# TF2_Markets_Scraper
This is a simplistic Python script that will take an item name for an input and spit back out the various prices across the Steam Community Market, Mannco.store, and Marketplace.tf marketplaces without having to provide any form of authentication. The script also considers marketplace fees that are in place for each website, providing the net proceeds that the seller would receive. The point of this program was to find the best website to sell various TF2 items that I no longer wanted. This was also a project that I worked on while learning how to code in Python, so there will likely be continued improvements over time.

# Packages Used:
* Requests (for basic web scraping)
* Re (for capturing/modifying all sorts of data)
* cloudscraper (for getting around CloudFlare on various marketplaces)

# Usage:
This program mostly follows the naming convention used by Steam Community, with exception to unusuals.
The format is as follows: "[Craftability] [Effect] [Strange] [Quality] [Festivized] [Killstreaker] [Item Name]".
Currently, everything is case sensitive. Each portion of the format (except item name) can be excluded if not present.

Example item: "Uncraftable Isotope Strange Unusual Festivized Professional Killstreak Quack Canvassed Black Box (Field-Tested)"

You should just be able to copy and paste the names straight from the item details in your steam backpack/community market listings (with exception to specifying unusual effects/craftability).
