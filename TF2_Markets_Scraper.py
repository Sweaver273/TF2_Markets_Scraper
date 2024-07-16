import requests
import re
import undetected_chromedriver as uc  #https://github.com/ultrafunkamsterdam/undetected-chromedriver

def GetItemAttributes(user_input):
    #I decided to break the one large regular expression into multiple smaller ones, as it significantly improved matching accuracy.
    #There are so many conditional 'parameters' in a TF2 item's name that using python logic was much more appropriate here than I had initially anticipated.
    #We can also skip a request to backpack.tf by doing this too.

    r = re.compile("^.*?(?P<quality>Vintage|Collectors|Genuine|Haunted|Normal|Unusual|Self-Made|Unique)")
    m = r.match(user_input)
    if m == None:
        item_quality = None
    else:
        item_quality = m.group('quality')
    
    r = re.compile("(?:(?P<craftability>Uncraftable|Craftable)\s)?.+")
    m = r.match(user_input)
    if m == None:
        item_craftability = None
    else:
        item_craftability = m.group("craftability")
        if item_craftability == "Uncraftable":
            global isUncraftable = True #Quick fix
    
    r = re.compile("^.*?(?P<strange>Strange)")
    m = r.match(user_input)
    if m == None:
        item_strange = None
    else:
        item_strange = m.group("strange")
    
    r = re.compile("^.*?(?P<festivized>Festivized)")
    m = r.match(user_input)
    if m == None:
        item_festivized = None
    else:
        item_festivized = m.group("festivized")
    
    r = re.compile("^.*?(?P<killstreaker>Specialized Killstreak|Professional Killstreak|Killstreak)")
    m = r.match(user_input)
    if m == None:
        item_killstreaker = None
    else:
        item_killstreaker = m.group("killstreaker")
    
    if item_quality == "Unusual" or item_quality == "Vintage":
        if item_craftability != None:
            effect_regex = "^" + item_craftability + " " + "(?P<effect>.+)"
        else:
            effect_regex = "^(?P<effect>.+)"
        if item_strange == "Strange":
            effect_regex += " " + item_strange
        effect_regex += " " + item_quality
        
        r = re.compile(effect_regex)
        m = r.match(user_input)
        if m == None:
            item_effect = None
        else:
            item_effect = m.group("effect")
    else:
        item_effect = None
    
    x = user_input
    if item_craftability != None:
        x = x.replace(item_craftability + " ", "")
    if item_effect != None:
        x = x.replace(item_effect + " ", "")
    if item_strange != None:
        x = x.replace(item_strange + " ", "")
    if item_quality != None:
        x = x.replace(item_quality + " ", "")
    if item_festivized != None:
        x = x.replace(item_festivized + " ", "")
    if item_killstreaker != None:
        x = x.replace(item_killstreaker + " ", "")
    item_name = x
    
    item = {"craftability": item_craftability, "effect": item_effect, "strange": item_strange, "quality": item_quality, "festivized": item_festivized, "killstreaker": item_killstreaker, "name": item_name}
    return item

