import csv
import json
import re
import time
from bs4 import BeautifulSoup
from datetime import datetime
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from urllib.request import urlopen


def is_legit(handle, followers_threshold, following_threshold, posts_treshold):
    url = "https://www.instagram.com/"
    try:
        page = urlopen(url+handle).read()
        soup = BeautifulSoup(page, features="html.parser")
        string = soup.find("meta",  property="og:description")['content']

        followers = string.split(" Followers, ")[0].replace(",","").replace("k", "000")
        if "." in followers:
            followers = followers.replace(".","")[:-1]

        following = string.split(" Followers, ")[1].split(" Following, ")[0].replace(",","").replace("k", "000")
        if "." in following:
            following = following.replace(".","")[:-1]

        posts = string.split(" Followers, ")[1].split(" Following, ")[1].split(" Posts")[0].replace(",","").replace("k", "000")
        if "." in posts:
            posts = posts.replace(".","")[:-1]

        if int(followers) >= followers_threshold and int(following) >= following_threshold and int(posts) >= posts_treshold:
            return True
        else: return False
    except:
        return False

def find_winner(url, tagged_threshold, followers_threshold, following_threshold, posts_treshold):
    # fetch comments
    options = Options()
    options.add_argument("headless")
    driver = webdriver.Chrome('chromedriver.exe', options=options)
    driver.get(url)

    # remove login to insta banner
    time.sleep(1)
    if driver.find_element_by_xpath('//*[@id="react-root"]/section/nav/div[2]/div/div/div[3]/div/div/section/div/button'):
        driver.find_element_by_xpath('//*[@id="react-root"]/section/nav/div[2]/div/div/div[3]/div/div/section/div/button').click()

    # load all comments 
    hasLoadMore = True
    while hasLoadMore:
        time.sleep(1)
        try:
            if driver.find_element_by_css_selector('#react-root > section > main > div > div > article > div.eo2As > div.KlCQn.EtaWk > ul > li.lnrre > button'):
                driver.find_element_by_css_selector('#react-root > section > main > div > div > article > div.eo2As > div.KlCQn.EtaWk > ul > li.lnrre > button').click()
        except:
            hasLoadMore = False

    time.sleep(1)

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
    
    results = [["user", "text", "tagged_count", "valid_tags", "valid_post"]]
    for i in range(1,len(users_list)):
        user = users_list[i]
        text = texts_list[i]
        valid_post = False
        tagged_count = text.count('@')
        # exceed tagged counts
        if tagged_count >= tagged_threshold:
            idxs = [m.start() for m in re.finditer('@', text)]
            valid_tags = 0
            # check indiv account
            for idx in idxs:
                handle = text[idx:].split(" ")[0].replace("@","")
                if is_legit(handle, followers_threshold, following_threshold, posts_treshold):
                    valid_tags += 1
            if valid_tags >= tagged_threshold:
                valid_post = True

        result = [user, text, tagged_count, valid_tags, valid_post]
        results.append(result)

        # to create multiple rows for each tag for randomizer
        result_plus = [user, None, None, None, None]
        if valid_tags != 0:
            for i in range(0, valid_tags-1):
                results.append(result_plus)

    with open("results.csv", "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(results)
    

find_winner(url="https://www.instagram.com/p/BqCo_tvFWl1/",
            tagged_threshold=1,
            followers_threshold=100,
            following_threshold=50,
            posts_treshold=10)
    
