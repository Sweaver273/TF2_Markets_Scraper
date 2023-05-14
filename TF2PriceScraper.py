import requests
import re
import undetected_chromedriver as uc  #https://github.com/ultrafunkamsterdam/undetected-chromedriver

while True:
    itemname = input("Provide a market hash name:")
    driver = uc.Chrome(headless=True, version_main=112)

    def SteamPrices(market_hash_name):
        #Steam Listings
        global steamcommunity
        global isUncraftable
        response = requests.get(f"https://steamcommunity.com/market/listings/440/{market_hash_name}")
        print(f"https://steamcommunity.com/market/listings/440/{market_hash_name}")
        if response.status_code == 200:
            global marketid
            marketid = re.search(r'Market_LoadOrderSpread.*?(\d+)', response.text)
            if marketid is None:
                steamcommunity = ['Steam Community', 'Not on Market', 'Not on Market', 'Not on Market', 'Not on Market']
                isUncraftable = False
                return
            isUncraftable = bool(re.search(r'Not Usable in Crafting', response.text))
        else:
            raise(f"Steam returned code {response.status_code} fetching sell orders. This shouldn't happen.")
        response = requests.get(f"https://steamcommunity.com/market/priceoverview/?appid=440&currency=1&market_hash_name={market_hash_name}")
        if response.status_code == 200:
            lowestsellr = re.search(r'lowest_price":"\$(\S{1,6}\.\d{2})",', response.text)
            if lowestsellr is None:
                lowestsell = "No Listings"
                LSactualreturn = "No Listings"
            else:
                lowestsell = "$" + lowestsellr.group(1)
                LSactualreturn = "$" + str(round((float(lowestsellr.group(1)) / 1.15) + .005, 2))  #ceil() but mathimatically
        elif response.status_code == 429:
            lowestsell = "Ratelimited"
            LSactualreturn = "Ratelimited"
        else:
            lowestsell = "N/A"
            BOactualreturn = "N/A"

        #Steam Buyorders
        response = requests.get(f"https://steamcommunity.com/market/itemordershistogram?country=US&language=english&currency=1&item_nameid={marketid.group(1)}&two_factor=0")
        if response.status_code == 200:
            highestbuyr = re.search(r'to buy at.*?\$(\S{1,6}\.\d{2})', response.text)
            if highestbuyr is None:
                BOactualreturn = "No Orders"
                highestbuy = "No Orders"
            else:
                BOactualreturn = highestbuyr.group(1).replace(",", "")
                highestbuy = "$" + BOactualreturn
                BOactualreturn = "$" + str(round((float(BOactualreturn) / 1.15) + .005, 2))  #ceil() but mathimatically
        elif response.status_code == 429:
            highestbuy = "Ratelimited"
            BOactualreturn = "Ratelimited"
        else:
            highestbuy = "N/A"
            BOactualreturn = "N/A"

        steamcommunity = ['Steam Community', lowestsell, LSactualreturn, highestbuy, BOactualreturn]
        return

    def MCPrices(name, driver):
        name = name.replace(" ", "-")
        name = name.replace(".", "")
        name = name.replace(":", "")
        name = name.lower()
        if isUncraftable == True:
            url = f"https://mannco.store/item/440-uncraftable-{name}"
        else:
            url = f"https://mannco.store/item/440-{name}"
        driver.get(url)
        print(f"{url}")
        lowestsellr = re.search(r'lowPrice": "(\d+\.\d{2})', driver.page_source) #r'ecurrency">\$(\d+\.\d{2})'
        highestbuyr = re.search(r'Quantity(?:<.*>\s)*?<td>\$(\S{1,6}\.\d{2})', driver.page_source)
        if lowestsellr.group(1) == "0.00":
            lowestsell = "No Listings"
            LSactualreturn = "No Listings"
        else:
            lowestsell = "$" + lowestsellr.group(1)
            LSactualreturn = "$" + str(round((float(lowestsellr.group(1)) / 1.05) + .005, 2))  #ceil() but mathimatically
        if highestbuyr is None:
            highestbuy = "No Orders"
            BOactualreturn = "No Orders"
        else:
            BOactualreturn = highestbuyr.group(1).replace(",", "")
            highestbuy = "$" + BOactualreturn
            BOactualreturn = "$" + str(round((float(BOactualreturn) / 1.05) + .005, 2))  #ceil() but mathimatically
        global Mannco_store
        Mannco_store = ['Mannco.store', lowestsell, LSactualreturn, highestbuy, BOactualreturn]
        return

    def Mkt_tfPrices(name, driver):
        name = re.sub(r'^(Strange\s|Vintage\s|Collectors\s|Genuine\s|Haunted\s)?(Professional |Specialized )(Killstreak )(.*)$', r'\2\1\4', name)
        name = re.sub(r'^(.*)(Unusual\s)(.*)$', r'\1\3', name)
        if isUncraftable == True:
            if name.find(" Kit") > -1:
                url = f"https://marketplace.tf/items/tf2/{name}"
            else:
                url = f"https://marketplace.tf/items/tf2/uncraftable {name}"
        else:
            url = f"https://marketplace.tf/items/tf2/{name}"
        driver.get(url)
        print(f"{url}")
        lowestsellr = re.search(r'\$(\S{1,6}\.\d{2}) each', driver.page_source)
        highestbuyr = re.search(r'Active Buy Orders<\/div>\s*<div class="ta(?:.*\s*){10}<td>\$(\S{1,5}\.\d{2})', driver.page_source)
        if lowestsellr is None:
            lowestsell = "No Listings"
            LSactualreturn = "No Listings"
        else:
            LSactualreturn = lowestsellr.group(1).replace(",", "")
            lowestsell = "$" + LSactualreturn
            LSactualreturn = "$" + str(round((float(LSactualreturn) / 1.10) + .005, 2))  #ceil() but mathimatically
        if highestbuyr is None:
            highestbuy = "No Orders"
            BOactualreturn = "No Orders"
        else:
            BOactualreturn = highestbuyr.group(1).replace(",", "")
            highestbuy = "$" + BOactualreturn
            BOactualreturn = "$" + str(round((float(BOactualreturn) / 1.10) + .005, 2))  #ceil() but mathimatically

        global Marketplace_tf
        Marketplace_tf = ['Marketplace.tf', lowestsell, LSactualreturn, highestbuy, BOactualreturn]
        return

    SteamPrices(itemname)
    MCPrices(itemname, driver)
    Mkt_tfPrices(itemname, driver)
    driver.quit()                        #don't want memory leaks now do we?

    labels = ["Website", "Listing", "Listing (net)", "Buy Order", "Buy Order (net)"]
    for i in range(len(steamcommunity)):
        print("{:<20}{:<20}{:<20}{:<20}".format(labels[i], steamcommunity[i], Mannco_store[i], Marketplace_tf[i]))