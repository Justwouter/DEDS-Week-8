import csv
from threading import Thread, Lock
import time
from csv import writer
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options 
from selenium.webdriver.common.by import By

url = "https://www.bol.com/nl/nl/l/rugzakken/20701/"
outputfile = 'bol.csv'
links = []

def writeToOutput(item):
    with open(outputfile, 'a', encoding="utf8", newline="") as out:
        write = writer(out)
        write.writerow(item)
        
def getBrowser():
    ffoptions = Options()
    #ffoptions.add_argument("--headless")
    return webdriver.Firefox(options=ffoptions)    

def BolGetProductsByURL(browser: webdriver.Firefox, url):
    browser.get(url)
    BolRefuseCookies(browser)
    products = browser.find_elements(By.XPATH, "//a[@class = 'product-title product-title--placeholder px_list_page_product_click list_page_product_tracking_target']")
    print(len(products))
    for element in products:
        print(element.get_attribute("title"))
        writeToOutput(element.get_attribute("title"))


def BolRefuseCookies(browser: webdriver.Firefox):
    browser.get(url)
    try:
        browser.find_element(By.ID, "js-reject-all-button").click()
    except:
        None


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
            BolGetProductsByURL(browser, link)
        browser.close()

        

def create_threads():
    start_time = time.time()
    for i in range(int(len(links)/5)): #Spawns a thread for each entry in a list threads (len(urls))
        name = "Thread #%s" % (i)
        my_thread = MyThread(name)
        my_thread.start()
    my_thread.join() 
    end_time = time.time()
    execution_time = end_time - start_time
    print("Execution time:", execution_time, "seconds")
    time.sleep(5)
    
if __name__ == "__main__":
    for i in range(1,50):
        links.append(i)
    create_threads()
    