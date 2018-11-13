import time
import re
from selenium import webdriver
url = "https://www.instagram.com/p/BqCo_tvFWl1/"
driver = webdriver.Chrome('chromedriver.exe')
driver.get(url)
# remove login to insta banner
time.sleep(1)
if driver.find_element_by_xpath('//*[@id="react-root"]/section/nav/div[2]/div/div/div[3]/div/div/section/div/button'):
   driver.find_element_by_xpath('//*[@id="react-root"]/section/nav/div[2]/div/div/div[3]/div/div/section/div/button' ).click()

# # load all comments
# hasLoadMore = True
# while hasLoadMore:
#     time.sleep(1)
#     try:
#         if driver.find_element_by_css_selector('#react-root > section > main > div > div > article > div.eo2As > div.KlCQn.EtaWk > ul > li.lnrre > button'):
#             driver.find_element_by_css_selector('#react-root > section > main > div > div > article > div.eo2As > div.KlCQn.EtaWk > ul > li.lnrre > button').click()
#     except:
#         hasLoadMore = False

users_list = []
users = driver.find_elements_by_class_name('_6lAjh')
for user in users:
    users_list.append(user.text)

i = 0
texts_list = []
texts = driver.find_elements_by_class_name('C4VMK')

for txt in texts:
    texts_list.append(txt.text.split(users_list[i])[1].replace("\r"," ").replace("\n"," ")) 
    i += 1
    comments_count = len(users_list)
    
for i in range(1, comments_count):
    user = users_list[i]
    text = texts_list[i]
    print("User ",user)
    print("Text ",text)
    idxs = [m.start() for m in re.finditer('@', text)]
    for idx in idxs:
        handle = text[idx:].split(" ")[0]
        print(handle)