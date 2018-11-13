import csv
import json
import re
import time
import sys
from bs4 import BeautifulSoup
from datetime import datetime
from flask import Flask, render_template, flash, request, send_file
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from tkinter import *
from tkinter import messagebox
from urllib.request import urlopen


def is_legit(handle, followers_threshold, following_threshold, posts_threshold):
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

        if int(followers) >= followers_threshold and int(following) >= following_threshold and int(posts) >= posts_threshold:
            return True
        else: return False
    except:
        return False

def find_winner(url, tagged_threshold, followers_threshold, following_threshold, posts_threshold):
    print("url = ", url, file=sys.stdout)
    print("tagged_threshold = ", tagged_threshold, file=sys.stdout)
    print("followers_threshold = ", followers_threshold, file=sys.stdout)
    print("following_threshold = ", following_threshold, file=sys.stdout)
    print("posts_threshold = ", posts_threshold, file=sys.stdout)

    # fetch comments
    print("\n Fetching comments . . . \n")
    options = Options()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--disable-gpu')
    options.add_argument('--headless')
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
    
    print("Checking comments . . .")
    results = [["user", "text", "tagged_count", "valid_tags", "valid_post"]]
    comments_count = len(users_list)
    for i in range(1, comments_count):
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
                if is_legit(handle, followers_threshold, following_threshold, posts_threshold):
                    valid_tags += 1
            if valid_tags >= tagged_threshold:
                valid_post = True

        result = [user, text, tagged_count, valid_tags, valid_post]
        results.append(result)

        # to create multiple rows for each tag for randomizer
        result_plus = [user, None, None, None, None]
        if valid_tags != 0:
            for j in range(0, valid_tags-1):
                results.append(result_plus)
        
        print(i, "/", comments_count-1, "comments checked")

    with open("results.csv", "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(results)

    
###############################################   CLI Entry   #####################################################
def cli_run():
    window = Tk() 
    window.title("Scrape Insta")
    info = Label(window, anchor=W, text="URL is the link to your post\nTagged is the min number of tagged friends required\nFollowers, Following, Posts threshold are the min numbers required for a user to be valid\nThis may take awhile\n")
    info.grid(column=0, row=0)

    url_lbl = Label(window, text="URL")
    url_lbl.grid(column=0, row=1)
    url = Entry(window,width=10)
    url.grid(column=1, row=1)

    tagged_threshold_lbl = Label(window, text="Tagged Threshold")
    tagged_threshold_lbl.grid(column=0, row=2)
    tagged_threshold = Entry(window,width=10)
    tagged_threshold.grid(column=1, row=2)

    followers_threshold_lbl = Label(window, text="Followers Threshold")
    followers_threshold_lbl.grid(column=0, row=3)
    followers_threshold = Entry(window,width=10)
    followers_threshold.grid(column=1, row=3)

    following_threshold_lbl = Label(window, text="Following Threshold")
    following_threshold_lbl.grid(column=0, row=4)
    following_threshold = Entry(window,width=10)
    following_threshold.grid(column=1, row=4)

    posts_threshold_lbl = Label(window, text="Posts Threshold")
    posts_threshold_lbl.grid(column=0, row=5)
    posts_threshold = Entry(window,width=10)
    posts_threshold.grid(column=1, row=5)

    def run():
        global this_url, this_tagged_threshold, this_followers_threshold, this_following_threshold, this_posts_threshold
        this_url = str(url.get())
        this_tagged_threshold = int(tagged_threshold.get())
        this_followers_threshold = int(followers_threshold.get())
        this_following_threshold = int(following_threshold.get())
        this_posts_threshold = int(posts_threshold.get())
        window.destroy()
        
        # main function
        find_winner(this_url,this_tagged_threshold,this_followers_threshold,this_following_threshold,this_posts_threshold)

        new_window = Tk()
        lbl = Label(new_window, text="Complete \n \n Find results.csv in same folder as app.exe")
        lbl.grid(column=0, row=0)
        def close():
            new_window.destroy()
        new_btn = Button(new_window, text="Ok", command=close)
        new_btn.grid(column=0, row=1)

    btn = Button(window, text="Run", command=run)
    btn.grid(column=3, row=6)
    window.mainloop()
    
cli_run()
