import csv,time
import os
from threading import Thread, Lock 
from csv import writer
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options 
from selenium.webdriver.common.by import By
import selenium.webdriver.support.ui as ui
import BeverAPI


url = "https://www.bever.nl/c/heren/schoenen.html"
outputpath = os.path.dirname(__file__)+'/output/'
outputfile = os.path.dirname(__file__)+'/output/Beverbot.csv'
imageoutputpath = outputpath+"Images/"
products = []
productNrs = []
wait = None
lock = Lock()


def getBrowser():
    ffoptions = Options()
    ffoptions.add_argument("--headless")
    return webdriver.Firefox(options=ffoptions)    

def BeverInitialSetup(browser:webdriver.Firefox):
    browser.get(url)
    browser.find_element(By.ID, 'accept-all-cookies').click()
        
    #Find the pagination and take the last element after the "->" which displays the total amount of pages. Can't get the number directly so get the link and add one because page=0 doesn't exist in the selector
    #Bit janky but it works on every page without an explicit Xpath
    pageAmount = int(browser.find_elements(By.XPATH, "//a[@class = 'as-a-btn as-a-btn--pagination as-m-pagination__item']")[-2].get_attribute("href").split("=")[-1])+1
    
    print(pageAmount)
    return int(pageAmount)

def BeverLoadFindAllURLs(browser:webdriver.Firefox, baseurl):
    pageAmount = BeverInitialSetup(browser)
    url = baseurl
    links = []
    for i in range(pageAmount):
        url = baseurl+"?page="+str(i)
        links.extend(BeverGetURLFromPage(browser, url))
        print("Found " + url)
    return links
        
def BeverGetURLFromPage(browser:webdriver.Firefox, page):
    browser.get(page)
    URLS = []
    Products = browser.find_elements(By.XPATH, "//a[@class = 'as-a-link as-a-link--container as-m-product-tile__link']")
    
    for thing in Products:
        print(thing.get_attribute("href"))

    for element in Products:
        link = element.get_attribute("href")
        if(not "https://www.bever.nl" in link):
            URLS.append('https://www.bever.nl' + link)
        else:
            URLS.append(link)
    return URLS

def BeverGetProductData(browser:webdriver.Firefox, url):
    SkuNr = BeverAPI.BeverGetSKUNr(url)
    if(not SkuNr in productNrs):
        productNrs.append(SkuNr)
        try:
            browser.get(url)
            try:
                browser.find_element(By.ID, 'accept-all-cookies').click()
            except:
                None
                
            #Get info
            brand = browser.find_element(By.XPATH, "//a[@class = 'as-a-link as-a-link--base']").text
            product = browser.find_element(By.XPATH, "//span[@class = 'as-a-text as-a-text--title']").text
            price = browser.find_element(By.XPATH, "//span[@data-qa = 'sell_price']").text.replace('€', '').replace(",",".")
            wait.until(lambda WaitForImagesToLoad: browser.find_element(By.XPATH, "//img[@class = 'as-a-image as-m-slide__thumb-img lazyautosizes ls-is-cached lazyloaded']"))
            image =  browser.find_element(By.XPATH, "//img[contains(@class, 'as-a-image as-m-slide__thumb-img lazyautosizes ls-is-cached lazyloaded')]").get_property("src").replace("65x98","550x825")
            
            info = [SkuNr,brand, product, price, image]
            products.append(info)
            BeverDownloadImage(image,SkuNr)
            BeverAPI.BeverGetReviewsFromURL(url)
            return True
        except:
            None
    else:
        return False

def BeverDownloadImage(url, sku):
    response = requests.get(url)
    if response.status_code == 200:
        with open(outputpath+"Images/"+sku+".jpg", 'wb') as f:
            f.write(response.content)
    
    



#=====================File Management==================================================
def writeToOutput(item):
    with open(outputfile, 'a', encoding="utf8", newline="") as out:
        write = writer(out)
        write.writerow(item)

def stringInOutput(item):
    with open(outputfile, 'r', encoding="utf8", newline="") as out:
        items = csv.reader(out, delimiter=",")
        for line in items:
            if item[1] in line[1] and item[2] == line[2]:
                return True
    return False

def setupOutputFile():
    EnsureFileExists(imageoutputpath)
    with open(outputfile, 'w', encoding="utf8", newline="") as out:
        out.write("")
        
        
def EnsureFileExists(outfile):
    directory = os.path.dirname(outfile)
    if not os.path.exists(directory):
        os.makedirs(directory)
    if not os.path.exists(outfile):
        open(outfile, 'w').close()







#=====================Threading==================================================

class MyThread(Thread):
    links = []
    
    def __init__(self, name):
        Thread.__init__(self)
        self.name = name

    def run(self):
        threadName = self.name
        browser = getBrowser()
        with getBrowser() as browser:
            while len(links) > 0:
                
                lock.acquire()
                link = links.pop()
                lock.release()
                
                if BeverGetProductData(browser, link):
                    print(threadName +" Finished "+ BeverAPI.BeverGetSKUNr(link))
                else:
                    print(threadName +" Skipped "+ BeverAPI.BeverGetSKUNr(link))
        

def create_threads():
    start_time = time.time()
    
    for i in range(int(len(links)/50)):
        name = "Thread #%s" % (i)
        my_thread = MyThread(name)
        my_thread.start()
    my_thread.join() 
    time.sleep(5)
    
    writeToOutput(["sku","brand","product","price","image link"])
    for product in products:
        writeToOutput(product)
        
    BeverAPI.BeverAPIWriteDataAsLinesToCSVFile()
    BeverAPI.BeverAPIWriteDataToJsonFile()
    BeverAPI.BeverAPIWriteReviewsLooseLiness()
    print(len(productNrs))
    
    end_time = time.time()
    time_elapsed = end_time - start_time
    print("Time elapsed:", time_elapsed, "seconds")

if __name__ == "__main__":
    browser = getBrowser()
    wait = ui.WebDriverWait(browser, 5)
    setupOutputFile()
    links = BeverLoadFindAllURLs(browser, url)
    print(len(links))
    browser.close()
    create_threads()
    