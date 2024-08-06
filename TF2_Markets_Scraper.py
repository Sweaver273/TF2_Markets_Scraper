import requests
import re
import undetected_chromedriver as uc  #https://github.com/ultrafunkamsterdam/undetected-chromedriver
import time

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
    
    item_attributes = {"craftability": item_craftability, "effect": item_effect, "strange": item_strange, "quality": item_quality, "festivized": item_festivized, "killstreaker": item_killstreaker, "name": item_name}
    return item_attributes

def SteamPrices(item_attributes):
    for key in item_attributes.keys():
        if key == 'name':
            continue
        elif item_attributes[key] != None:
            item_attributes[key] += " "
        else:
            item_attributes[key] = ""

    market_hash_name = item_attributes['strange'] + item_attributes['quality'] + item_attributes['festivized'] + item_attributes['killstreaker'] + item_attributes['name']
    market_hash_url = "https://steamcommunity.com/market/listings/440/" + market_hash_name
    if item_attributes['effect'] != "" or item_attributes['craftability'] == "Uncraftable ":
        market_hash_url += "?filter="
    if item_attributes['effect'] != "":
        market_hash_url += item_attributes['effect']
    if item_attributes['effect'] != "" and item_attributes['craftability'] == "Uncraftable ":
        market_hash_url += " "
    if item_attributes['craftability'] == "Uncraftable ":
        market_hash_url += "Not Usable in Crafting"
    #TODO: Currently, it is impossible to directly ask for only craftable items from Steam. If we did one request for all and one for uncraftables, we could subtract out to find craftables only.
    print(market_hash_url)

    #Steam market GET request for item data
    s = time.time()
    r = requests.get(market_hash_url)
    print("[DBG] Steam - Front: " + str(round(time.time()-s,4)))
    assert r.status_code == 200
    marketid = re.search(r'Market_LoadOrderSpread.*?(\d+)', r.text)
    if marketid is None:
        steamcommunity = ['Steam Community', 'No Marketid!', 'No Marketid!', 'No Marketid!', 'No Marketid!']
        return steamcommunity
    
    #If we are searching for Unusual effects/craftability, we need to scrape from the Community Market's frontend. The backend doesn't support these filtering parameters.
    #This also has a side-effect of showing each listing in the listers' native currency, which is a bit annoying. Fortunately, there are many public APIs that allow grabbing of currency conversion rates.
    #Unfortunately, this is a problem for another day.
    if market_hash_url.find("?filter=") != -1:
        lowestsellr = re.search(r'market_listing_price market_listing_price_with_fee">[\s.]{6,}\s(?P<curr>\D*)?(?P<value>[\d\.\,\ ]*)(?P<curr2>\D*)?\s{5}<\/', r.text)
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
        s = time.time()
        r = requests.get(f"https://steamcommunity.com/market/priceoverview/?appid=440&currency=1&market_hash_name={market_hash_name}")
        print("[DBG] Steam - Backend: " + str(round(time.time()-s,4)))
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
    s = time.time()
    r = requests.get(f"https://steamcommunity.com/market/itemordershistogram?country=US&language=english&currency=1&item_nameid={marketid.group(1)}&two_factor=0")
    print("[DBG] Steam - BuyAPI: " + str(round(time.time()-s,4)))
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

def MCPrices(name, item_attributes, driver): #TODO: Less regex, more logic using item_attributes
    name = name.lower()
    name = name.replace(" ", "-")
    punc = '!()[]{};:\'\"\\,<>./?@#$%^&*_~'
    for ele in name:
        if ele in punc:
            name = name.replace(ele, "")
    if item_attributes['craftability'] == "Uncraftable" or item_attributes['name'].find("Kit") != -1:
        url = f"https://mannco.store/item/440-uncraftable-{name}"
    else:
        url = f"https://mannco.store/item/440-{name}"
    print(url)
    
    s = time.time()
    driver.get(url)
    print("[DBG] Mannco: " + str(round(time.time()-s,4)))
    
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
    return Mannco_store

def Mkt_tfPrices(name, item_attributes, driver):
    isWeaponEffect = bool(re.search(r'Hot|Isotope|Cool|Energy Orb', item_attributes['effect']))
    #regex = r"^(?:(?P<effect>"+'|'.join(effects)+r")\s)?(?:(?P<quality>Vintage|Collectors|Strange Geniune|Strange Haunted|Genuine|Haunted|Strange)\s)?(?P<unusual>Unusual)?\s?(?:(?P<festivized>Festivized)\s)?(?:(?P<killstreak>Specialized|Professional|Basic Killstreak)\s)?(?P<item>.*)$"
    mktname = ""
    
    if item_attributes['craftability'] != "":
        mktname += item_attributes['craftability']
    
    if item_attributes['killstreaker'] == "Professional Killstreak ":
        mktname += "Professional "
    elif item_attributes['killstreaker'] == "Specialized Killstreak ":
        mktname += "Specialized "
    elif item_attributes['killstreaker'] == "Killstreak ":
        mktname += "Basic Killstreak " #Odd inconsistency but okay
        
    if item_attributes['strange'] != "":
        mktname += "Strange "
        
    if item_attributes['quality'] != "":
        mktname += item_attributes['quality']
    
    if item_attributes['effect'] != "":
        if item_attributes['effect'] in ["Hot", "Isotope", "Cool", "Energy Orb"]:
            mktname += "★" + item_attributes['effect']
        else:
            mktname += item_attributes['effect']

    if item_attributes['festivized'] != "":
        mktname += item_attributes['festivized']

    mktname += item_attributes['name']
    url = f"https://marketplace.tf/items/tf2/{mktname}"
    print(url)
    s = time.time()
    driver.get(url)
    #print("[DBG] Marketplace.tf: "+ str(round(time.time()-s,4)))

    lowestsellr = re.search(r'<\/td>\s.*<td>\$(\d+\.\d{2})', driver.page_source)
    highestbuyr = re.search(r'<tr>\s.*<td>\$(\d+\.\d{2})', driver.page_source)
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
    return Marketplace_tf

IsDriverRunning = False
while True:
    itemname = input("Provide a Market Item Name:\n")
    s = time.time()
    item_attributes = GetItemAttributes(itemname)
    print("[DBG] Item attributes set.")
    steamcommunity = SteamPrices(item_attributes)
    try:
        print("[DBG] Initializing driver")
        driver = uc.Chrome(headless=False) #UC will send Chrome's 'headless' header to the destination site, which triggers cloudflare detection. There's probably an easy fix here.
        
        IsDriverRunning = True
        print("[DBG] Driver initialized.")
        Mannco_store = MCPrices(itemname, item_attributes, driver) #TODO: stop passing itemname, start using item_attributes
        Marketplace_tf = Mkt_tfPrices(itemname, item_attributes, driver)
        print("[DBG] Completed successfully in " + str(round(time.time-s,4)))
        driver.close()
        driver.quit()
        IsDriverRunning = False
    except KeyboardInterrupt:
        if IsDriverRunning == True:
            driver.close()
            driver.quit()
        break
    except Exception as e:
        print(e)
        if IsDriverRunning == True:
            driver.close()
            driver.quit()
        IsDriverRunning = False

    labels = ["Website", "Listing", "Buy Order", "Listing (Revenue)", "Buy Order (Revenue)"]
    for i in range(len(steamcommunity)):
        print("{:<20}{:<20}{:<20}{:<20}".format(labels[i], steamcommunity[i], Mannco_store[i], Marketplace_tf[i]))
