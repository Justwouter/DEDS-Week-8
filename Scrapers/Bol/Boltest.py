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


url = "https://www.bol.com/nl/nl/p/superdry-classic-fuji-puffer-heren-jas-maat-m/9300000044880252/?bltgh=viqj7Z7WL-Lz0MSEhA9L2Q.3_22.25.ProductImage"


def getBrowser():
    ffoptions = Options()
    #ffoptions.add_argument("--headless")
    return webdriver.Firefox(options=ffoptions)    


browser = getBrowser()
browser.get(url)
ean = browser.find_elements(By.XPATH, "//dd[@class = 'specs__value']")
for element in ean:
    text = element.get_attribute("textContent").replace(" ", "").replace("\n", "")
    if len(text) == 13 and text.isdigit():
        print(text)
