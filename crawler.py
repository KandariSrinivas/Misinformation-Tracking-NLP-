import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pyautogui
import validators
import time
import json

cwd = os.getcwd()
executable_path = cwd + "\chromedriver"
os.environ["webdriver.chrome.driver"] = executable_path

chrome_options = Options()
chrome_options.add_extension(cwd + '\extension_1_9_0_0.crx')
TOTAL_COUNT = 0

def getLinks(key):
    global TOTAL_COUNT
    TOTAL_COUNT +=1
    print(TOTAL_COUNT, "TOTAL HITS")
    if(validators.url(key) and TOTAL_COUNT < 50):
        Failed = True
        count =0
        while(Failed and count < 5):
            count +=1
            try:
                driver = webdriver.Chrome(executable_path=executable_path, options = chrome_options)
                driver.get(key)
                extn1 = pyautogui.locateOnScreen(cwd + "\\violet_icon.png")
                pyautogui.click(x=extn1[0],y=extn1[1],clicks=1,interval=0.0,button="left")

                # WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[@id='dom-distiller-result-iframe']")))
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,"//iframe[@id='dom-distiller-result-iframe']")))

                ele = driver.find_element_by_css_selector("#dom-distiller-result-iframe")
                driver.switch_to.frame(ele)
                Failed = False
                
                childs = {}
                elems = driver.find_elements_by_xpath("//a[@href]")
                for elem in elems:
                    childs[elem.get_attribute("href")] = {}
                driver.quit()
                return childs
            except:
                print("Failed")
                driver.quit()
                pass
    
    return {}

def traverse(hashmap, key, depth):
    global TOTAL_COUNT
    print("DEPTH: ", depth, TOTAL_COUNT)
    if(TOTAL_COUNT < 50):
        hashmap[key] = getLinks(key)
        if(depth < 3): 
            for k in hashmap[key]:
                traverse(hashmap[key], k, depth+1)
        

pages = []
with open('links.txt', 'r') as f:
  pages = f.read().split('\n')

data = {}
for page in pages[2:4]:
    traverse(data, page, 0)



with open('data.json', 'w') as fp:
    json.dump(data, fp)

"""
recursive function (hashmap, key):
    get links for key
        hashmap[key] = links
        if(depth < 10):
            for k in hashmap[key]:
                function(hashmap[key], k, depth)
    

    

"""
