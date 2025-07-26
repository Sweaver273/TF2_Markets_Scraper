import cloudscraper
import re
import time

def GetPrices(item_attributes):
    item_urlname = ""
    
    #Run-through all attributes, adjusting for any website-specific handling.
    if item_attributes['craftability'] == "Uncraftable": #mannco handles craftability by presence of the 'uncraftable' attribute.
        item_urlname += item_attributes['craftability'] + "-"
    if item_attributes['effect'] != None:
        item_urlname += item_attributes['effect'] + "-"
    if item_attributes['strange'] != None:
        item_urlname += item_attributes['strange'] + "-"
    if item_attributes['quality'] != None and item_attributes['quality'] != "Unique": #Unique quality is discarded from the name.
        item_urlname += item_attributes['quality'] + "-"
    if item_attributes['festivized'] != None:
        item_urlname += item_attributes['festivized'] + "-"
    if item_attributes['killstreaker'] != None:
        item_urlname += item_attributes['killstreaker'] + "-"
    item_urlname += item_attributes['name']
    
    #Adjust to Mannco's formatting.
    item_urlname = item_urlname.lower()
    item_urlname = item_urlname.replace(" ", "-") #Some items have spaces that mannco wants coverted to dashes.
    punc = '!()[]{};:\'\"\\,<>./?@#$%^&*_~'
    for ele in item_urlname:
        if ele in punc:
            item_urlname = item_urlname.replace(ele, "") #Mannco discards punctuation from URL encoding.
    
    url = f"https://mannco.store/item/440-{item_urlname}"
    #print(url)
    s = time.time()
    cs = cloudscraper.create_scraper()
    r = cs.get(url)
    assert r.status_code == 200
    print("[INFO] Mannco responded in: " + str(round((time.time()-s)*1000,0)) + " ms.")
    
    lowestsellr = re.search(r'lowPrice": "(\d+\.\d{2})', r.text)
    highestbuyr = re.search(r'Quantity(?:<.*>\s+)*?<td\s?>\$(\S{1,6}\.\d{2})', r.text)
    if lowestsellr is None or lowestsellr.group(1) == "0.00": #this is the listed price if there are no listings - None is a failsafe
        lowestsell = None
        LSactualreturn = None
    else:
        lowestsell = "$" + "{:.2f}".format(float(lowestsellr.group(1)))
        LSactualreturn = "$" + str("{:.2f}".format(round((float(lowestsellr.group(1)) / 1.05) + .005, 2)))

    if highestbuyr is None:
        highestbuy = None
        BOactualreturn = None
    else:
        BOactualreturn = highestbuyr.group(1).replace(",", "")
        highestbuy = "$" + "{:.2f}".format(float(BOactualreturn))
        BOactualreturn = "$" + str("{:.2f}".format(round((float(BOactualreturn) / 1.05) + .005, 2)))

    prices = {"Ask": lowestsell, "Bid": highestbuy, "Ask (net)": LSactualreturn, "Bid (net)": BOactualreturn}
    return prices
