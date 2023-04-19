from csv import writer
import os
import requests
import json

outfile = os.path.dirname(__file__)+"/output/data"
storageList = []

#======File managment=======

def BeverAPIWriteDataToJsonFile():
    with open(outfile+".json", 'w', encoding="utf8", newline="") as out:
        json.dump(storageList, out) 
        
def BeverAPIWriteDataToCSVFile():
    with open(outfile+".csv", 'w', encoding="utf8", newline="") as out:
        write = writer(out)
        write.writerow(["sku","rating","good points","bad points"])
    with open(outfile+".csv", 'a', encoding="utf8", newline="") as out:
        write = writer(out)
        for entry in storageList:
            write.writerow(entry)
            
def BeverAPIWriteDataAsLinesToCSVFile():
    with open(outfile+".csv", 'w', encoding="utf8", newline="") as out:
        write = writer(out)
        write.writerow(["sku","rating","good points","bad points"])
    with open(outfile+".csv", 'a', encoding="utf8", newline="") as out:
        write = writer(out)
        for entry in storageList:
            for review in entry:
                write.writerow(review)
                
def BeverAPIWriteReviewsLooseLiness():
    with open(outfile+".txt", 'w', encoding="utf8", newline="") as out:
        write = writer(out, delimiter=".")
        for entry in storageList:
            for review in entry:
                write.writerow(review[2:] for i in review[2:])
                
                
                
                

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

    nrOfPages = int(data["body"]["pagination"]["total_pages"])
    print(nrOfPages)
    for i in range(nrOfPages):
        data = BeverGetReviewFromSKU_AsLines(skuNr, i+1)
        if not data == None : #and not data in storageList
            storageList.append(data)
        # print(str(data) + " " + str(i))
        # print(len(storageList))
        
    


def BeverGetReviewFromSKU(skuNr, pagenr:int):
    request = requests.get("https://widgets.reevoo.com/api/product_reviews?per_page=10&trkref=BEV&sku="+skuNr+"&locale=nl-NL&display_mode=embedded&page="+str(pagenr))
    data = json.loads(request.content)
    data = data["body"]["reviews"]
    
    rating = []
    goodPoints = []
    badpoints = []
    
    for thingy in data:
        try:
            appendToList(rating, thingy["overall_score"])
        except:
            None
        try:
            appendToList(goodPoints, thingy["text"]["good_points"])
        except:
            None
        try:
            appendToList(badpoints, thingy["text"]["bad_points"])
        except:
            None
            
    if len(goodPoints) > 0 or len(badpoints) > 0:
        return [skuNr,rating,goodPoints,badpoints]
    return None

def BeverGetReviewFromSKU_AsLines(skuNr, pagenr:int):
    request = requests.get("https://widgets.reevoo.com/api/product_reviews?per_page=10&trkref=BEV&sku="+skuNr+"&locale=nl-NL&display_mode=embedded&page="+str(pagenr))
    data = json.loads(request.content)
    data = data["body"]["reviews"]
    reviews = []

    for entry in data:
        review = [skuNr]
        try:
            score = entry["overall_score"]
            goodPoints = entry["text"]["good_points"].replace("\n"," ")
            badPoints = entry["text"]["bad_points"].replace("\n"," ")

            review.append(score)
            review.append(goodPoints)
            review.append(badPoints)
        except Exception as e:
            #print(e)
            continue
        reviews.append(review)
        
    return reviews

# def BeverGetProductImageFrom(skuNr):
#     request = requests.get("https://widgets.reevoo.com/api/product_reviews?per_page=3&trkref=BEV&sku="+skuNr+"&locale=nl-NL&display_mode=embedded&page=1")
#     data = json.loads(request.content)
#     data = data["body"]["reviews"]
      
   
BeverGetReviewsFromURL("https://www.bever.nl/p/lowa-renegade-gtx-mid-HABFA62001.html?colour=4169")
BeverAPIWriteDataAsLinesToCSVFile()
BeverAPIWriteReviewsLooseLiness()
