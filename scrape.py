"""
* Scrapes the http://platinumgod.co.uk site for all Isaac-Items
* Removes any Unicode-characters && quotation marks etc.
* Outputs to json file (itemdb.json)
"""

import lxml.html
from lxml.cssselect import CSSSelector
import json
import os
import glob

import requests

def generateImgUrlItems(title):
    search = title.zfill(3)
    result = glob.glob('./collectibles/' + '*' + search + '*')
    result[0] = result[0].replace('./collectibles\\', '')
    return "/collectibles/"+result[0]


url = "http://platinumgod.co.uk"
outfile = "itemdb.json"

print "Getting index of " + url
r = requests.get(url)
tree = lxml.html.fromstring(r.text)
sel = CSSSelector('li.textbox')
results = sel(tree)
items = []

print "Scraping..."

for j in range(0, 341):  # TODO: remove hardcoded values
    match = results[j]
    item_title = CSSSelector('.item-title')(match)[0].text
    item_id = CSSSelector('.r-itemid')(match)[0].text
    item_desc = CSSSelector('.pickup')(match)[0].text
    item_desc = item_desc.replace('"', '') # remove quotation mark
    item_id = item_id.replace('ItemID: ', '') # remove "ItemID"
    item_url = generateImgUrlItems(item_id)
    item_effects = []

    effect = CSSSelector('p')(match)[0].getnext().getnext().getnext()  # "move" into the effects-section

    while 1:
        text = effect.text
        if isinstance(text, unicode):
            item_effects.append(text[2:].encode("utf-8"))  # scrap unicode
            effect = effect.getnext()
        else:
            break

    items.append([])
    items[j].append(item_title)
    items[j].append(item_desc)
    items[j].append(item_id)
    items[j].append(item_effects)
    items[j].append(item_url)

for j in range(341, len(results)-1):
    match = results[j]
    item_title = CSSSelector('.item-title')(match)[0].text
    item_id = "null"
    item_url = "null"
    item_desc = CSSSelector('.pickup')(match)[0].text
    item_desc = item_desc.replace('"', '') # remove quotation mark

    item_effects = []

    effect = CSSSelector('p')(match)[0].getnext().getnext()

    while 1:
        text = effect.text
        if isinstance(text, unicode):
            item_effects.append(text[2:].encode("utf-8"))
            effect = effect.getnext()
        else:
            break

    items.append([])
    items[j].append(item_title)
    items[j].append(item_desc)
    items[j].append(item_id)
    items[j].append(item_effects)
    items[j].append(item_url)


print "Removing existing DB"
os.remove(outfile)

print "Dumping to " + outfile
fout = open(outfile, "a")
data = {"items": []}
for j in range(0, len(results)-1):
    data["items"].insert(j, {"name": items[j][0],
                             "description": items[j][1],
                             "id": items[j][2],
                             "effects": items[j][3],
                             "url": items[j][4]})

json.dump(data, fout, indent=4, sort_keys=False, separators=(',', ': '))
fout.close()