import cloudscraper #Lightweight Cloudflare Bypass
import re
import time

def GetPrices(item_attributes):
    mktname = ""
    
    #Run-through all attributes, adjusting for any website-specific handling.
    if item_attributes['craftability'] == "Uncraftable" and item_attributes['name'].find("Kit") == -1:
        mktname += "Uncraftable "
    if item_attributes['killstreaker'] == "Professional Killstreak":
        mktname += "Professional "
    elif item_attributes['killstreaker'] == "Specialized Killstreak":
        mktname += "Specialized "
    elif item_attributes['killstreaker'] == "Killstreak":
        mktname += "Basic Killstreak " #Odd inconsistency but okay
    if item_attributes['strange'] != None:
        mktname += "Strange "
    if item_attributes['quality'] != None and item_attributes['quality'] != "Unusual": 
        mktname += item_attributes['quality']
    if item_attributes['effect'] != None:
        if item_attributes['effect'] in ["Hot", "Isotope", "Cool", "Energy Orb"]: #Watch out for new weapon unusual effects.
            mktname += "%E2%98%85" + item_attributes['effect'] + " " #Unicode: ★
        else:
            mktname += item_attributes['effect'] + " "
    if item_attributes['festivized'] != None:
        mktname += item_attributes['festivized'] + " "
    
    mktname += item_attributes['name']
    
    url = f"https://marketplace.tf/items/tf2/{mktname}"
    #print(url)

    cs = cloudscraper.create_scraper()
    s = time.time()
    r = cs.get(url)
    assert r.status_code == 200
    print("[INFO] mp.tf responded in: "+ str(round((time.time()-s)*1000,0)) + " ms.")

    lowestsellr = re.search(r'<\/td>\s.*<td>\$(\d{1,3}(?:,\d{3})*(?:\.\d+)?)', r.text)
    highestbuyr = re.search(r'<tr>\s.*<td>\$(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',  r.text)
    if lowestsellr is None:
        lowestsell = None
        LSactualreturn = None
    else:
        LSactualreturn = lowestsellr.group(1).replace(",", "")
        lowestsell = "$" + "{:.2f}".format(float(LSactualreturn))
        LSactualreturn = "$" + str("{:.2f}".format(round((float(LSactualreturn) / 1.10) + .005, 2)))
    if highestbuyr is None:
        highestbuy = None
        BOactualreturn = None
    else:
        BOactualreturn = highestbuyr.group(1).replace(",", "")
        highestbuy = "$" + "{:.2f}".format(float(BOactualreturn))
        BOactualreturn = "$" + str("{:.2f}".format(round((float(BOactualreturn) / 1.10) + .005, 2)))

    #Marketplace_tf = ['Marketplace.tf', lowestsell, highestbuy, LSactualreturn, BOactualreturn] #This should really just be a dict
    prices = {"Ask": lowestsell, "Bid": highestbuy, "Ask (net)": LSactualreturn, "Bid (net)": BOactualreturn}
    return prices