def SteamPrices(item):
    for key in item.keys():
        if key == 'name':
            continue
        elif item[key] != None:
            item[key] += " "
        else:
            item[key] = ""

    market_hash_name = item['strange'] + item['quality'] + item['festivized'] + item['killstreaker'] + item['name']
    market_hash_url = "https://steamcommunity.com/market/listings/440/" + market_hash_name
    if item['effect'] != "" or item['craftability'] == "Uncraftable ":
        market_hash_url += "?filter="
    if item['effect'] != "":
        market_hash_url += item['effect']
    if item['effect'] != "" and item['craftability'] == "Uncraftable ":
        market_hash_url += " "
    if item['craftability'] == "Uncraftable ":
        market_hash_url += "Not Usable in Crafting"
    #TODO: Currently, it is impossible to directly ask for only craftable items from Steam. If we did one request for all and one for uncraftables, we could subtract out to find craftables only.
    print(market_hash_url)

    #Steam market GET request for item data
    r = requests.get(market_hash_url)
    assert r.status_code == 200
    marketid = re.search(r'Market_LoadOrderSpread.*?(\d+)', r.text)
    if marketid is None:
        steamcommunity = ['Steam Community', 'No Marketid!', 'No Marketid!', 'No Marketid!', 'No Marketid!']
        return
    
    #If we are searching for Unusual effects/craftability, we need to scrape from the Community Market's frontend. The backend doesn't support these filtering parameters.
    #This also has a side-effect of showing each listing in the listers' native currency, which is a bit annoying. Fortunately, there are many public APIs that allow grabbing of currency conversion rates.
    #Unfortunately, this is a problem for another day.
    if market_hash_url.find("?filter=") != -1:
        lowestsellr = re.search(r'market_listing_price market_listing_price_with_fee">[\s.]{6,}\s(?P<curr>\D*)?(?P<value>[\d\.\,\ ]*)(?P<curr2>\D*)?\s{5}<\/', response.text)
        if lowestsellr is None:
            lowestsell = "No Listings"
            LSactualreturn = "No Listings"
        else:
            lowestsell = float(re.sub(r'[^\d]', "", lowestsellr.group('value')))
            lowestsell = lowestsell / 100
            LSactualreturn = lowestsellr.group('curr') + str("{:.2f}".format(round((float(lowestsell) / 1.15) + .005, 2))) + lowestsellr.group('curr2')
            lowestsell = lowestsellr.group('curr') + "{0:.2f}".format(lowestsell) + lowestsellr.group('curr2')

    #Backend request
    if market_hash_url.find("?filter=") == -1:
        r = requests.get(f"https://steamcommunity.com/market/priceoverview/?appid=440&currency=1&market_hash_name={market_hash_name}")
        assert r.status_code == 200 or r.status_code == 429
        if r.status_code == 429: #Ratelimits are more lenient here, presumably because it is requested a lot less
            lowestsell = "Ratelimited"
            LSactualreturn = "Ratelimited"
        else:
            lowestsellr = re.search(r'lowest_price":"\$(\S{1,6}\.\d{2})"', r.text)
            if lowestsellr is None:
                lowestsell = "No Listings"
                LSactualreturn = "No Listings"
            else:
                lowestsell = "$" + "{:.2f}".format(float(lowestsellr.group(1)))
                LSactualreturn = "$" + str("{:.2f}".format(round((float(lowestsellr.group(1)) / 1.15) + .005, 2)))

    #Steam Buyorders - this backend link is the ONLY OPTION for grabbing buy order data. This has led to Steam HEAVILY ratelimiting this endpoint, which sucks for us.
    r = requests.get(f"https://steamcommunity.com/market/itemordershistogram?country=US&language=english&currency=1&item_nameid={marketid.group(1)}&two_factor=0")
    assert r.status_code == 200 or r.status_code == 429
    if r.status_code == 429: #Common outcome
            lowestsell = "Ratelimited"
            LSactualreturn = "Ratelimited"
    else:
        highestbuyr = re.search(r'to buy at.*?\$(\S{1,6}\.\d{2})', r.text)
        if highestbuyr is None:
            BOactualreturn = "No Orders"
            highestbuy = "No Orders"
        else:
            BOactualreturn = highestbuyr.group(1).replace(",", "")
            highestbuy = "$" + "{:.2f}".format(float(BOactualreturn))
            BOactualreturn = "$" + str("{:.2f}".format(round((float(BOactualreturn) / 1.15) + .005, 2)))

    steamcommunity = ['Steam Community', lowestsell, highestbuy, LSactualreturn, BOactualreturn]
    return steamcommunity

def MCPrices(name, driver):
    global Mannco_store

    name = name.lower()
    name = name.replace(" ", "-")
    punc = '!()[]{};:\'\"\\,<>./?@#$%^&*_~'
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
    item = GetItemAttributes(itemname)
    SteamPrices(itemname)
    #TODO: Review MCPrices and Mkt_tfPrices functions
    try:
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
