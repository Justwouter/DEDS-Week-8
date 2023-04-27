from csv import writer,DictWriter
import os
import requests
import json

outfile = os.path.dirname(__file__)+"/output/data"
storageList = []

#======File managment=======

def BeverAPIWriteDataToJsonFile():
    with open(outfile+".json", 'w', encoding="utf8", newline="") as out:
        
        json.dump(storageList, out, ensure_ascii=False)  
        # out.write(json.dumps(storageList, ensure_ascii=False).encode("utf8").decode())
        
def BeverAPIWriteDataToCSVFile():
    with open(outfile+".csv", 'w', encoding="utf8", newline="") as out:
        write = DictWriter(out, fieldnames=storageList[0].keys())
        write.writeheader()
        for entry in storageList:
            write.writerow(entry)
            
def BeverAPIWriteDataAsLinesToCSVFile():
    with open(outfile+".csv", 'w', encoding="utf8", newline="") as out:
        write = writer(out)
        for entry in storageList:
            for item in range(len(entry["badpoints"])):
                write.writerow([entry["sku"],entry["score"][item],entry["goodpoints"][item],entry["badpoints"][item]])
                
                
def BeverAPIWriteReviewsLooseLiness():
    with open(outfile+".txt", 'w', encoding="utf8", newline="") as out:
        write = writer(out)
        for entry in storageList:
            for item in range(len(entry["badpoints"])):
                write.writerow([entry["sku"],entry["badpoints"][item]])
            for item in range(len(entry["goodpoints"])):
                    write.writerow([entry["sku"],entry["goodpoints"][item]])
                
                
                
                

#======Helpers===========

def appendToList(list, data):
    if(not data == None):
        list.append(data)
        
def BeverGetSKUNr(url:str):
    return url.split("-")[-1].split(".")[0]


#=====Main methods========

def BeverGetReviewsFromURL(url:str):
   skuNr = BeverGetSKUNr(url)
   request = requests.get("https://widgets.reevoo.com/api/product_reviews?per_page=10&trkref=BEV&sku="+skuNr+"&locale=nl-NL&display_mode=embedded&page=1")
   if(request.ok):
    data = json.loads(request.content)

    rating = []
    goodPoints = []
    badpoints = []
    
    nrOfPages = int(data["body"]["pagination"]["total_pages"])
    print(nrOfPages)
    for i in range(nrOfPages):
        data = BeverGetReviewFromSKU(skuNr, i+1)
        if not data == None : #and not data in storageList
            rating.extend(data.get("score"))
            goodPoints.extend(data.get("goodpoints"))
            badpoints.extend(data.get("badpoints"))
        
    storageList.append(dict(sku = skuNr, score = rating, goodpoints = goodPoints,badpoints = badpoints))
        
    


def BeverGetReviewFromSKU(skuNr, pagenr:int):
    request = requests.get("https://widgets.reevoo.com/api/product_reviews?per_page=10&trkref=BEV&sku="+skuNr+"&locale=nl-NL&display_mode=embedded&page="+str(pagenr))
    data = json.loads(request.content)
    data = data["body"]["reviews"]
    
    scores = []
    goodpoints = []
    badpoints = []
    
    for entry in data:
        try:
            scores.append(entry["overall_score"])
            goodpoints.append(entry["text"]["good_points"].replace("\n"," "))
            badpoints.append(entry["text"]["bad_points"].replace("\n"," "))
        except:
            None
            
    if len(goodpoints) > 0 and len(badpoints) > 0:
        return dict(sku = skuNr, score = scores, goodpoints = goodpoints,badpoints = badpoints)
    return None

def BeverGetReviewFromSKU_AsLines(skuNr, pagenr:int):
    request = requests.get("https://widgets.reevoo.com/api/product_reviews?per_page=10&trkref=BEV&sku="+skuNr+"&locale=nl-NL&display_mode=embedded&page="+str(pagenr))
    data = json.loads(request.content)
    data = data["body"]["reviews"]
    
    scores = []
    goodPoints = []
    badPoints = []
    for entry in data:
        
        try:
            scores.append(entry["overall_score"])
            goodPoints.append(entry["text"]["good_points"].replace("\n"," "))
            badPoints.append(entry["text"]["bad_points"].replace("\n"," "))

        except Exception as e:
            #print(e)
            continue
        
    review = dict(sku = skuNr, score = scores, goodpoints = goodPoints,badpoints = badPoints)
    return review

# def BeverGetProductImageFrom(skuNr):
#     request = requests.get("https://widgets.reevoo.com/api/product_reviews?per_page=3&trkref=BEV&sku="+skuNr+"&locale=nl-NL&display_mode=embedded&page=1")
#     data = json.loads(request.content)
#     data = data["body"]["reviews"]
      
   
# BeverGetReviewsFromURL("https://www.bever.nl/p/lowa-renegade-gtx-mid-HABFA62001.html?colour=4169")
# BeverAPIWriteDataAsLinesToCSVFile()
# BeverAPIWriteDataToJsonFile()
# BeverAPIWriteReviewsLooseLiness()
