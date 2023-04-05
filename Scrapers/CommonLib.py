import requests
import json


def BeverGetReviewsFromURL(url:str):
   skuNr = url.split("-")[-1].split(".")[0]
   request = requests.get("https://widgets.reevoo.com/api/product_reviews?per_page=3&trkref=BEV&sku="+skuNr+"&locale=nl-NL&display_mode=embedded&page=1")
   if(request.ok):
    data = json.loads(request.content)

    nrOfPages = int(data["body"]["pagination"]["total_pages"])



    
def BeverGetReviewFromURL(url:str, pagenr:int):
    request = requests.get("https://widgets.reevoo.com/api/product_reviews?per_page=3&trkref=BEV&sku="+skuNr+"&locale=nl-NL&display_mode=embedded&page=1")
    data = json.loads(request.content)
    data = data["body"]["reviews"]
    
    rating = []
    goodPoints = []
    badpoints = []
    
    for thingy in data:
        rating.append(thingy["overall_score"])
        goodPoints.append(thingy["text"]["good_points"])
        badpoints.append(thingy["text"]["bad_points"])    
    with open("out.json", 'w', encoding="utf8", newline="") as out:
        json.dump(data, out)   
   
    
    
BeverGetReviewsFromURL("https://www.bever.nl/p/ayacucho-annapurna-softshell-B12AD90130.html?colour=4168")