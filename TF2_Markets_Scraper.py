import requests
import re
import undetected_chromedriver as uc  #https://github.com/ultrafunkamsterdam/undetected-chromedriver

getparticles = requests.get("https://backpack.tf/developer/particles").text
effectsraw = re.findall(r"<\/small> (.*)", getparticles)
effects = [effect.replace('&#039;', "'") for effect in effectsraw]

def SteamPrices(item):
        global steamcommunity
        global isUncraftable

        regex = r"^(?:(?P<effect>"+'|'.join(effects)+r")\s)?(?:(?P<quality>Vintage|Collectors|Strange Geniune|Strange Haunted|Genuine|Haunted|Strange)\s)?(?P<unusual>Unusual)?\s?(?:(?P<festivized>Festivized)\s)?(?:(?P<killstreak>Specialized Killstreak|Professional Killstreak|Killstreak)\s)?(?P<item>.*)$"
        market_hash_name = re.sub(regex, r"\g<quality> \g<unusual> \g<festivized> \g<killstreak> \g<item>", item)
        market_hash_name = ' '.join(market_hash_name.split())
        params = re.sub(regex, r"\g<effect>", item)
        market_hash_url = "https://steamcommunity.com/market/listings/440/" + market_hash_name + '?filter=' + params
        print(market_hash_url)

        #Steam market GET request for item data
        response = requests.get(market_hash_url)
        if response.status_code == 200:
            global marketid
            marketid = re.search(r'Market_LoadOrderSpread.*?(\d+)', response.text)
            if marketid is None:
                steamcommunity = ['Steam Community', 'No Marketid!', 'No Marketid!', 'No Marketid!', 'No Marketid!']
                isUncraftable = False #This shouldn't matter because every item should have a marketid, but it's here just in case.
                return
            isUncraftable = bool(re.search(r'Not Usable in Crafting', response.text))

            #If we are searching for Unusual effects, we need to scrape from the Community Market's frontend. Backend doesn't support these parameters.
            #This also has a side-effect of showing each listing in the listers' native currency, which is a bit annoying. Would be cool to eventually convert these values.
            if params:
                lowestsellr = re.search(r'market_listing_price market_listing_price_with_fee">[\s.]{6,}\s(?P<curr>\D*)?(?P<value>[\d\.\,\ ]*)(?P<curr2>\D*)?\s{5}<\/', response.text)
                if lowestsellr is None:
                    lowestsell = "No Listings"
                    LSactualreturn = "No Listings"
                else:
                    lowestsell = float(re.sub(r'[^\d]', "", lowestsellr.group('value')))
                    lowestsell = lowestsell / 100
                    LSactualreturn = lowestsellr.group('curr') + str("{:.2f}".format(round((float(lowestsell) / 1.15) + .005, 2))) + lowestsellr.group('curr2')
                    lowestsell = lowestsellr.group('curr') + "{0:.2f}".format(lowestsell) + lowestsellr.group('curr2')

        else:
            raise Exception(f"Steam returned code {response.status_code} fetching sell orders. This shouldn't happen.")

        #Backend request
        if params == "":
            response = requests.get(f"https://steamcommunity.com/market/priceoverview/?appid=440&currency=1&market_hash_name={market_hash_name}")
            if response.status_code == 200:
                lowestsellr = re.search(r'lowest_price":"\$(\S{1,6}\.\d{2})"', response.text)
                if lowestsellr is None:
                    lowestsell = "No Listings"
                    LSactualreturn = "No Listings"
                else:
                    lowestsell = "$" + "{:.2f}".format(float(lowestsellr.group(1)))
                    LSactualreturn = "$" + str("{:.2f}".format(round((float(lowestsellr.group(1)) / 1.15) + .005, 2)))
            elif response.status_code == 429: #Ratelimits are more lenient here, presumably because it is requested a lot less
                lowestsell = "Ratelimited"
                LSactualreturn = "Ratelimited"
            else:
                lowestsell = "N/A"
                LSactualreturn = "N/A"

        #Steam Buyorders - this backend link is the ONLY OPTION for grabbing buy order data. The market page will make calls to this constantly when open.
        response = requests.get(f"https://steamcommunity.com/market/itemordershistogram?country=US&language=english&currency=1&item_nameid={marketid.group(1)}&two_factor=0")
        if response.status_code == 200:
            highestbuyr = re.search(r'to buy at.*?\$(\S{1,6}\.\d{2})', response.text)
            if highestbuyr is None:
                BOactualreturn = "No Orders"
                highestbuy = "No Orders"
            else:
                BOactualreturn = highestbuyr.group(1).replace(",", "")
                highestbuy = "$" + "{:.2f}".format(float(BOactualreturn))
                BOactualreturn = "$" + str("{:.2f}".format(round((float(BOactualreturn) / 1.15) + .005, 2)))
        elif response.status_code == 429: #Ratelimits are stricter here because of continuous calls when market pages are open. Typically last 5 minutes
            highestbuy = "Ratelimited"
            BOactualreturn = "Ratelimited"
        else:
            highestbuy = "N/A"
            BOactualreturn = "N/A"

        steamcommunity = ['Steam Community', lowestsell, highestbuy, LSactualreturn, BOactualreturn]
        return

