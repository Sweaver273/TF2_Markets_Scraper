import src.ItemAttributes as IA
import src.markets.SteamCommunityMarket as SCM
import src.markets.Marketplacetf as MPTF
import src.markets.Manncostore as MCS
import time

while True:
    itemname = input("Provide a Market Item Name:\n")
    s = time.time()
    item_attributes = IA.GetItemAttributes(itemname)
    #print(item_attributes)
    Steam       = SCM.GetPrices(item_attributes)
    Mannco      = MCS.GetPrices(item_attributes)
    Marketplace = MPTF.GetPrices(item_attributes)
    print("[INFO] Finished in " + str(round(time.time()-s,2)) + " sec.")

    labels = ["", "Ask", "Bid", "Ask (net)", "Bid (net)"]
    row_format = "{:>15}" * (len(labels))
    print(row_format.format(*labels))
    print(row_format.format(*["Steam", Steam["Ask"], Steam["Bid"], Steam["Ask (net)"], Steam["Bid (net)"]]))
    print(row_format.format(*["Mannco", Mannco["Ask"], Mannco["Bid"], Mannco["Ask (net)"], Mannco["Bid (net)"]]))
    print(row_format.format(*["Marketplace", Marketplace["Ask"], Marketplace["Bid"], Marketplace["Ask (net)"], Marketplace["Bid (net)"]]))
