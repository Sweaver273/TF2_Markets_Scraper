import re

def GetItemAttributes(user_input):
    #I decided to break the one large regular expression into multiple smaller ones, as it significantly improved matching accuracy.
    #There are so many conditional 'attributes' in a TF2 item's name that trying to use a singular regex to capture all elements became unreasonably difficult.
    
    #TODO: Add weapon wear. For now, it seems fine to store as part of the item name.
    
    r = re.compile(r"^.*?(?P<quality>Vintage|Collectors|Genuine|Haunted|Normal|Unusual|Self-Made|Unique)")
    m = r.match(user_input)
    if m == None:
        item_quality = None #Since stranges are excluded here, a NoneType is appropriate (still allows for strange unique items in the lookup)
    else:
        item_quality = m.group('quality')
    
    r = re.compile(r"(?:(?P<craftability>Uncraftable|Craftable)\s)?.+")
    m = r.match(user_input)
    if m == None:
        item_craftability = None #Leaving this as none will allow 3rd party websites to autofill best match.
    else:
        item_craftability = m.group("craftability")
    
    r = re.compile(r"^.*?(?P<strange>Strange)")
    m = r.match(user_input)
    if m == None:
        item_strange = None
    else:
        item_strange = "Strange"
    
    r = re.compile(r"^.*?(?P<festivized>Festivized)")
    m = r.match(user_input)
    if m == None:
        item_festivized = None
    else:
        item_festivized = m.group("festivized")
    
    r = re.compile(r"^.*?(?P<killstreaker>Specialized Killstreak|Professional Killstreak|Killstreak)")
    m = r.match(user_input)
    if m == None:
        item_killstreaker = None
    else:
        item_killstreaker = m.group("killstreaker")
    
    if item_quality == "Unusual" or item_quality == "Vintage": #Vintage community sparkle lugermorph applies here.
        if item_craftability != None:
            effect_regex = r"^" + item_craftability + r" " + r"(?P<effect>.+)"
        else:
            effect_regex = r"^(?P<effect>.+)"
        if item_strange == "Strange":
            effect_regex += r" " + item_strange #Need to anchor on Stange quality if present.
        effect_regex += r" " + item_quality #Add quality to the anchor point.
        
        r = re.compile(effect_regex)
        m = r.match(user_input)
        if m == None:
            item_effect = None
        else:
            item_effect = m.group("effect")
    else:
        item_effect = None
    
    #Remove matched components from the user's string so we can end up with just the item name.
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
    
    #Here, we can add any last-second checks for items that have forced attributes. This helps websites that don't automatically resolve these.
    #Set killstreak kits to be uncraftable.
    if item_name.find("Kit Fabricator") == -1:
        if item_name.find("Kit") != -1:
            item_craftability = "Uncraftable"
    
    item_attributes = {"craftability": item_craftability, "effect": item_effect, "strange": item_strange, "quality": item_quality, "festivized": item_festivized, "killstreaker": item_killstreaker, "name": item_name}
    return item_attributes