def MCPrices(name, driver):
    global Mannco_store

    name = name.lower()
    name = name.replace(" ", "-")
    punc = '''!()[]{};:'"\,<>./?@#$%^&*_~'''
    for ele in name:
        if ele in punc:
            name = name.replace(ele, "")
    if isUncraftable == True:
        url = f"https://mannco.store/item/440-uncraftable-{name}"
    else:
        url = f"https://mannco.store/item/440-{name}"
    driver.get(url)
    print(f"{url}")
    lowestsellr = re.search(r'lowPrice": "(\d+\.\d{2})', driver.page_source)
    highestbuyr = re.search(r'Quantity(?:<.*>\s)*?<td>\$(\S{1,6}\.\d{2})', driver.page_source)
    if lowestsellr is None or lowestsellr.group(1) == "0.00": #this is the listed price if there are no listings - None is a failsafe
        lowestsell = "No Listings"
        LSactualreturn = "No Listings"
    else:
        lowestsell = "$" + "{:.2f}".format(float(lowestsellr.group(1)))
        LSactualreturn = "$" + str("{:.2f}".format(round((float(lowestsellr.group(1)) / 1.05) + .005, 2)))

    if highestbuyr is None:
        highestbuy = "No Orders"
        BOactualreturn = "No Orders"
    else:
        BOactualreturn = highestbuyr.group(1).replace(",", "")
        highestbuy = "$" + "{:.2f}".format(float(BOactualreturn))
        BOactualreturn = "$" + str("{:.2f}".format(round((float(BOactualreturn) / 1.05) + .005, 2)))
    Mannco_store = ['Mannco.store', lowestsell, highestbuy, LSactualreturn, BOactualreturn]
    return

def Mkt_tfPrices(name, driver):
    global Marketplace_tf

    isWeaponEffect = bool(re.search(r'Hot|Isotope|Cool|Energy Orb', name))
    regex = r"^(?:(?P<effect>"+'|'.join(effects)+r")\s)?(?:(?P<quality>Vintage|Collectors|Strange Geniune|Strange Haunted|Genuine|Haunted|Strange)\s)?(?P<unusual>Unusual)?\s?(?:(?P<festivized>Festivized)\s)?(?:(?P<killstreak>Specialized|Professional|Basic Killstreak)\s)?(?P<item>.*)$"

    name = re.sub(r"(Professional|Specialized) Killstreak", r"\1", name)
    name = name.replace("Killstreak", "Basic Killstreak")
    if isWeaponEffect == True:
        name = re.sub(regex, r'\g<killstreak> \g<quality> ★\g<effect> \g<festivized> \g<item>', name)
    else:
        name = re.sub(regex, r'\g<killstreak> \g<quality> \g<effect> \g<festivized> \g<item>', name)
    name = ' '.join(name.split())
    if isUncraftable == True:
        if name.find(" Kit") > -1:
            url = f"https://marketplace.tf/items/tf2/{name}"
        else:
            url = f"https://marketplace.tf/items/tf2/Uncraftable {name}"
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
        lowestsell = "$" + "{:.2f}".format(float(LSactualreturn))
        LSactualreturn = "$" + str("{:.2f}".format(round((float(LSactualreturn) / 1.10) + .005, 2)))
    if highestbuyr is None:
        highestbuy = "No Orders"
        BOactualreturn = "No Orders"
    else:
        BOactualreturn = highestbuyr.group(1).replace(",", "")
        highestbuy = "$" + "{:.2f}".format(float(BOactualreturn))
        BOactualreturn = "$" + str("{:.2f}".format(round((float(BOactualreturn) / 1.10) + .005, 2)))

    Marketplace_tf = ['Marketplace.tf', lowestsell, highestbuy, LSactualreturn, BOactualreturn]
    return

while True:
    itemname = input("Provide a Market Item Name:\n")
    try:
        SteamPrices(itemname)
        driver = uc.Chrome(headless=True, version_main=112) #initialize the driver while the user is inputting an item name
        MCPrices(itemname, driver)
        Mkt_tfPrices(itemname, driver)
        driver.quit()
    except:
        driver.quit()
        raise Exception("Unhandled exception occured. Closing the driver.")

    labels = ["Website", "Listing", "Buy Order", "Listing (Revenue)", "Buy Order (Revenue)"]
    for i in range(len(steamcommunity)):
        print("{:<20}{:<20}{:<20}{:<20}".format(labels[i], steamcommunity[i], Mannco_store[i], Marketplace_tf[i]))