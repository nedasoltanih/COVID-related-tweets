"""
 This code reads tweets from a csv file then gathers likes of comments of that tweet based on tweet id.
 Comments include text, date and the username of the person who commented.
 Likes include the username of the person who commented. 
"""

import csv
import pytz
import time
import pickle
import datetime
import pandas as pd
from os import listdir
from os.path import exists
from bs4 import BeautifulSoup
from selenium import webdriver

utc = pytz.UTC

chrome_path = 'chromedriver'
driver = webdriver.Chrome(executable_path=chrome_path)

def write_to_csv(folder, name, data):
    """Write information to CSV file

    Args:
        folder (str): path to output file
        name (str): name of the user
        data (iterable): data to write inside file
    """    
    output = folder + '/' + name + '.csv'
    with open(output, 'a', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(data)

def is_about_corona(text):
    """check if the tweet is about COVID19

    Args:
        text (str): text of the tweet

    Returns:
        boolean: True if the tweet is about COVID19, False if not
    """    
    keywords = ['کرونا', 'واکسن', 'واکسیناسیون', 'پاندمی', 'کووید', 'کوید', 'همه گیری', 'همه‌گیری', 
                'corona', 'vaccine', 'vaccination', 'pandemi', 'covid']
    for k in keywords:
        if k in text.lower():
            return True
    else:
        return False

# List of the twitter usernames to check the tweets
usernames = ['WHO', 'UN', 'NIH']


# open twitter on chrome
driver.get("https://mobile.twitter.com/")

# use the cookies to login
if exists("cookies_vs.pkl"):
    cookies = pickle.load(open("cookies_vs.pkl", "rb"))
    for cookie in cookies:
        driver.add_cookie(cookie)
else:
    pickle.dump(driver.get_cookies(), open("cookies_vs.pkl", "wb"))

# Start crawling each user's timeline
for username in usernames:
    all_tweets = pd.read_csv(f'tweets/{username}.csv', header=0, index_col=False)

    for idx, tweet in all_tweets.iterrows():
        tweet_date = datetime.datetime.strptime(tweet['date'], '%Y-%m-%d').replace(tzinfo=utc)

        if not is_about_corona(tweet['text']):
            continue

        # Gather tweets between specific dates
        if tweet_date >= utc.localize(datetime.datetime(2023, 1, 1)) \
            or tweet_date < utc.localize(datetime.datetime(2021, 1, 1)):
            continue

        # sleep for two seconds because twitter may recognize you as a bot :)
        if idx % 100 == 0:
            time.sleep(2)
        try:
            num_likes = 0
            num_comments = 0

            orig_tweet = tweet['tweet_id']

            # Write original tweets inside csv file
            write_to_csv('comments', f'{username}_{orig_tweet}_comments', [
                            'user', 'text', 'comment_date', 'original_tweet'])

            url = "https://mobile.twitter.com/{}/status/{}".format(
                username, tweet['tweet_id'])
            driver.get(url)
            time.sleep(2)

            # Get the comments
            for i in range(1, 11):

                # If there are more comments, click on Show More link and sleep 2 seconds so all the comments are loaded
                show_more = driver.find_elements_by_xpath(
                    "//*[@class='css-18t94o4']")    # TODO: Find the proper element in page and replace it here
                
                if show_more:
                    show_more[0].click()
                    time.sleep(2)
                scroll = i * 2000

                soup = BeautifulSoup(driver.page_source, 'html.parser')
                comments = soup.find_all(
                    'div', {'class': "css-1dbjc4n"})

                for comment in comments:
                    if len(comment.contents) > 1:
                        # Extract text, user and date from comment
                        text = comment.contents[1].text
                        if len(comment.findChildren('a')):
                            if '@' in comment.findChildren('a')[0].text:
                                user = comment.findChildren(
                                    'a')[0].text.split('@')[1]
                                comment_date = comment.find_all(
                                    'time')[0].attrs['datetime']

                                info = [user, text, comment_date, orig_tweet]
                                write_to_csv(
                                    './comments', f'{username}_{orig_tweet}_comments', info)
                                num_comments += 1
                        else:
                            continue

                # If reached the bottom, break
                if not comments or num_comments == 0:
                    break
                if i > 1:
                    if prev_comments == comments:
                        break
                prev_comments = comments

                # scroll down
                driver.execute_script(f"window.scrollTo(0,{scroll})")
                time.sleep(2)

            # Get the likes
            driver.get(
                f"https://mobile.twitter.com/{username}/status/{orig_tweet}/likes")
            time.sleep(4)

            for i in range(1, 301):
                scroll = i * 1000

                soup = BeautifulSoup(driver.page_source, 'html.parser')
                likers = soup.find_all('div', {'id': "react-root"})[0]
                lst = likers.find_all('span')

                for l in lst:
                    if l.text.find('@') == 0:
                        write_to_csv(
                            '.likes', f'{username}_{orig_tweet}_likes', [l.text])
                        num_likes += 1

                if num_likes == 0:
                    break
                if i > 1:
                    if prev_likes == lst:
                        break

                num_likes = 0
                prev_likes = lst

                driver.execute_script(f"window.scrollTo(0,{scroll})")
                time.sleep(1)

        except Exception as ex:
            write_to_csv('./', 'exception', [ex, orig_tweet, username])
            continue

driver.quit()
