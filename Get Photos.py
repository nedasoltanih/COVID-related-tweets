"""
 This code reads likes and comments from csv files then gathers profile picture of each user.
"""

import time
import pickle
import pandas as pd
import urllib.request
from os import listdir
from os.path import exists
from bs4 import BeautifulSoup
from selenium import webdriver


chrome_path = 'chromedriver'
driver = webdriver.Chrome(executable_path=chrome_path)


usernames = []

unames = set()
driver.get("https://mobile.twitter.com/")

if exists("cookies_vs.pkl"):
    cookies = pickle.load(open("cookies_vs.pkl", "rb"))
    for cookie in cookies:
        driver.add_cookie(cookie)
else:
    pickle.dump(driver.get_cookies(), open("cookies_vs.pkl", "wb"))

for u in listdir(f'images/'):
    unames.add(u.replace(".jpg", ""))
    
for username in usernames:
    files = listdir(f'likes/')
    for f in files:
        likers = pd.read_csv(f'likes/' + f)
        for _, like in likers.iterrows():
            uname = like.values[0][1:]
            if uname not in unames:
                driver.get(f"https://twitter.com/{uname}/photo")
                time.sleep(2)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                link = soup.find_all(
                            'img', {'alt': "Image"})[0].attrs["src"]
                urllib.request.urlretrieve(link, f"images/{uname}.jpg")

            unames.add(uname)

    files = listdir(f'comments/')
    for f in files:
        likers = pd.read_csv(f'comments/' + f)
        for _, like in likers.iterrows():
            uname = like.values[0]
            if uname not in unames:
                driver.get(f"https://twitter.com/{uname}/photo")
                time.sleep(2)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                link = soup.find_all(
                            'img', {'alt': "Image"})[0].attrs["src"]
                urllib.request.urlretrieve(link, f"images/{uname}.jpg")

            unames.add(uname)

driver.close()