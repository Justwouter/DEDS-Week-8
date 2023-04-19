import csv
import os
from threading import Thread, Lock
import time
from csv import writer
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options 
from selenium.webdriver.common.by import By
import selenium.webdriver.support.ui as ui


url = "https://www.bol.com/nl/nl/l/jassen/47445/"
outputpath = os.path.dirname(__file__)+'/output/'
outputfile = os.path.dirname(__file__)+'/output/bol.txt'
links = []
codes = []
wait = ""



def writeToOutput(item):
    with open(outputfile, 'a', encoding="utf8", newline="") as out:
        out.write(item+"\n")
        
def getBrowser():
    ffoptions = Options()
    ffoptions.add_argument("--headless")
    return webdriver.Firefox(options=ffoptions)    

def BolRefuseCookies(browser: webdriver.Firefox, link):
    browser.get(link)
    try:
        wait.until(lambda Waitlol: browser.find_element(By.XPATH, "//div[@class = 'modal__window js_modal_window']"))
        browser.find_element(By.ID, "js-reject-all-button").click()
    except:
        None

def BolGetEANCode(browser: webdriver.Firefox):
    specs = browser.find_elements(By.XPATH, "//dd[@class = 'specs__value']")
    for element in specs:
        ean = element.get_attribute("textContent").replace(" ", "").replace("\n", "")
        if len(ean) == 13 and ean.isdigit():
            return ean


def BolGetProductsByURL(browser: webdriver.Firefox, link):
    BolRefuseCookies(browser, link)
    products = browser.find_elements(By.XPATH, "//a[@class = 'product-title product-title--placeholder px_list_page_product_click list_page_product_tracking_target']")
    productLinks = []

    for element in products:
        productlink = element.get_attribute("href")
        productLinks.append(productlink)
        
    for link in productLinks:
        BolGetInfoFromProductPage(browser, link)
        
        
def BolGetInfoFromProductPage(browser: webdriver.Firefox, link):
    BolRefuseCookies(browser, link)
    ean = BolGetEANCode(browser)
    
    if(ean is not None and ean not in codes):
        codes.append(ean)
        name = browser.find_element(By.XPATH, "//span[@data-test = 'title']").text
        image = browser.find_element(By.XPATH, "//img[contains(@class, 'js_selected_image')]").get_attribute("src") 
        print(ean)
        DownloadImage(image, ean)
        writeToOutput([ean, name, image])
        
        reviews = browser.find_elements(By.XPATH, "//span[@class = 'review__body']")

        for item in reviews:
            with open(outputpath+"data.csv", 'a', encoding="utf8", newline="") as out:
                write = writer(out)
                write.writerow(item.text)
                print("Im working")
    else:
        return 0
    

    
def writeToOutput(item):
    with open(outputfile, 'a', encoding="utf8", newline="") as out:
        write = writer(out)
        write.writerow(item)

def setupOutputFile():
    with open(outputfile, 'w', encoding="utf8", newline="") as out:
        out.write("")
        
        
        
def DownloadImage(url, ean):
    response = requests.get(url)
    if response.status_code == 200:
        with open(outputpath+"Images/"+ean+".jpg", 'wb') as f:
            f.write(response.content)



lock = Lock()
class MyThread(Thread):
    
    def __init__(self, name):
        Thread.__init__(self)
        self.name = name

    def run(self):
        threadName = self.name
        browser = getBrowser()

        while len(links) > 0:
            
            lock.acquire()
            pageNr = links.pop()
            lock.release()
            
            
            link = url+"?page="+str(pageNr)
            # try:
            BolGetProductsByURL(browser, link)
            # except:
            #     print("Error in " + threadName)
        browser.close()

        

def create_threads():
    start_time = time.time()
    for i in range(int(len(links)/50)+1): #Spawns a thread for each entry in a list threads (len(urls)) #
        name = "Thread #%s" % (i)
        my_thread = MyThread(name)
        my_thread.start()
    my_thread.join() 
    end_time = time.time()
    execution_time = end_time - start_time
    print("Execution time:", execution_time, "seconds")
    time.sleep(5)
    
if __name__ == "__main__":
    for i in range(1,500):
        links.append(i)
    browser = getBrowser()
    wait = ui.WebDriverWait(browser, 5)
    browser.close()
    create_threads()
    