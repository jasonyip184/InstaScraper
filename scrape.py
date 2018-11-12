import csv
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime
from pprint import pprint
from urllib.request import urlopen

def is_legit(handle, followers_threshold, following_threshold, posts_treshold):
    url = "https://www.instagram.com/"
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

def find_winner(url, tagged_threshold, followers_threshold, following_threshold, posts_treshold, datetime_treshold):
    # fetch comments
    page = urlopen(url).read()
    soup = BeautifulSoup(page, features="html.parser")
    script_tag = soup.find('script', text=re.compile('window\._sharedData'))
    shared_data = script_tag.string.partition('=')[-1].strip(' ;')
    json_data = json.loads(shared_data)
    comments = json_data['entry_data']['PostPage'][0]['graphql']['shortcode_media']['edge_media_to_comment']['edges']
    results = [["timestamp", "user", "text", "tagged_count", "valid_tags", "valid_post"]]
    for comment in comments:
        timestamp = datetime.utcfromtimestamp(comment['node']['created_at']).strftime('%Y-%m-%d %H:%M:%S')
        user = comment['node']['owner']['username']
        text = comment['node']['text']
        valid_post = False
        # does not exceed datetime
        if timestamp.split(" ")[0] <= datetime_treshold:
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
        result = [timestamp, user, text, tagged_count, valid_tags, valid_post]
        results.append(result)
        print(result)

    with open("results.csv", "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(results)
    

find_winner(url="https://www.instagram.com/p/BqCo_tvFWl1/",
            tagged_threshold=1,
            followers_threshold=100,
            following_threshold=50,
            posts_treshold=10,
            datetime_treshold="2018-11-17 23:59:59")
    
