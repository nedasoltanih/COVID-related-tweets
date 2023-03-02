"""
 This code gathers tweets about COVID19 from specific usernames from twitter 
"""

import pytz
import twitter
import datetime
import pandas as pd

utc = pytz.UTC

# Twitter API information - THESE ARE CONFIDENTIAL INFORMATION, THEREFORE DELETED -
CONSUMER_KEY = ''
CONSUMER_SECRET = ''
OAUTH_TOKEN = ''
OAUTH_TOKEN_SECRET = ''


def is_about_corona(text):
    """Determine if the tweet is about corona

    Args:
        text (string): tweet text

    Returns:
        Boolean: True if the tweet text is about corona, False if not
    """    
    keywords = ['کرونا', 'واکسن', 'واکسیناسیون', 'پاندمی', 'کووید', 'کوید', 'همه گیری', 'همه‌گیری', 
                'corona', 'vaccine', 'vaccination', 'pandemi', 'covid']
    for k in keywords:
        if k in text.lower():
            return True
    else:
        return False
    


# Create a Twitter OAuth object
auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET)

# Initialize the API
twitter_api = twitter.Twitter(auth=auth)

# List of the users whose tweets are needed
user_names = ['WHO', 'UN', 'NIH']

for query in user_names:
    count = 3000

    search_results = twitter_api.search.tweets(q=query, count=count)
    statuses = search_results['statuses']

    tweets = pd.DataFrame(columns=['tweet_id', 'user', 'text', 'time', 'in_reply_to'])

    for i in range(0, len(statuses)):
        if is_about_corona(statuses[i]["text"]):
            if statuses[i].created_at.replace(tzinfo=utc) >= utc.localize(datetime.datetime(2021, 9, 1)) \
                or statuses[i].created_at.replace(tzinfo=utc) < utc.localize(datetime.datetime(2021, 6, 1)):
                tweets.loc[len(tweets)] = [statuses[i]['id_str'], statuses[i]["user"]["screen_name"], statuses[i]["text"], statuses[i]["created_at"], statuses[i]['in_reply_to_status_id_str']]

    # Write tweets of the user in file
    tweets.to_csv(query + "_tweets.csv", index=False)