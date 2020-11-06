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
from urlparse import urlparse


cwd = os.getcwd()
executable_path = cwd + "\chromedriver"
os.environ["webdriver.chrome.driver"] = executable_path

chrome_options = Options()
chrome_options.add_extension(cwd + '\extension_1_9_0_0.crx')
TOTAL_COUNT = 0
MAX_LINKS = 1500
MAX_DEPTH = 4
counter = {}

def trimURL(link):
  l = urlparse(link)
  if(l.scheme == 'https' or l.scheme == 'http'):
    return l.scheme + '://' + l.netloc + l.path
  return None
def getJavaScriptCode(query):
    if(query== "Verify URL"):
        return "let {protocol , hostname , pathname} = window.location; return protocol + '//' + hostname + pathname;"
    return None
Visited = set([])
Queue = []

def getLinks(key, depth, parent):
    global TOTAL_COUNT
    global counter
    global MAX_DEPTH
    global MAX_LINKS
    TOTAL_COUNT +=1
    print(TOTAL_COUNT, "TOTAL HITS")
    if(validators.url(key)):
        Failed = True
        count =0
        key = trimURL(key)
        if(key and (key not in Visited)): #URL Check 1

            while(Failed and count < 3):
                count +=1
                try:
                    driver = webdriver.Chrome(executable_path=executable_path, options = chrome_options)
                    driver.get(key)
                    # print("Console: ", driver.execute_script(getJavaScriptCode("Verify URL")))
                    browserLink = str(driver.execute_script(getJavaScriptCode("Verify URL")))
                    print("Browser Link", browserLink)
                    if(browserLink in Visited): #URL Check 2
                        driver.quit()
                        return False

                    extn1 = pyautogui.locateOnScreen(cwd + "\\violet_icon.png")
                    pyautogui.click(x=extn1[0],y=extn1[1],clicks=1,interval=0.0,button="left")

                    # WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[@id='dom-distiller-result-iframe']")))
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,"//iframe[@id='dom-distiller-result-iframe']")))

                    ele = driver.find_element_by_css_selector("#dom-distiller-result-iframe")
                    print(ele.tag_name)
                    driver.switch_to.frame(ele)
                    Failed = False
                    Visited.add(browserLink)

                    childs = set([])
                    elems = driver.find_elements_by_xpath("//a[@href]")
                    for elem in elems:
                        # Queue
                        childLink = trimURL(elem.get_attribute("href"))
                        if(childLink and childLink != browserLink):
                            childs.add(childLink) #remove self links
                            counter[parent] +=1
                            if(childLink not in Visited and depth +1 < MAX_DEPTH and counter[parent] < MAX_LINKS):
                                Queue.append((childLink, depth +1, parent))
                        
                    driver.quit()
                    return (browserLink , list(childs))
                except:
                    print("Failed")
                    driver.quit()
                    pass
    
    return False



with open('links.txt', 'r') as f:
  links = f.read().split('\n')
  for link in links[:5]:
      counter[link] = 0
      Queue.append((link, 0, link))



data = {}
while(len(Queue)):
    page, depth, parent = Queue.pop(0)
    if(depth < MAX_DEPTH and counter[parent] < MAX_LINKS):
        childs = getLinks(page, depth, parent)
        if(childs):
            data[childs[0]] = childs[1]
# print("V:", Visited)
    # print("Q:", Queue)



with open('data.json', 'w') as fp:
    json.dump(data, fp)
print("COUNTER: " ,counter)

"""
recursive function (hashmap, key):
    get links for key
        hashmap[key] = links
        if(depth < 10):
            for k in hashmap[key]:
                function(hashmap[key], k, depth)
    
# def traverse(hashmap, key, depth):
#     global TOTAL_COUNT
#     print("DEPTH: ", depth, TOTAL_COUNT)
#     if(TOTAL_COUNT < 50):
#         hashmap[key] = getLinks(key)
#         if(depth < 3): 
#             for k in hashmap[key]:
#                 traverse(hashmap[key], k, depth+1)
        
    

"""
# {'https://www.medicalnewstoday.com/articles/320984#What-are-the-medical-benefits-of-marijuana?': 1588, 
#  'https://onlinelibrary.wiley.com/doi/full/10.1111/add.14031': 0, 
#  'https://www.dw.com/en/the-real-winners-of-the-us-china-trade-dispute/a-55420269': 190, 
#  'https://www.bbc.com/news/business-45899310': 2, 
#  'https://www.nature.com/articles/d41586-020-02965-3': 859}