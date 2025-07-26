import requests
import re
import time

def GetPrices(item_attributes):
    market_hash_name = ""
    market_filter = ""
    if item_attributes['strange'] != None:
        market_hash_name += item_attributes['strange'] + " "
    if item_attributes['quality'] != None and item_attributes['quality'] != "Unique": #Unique quality is discarded from the name.
        market_hash_name += item_attributes['quality'] + " "
    if item_attributes['festivized'] != None:
        market_hash_name += item_attributes['festivized'] + " "
    if item_attributes['killstreaker'] != None:
        market_hash_name += item_attributes['killstreaker'] + " "
    
    market_hash_name += item_attributes['name']
    
    if item_attributes['craftability'] != None or item_attributes['effect'] != None:
        market_filter += "?filter="
        #Could add strange part lookups, custom names/descriptions?, 
        if item_attributes['craftability'] == "Uncraftable":
            #NOTE: Currently, it is impossible to directly ask for only craftable items from Steam.
            market_filter += "Not+Usable+in+Crafting+"
        if item_attributes['effect'] != None:
            market_filter += item_attributes['effect'] + "+"
    
    market_hash_url = "https://steamcommunity.com/market/listings/440/" + market_hash_name + market_filter
    #print(market_hash_url)

    #Steam Frontend
        #To my knowledge, there's no ratelimit here.
    s = time.time()
    r = requests.get(market_hash_url)
    print("[INFO] Steam Frontend: " + str(round((time.time()-s)*1000,0)) + " ms.")
    assert r.status_code == 200
    marketid = re.search(r'Market_LoadOrderSpread.*?(\d+)', r.text)
    if marketid is None:
        steamcommunity = ['Steam Community', 'No Marketid!', 'No Marketid!', 'No Marketid!', 'No Marketid!']
        return steamcommunity
    
    #If we are searching for Unusual effects/craftability, we need to scrape from the Community Market's frontend. 
    #Eventually, we should try to only use this request and process currency conversions to avoid API IP ratelimits.
    #This also has a side-effect of showing each listing in the listers' native currency, which is a bit annoying.
    if market_hash_url.find("?filter=") != -1:
        lowestsellr = re.search(r'market_listing_price market_listing_price_with_fee">[\s.]{6,}\s(?P<curr>\D*)?(?P<value>[\d\.\,\ ]*)(?P<curr2>\D*)?\s{5}<\/', r.text)
        if lowestsellr is None:
            lowestsell = None
            LSactualreturn = None
        else:
            lowestsell = float(re.sub(r'[^\d]', "", lowestsellr.group('value')))
            lowestsell = lowestsell / 100
            
            #TODO: Review this callculation for actual return
            LSactualreturn = lowestsellr.group('curr') + str("{:.2f}".format(round((float(lowestsell) / 1.15) + .005, 2))) + lowestsellr.group('curr2')
            lowestsell = lowestsellr.group('curr') + "{0:.2f}".format(lowestsell) + lowestsellr.group('curr2')
    
    #Backend request
        #The ratelimit is 20/min, 1000/day, which is lenient but would suck if trying to price entire inventories.
    if market_hash_url.find("?filter=") == -1:
        s = time.time()
        r = requests.get(f"https://steamcommunity.com/market/priceoverview/?appid=440&currency=1&market_hash_name={market_hash_name}")
        print("[INFO] Steam Backend: " + str(round((time.time()-s)*1000,0)) + " ms.")
        assert r.status_code == 200 or r.status_code == 429
        if r.status_code == 429:
            lowestsell = "Ratelimited"
            LSactualreturn = "Ratelimited"
        else:
            lowestsellr = re.search(r'lowest_price":"\$(\S{1,6}\.\d{2})"', r.text)
            if lowestsellr is None:
                lowestsell = None
                LSactualreturn = None
            else:
                #Since we specify currency=1, USD will always be returned.
                lowestsell = "$" + "{:.2f}".format(float(lowestsellr.group(1)))

                #TODO: Review this callculation for actual return
                LSactualreturn = "$" + str("{:.2f}".format(round((float(lowestsellr.group(1)) / 1.15) + .005, 2)))
    
    #Steam Buyorders
        #Ratelimit: 10 different items per hour. The same item is allowed to repeat w/o limit.
        #This backend API is the ONLY OPTION for grabbing buy order data.
    s = time.time()
    r = requests.get(f"https://steamcommunity.com/market/itemordershistogram?country=US&language=english&currency=1&item_nameid={marketid.group(1)}&two_factor=0")
    print("[INFO] Steam - BuyAPI: " + str(round((time.time()-s)*1000,0)) + " ms.")
    assert r.status_code == 200 or r.status_code == 429
    if r.status_code == 429:
            lowestsell = "Ratelimited"
            LSactualreturn = "Ratelimited"
    else:
        highestbuyr = re.search(r'to buy at.*?\$(\S{1,6}\.\d{2})', r.text)
        if highestbuyr is None:
            BOactualreturn = None
            highestbuy = None
        else:
            BOactualreturn = highestbuyr.group(1).replace(",", "")
            highestbuy = "$" + "{:.2f}".format(float(BOactualreturn))

            #TODO: Review this callculation for actual return
            BOactualreturn = "$" + str("{:.2f}".format(round((float(BOactualreturn) / 1.15) + .005, 2)))

    prices = {"Ask": lowestsell, "Bid": highestbuy, "Ask (net)": LSactualreturn, "Bid (net)": BOactualreturn}
    return prices
