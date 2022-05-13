import csv
from traitlets import Undefined
import tweepy
import configparser
import requests
import json
import pandas as pd
import dateutil.parser

#read config
config = configparser.ConfigParser()
config.read('./config.ini')

api_key = config['twitter']['api_key']
api_key_secret = config['twitter']['api_key_secret']

bearer_token = config['twitter']['bearer_token']

access_token = config['twitter']['access_token']
access_token_secret = config['twitter']['access_token_secret']

def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers

def create_url(keyword, start_date, end_date, max_results = 10):
    
    search_url = "https://api.twitter.com/2/tweets/search/recent" 
    #change params based on the endpoint you are using
    query_params = {'query': keyword,
                    'start_time': start_date,
                    'end_time': end_date,
                    'max_results': max_results,
                    'expansions': 'author_id,in_reply_to_user_id',
                    'tweet.fields': 'id,text,author_id,in_reply_to_user_id,conversation_id,created_at,lang,public_metrics,referenced_tweets',
                    'next_token': {}}
    return (search_url, query_params)

def connect_to_endpoint(url, headers, params, next_token = None):
    params['next_token'] = next_token   #params object received from create_url function
    response = requests.request("GET", url, headers = headers, params = params)
    print("Endpoint Response Code: " + str(response.status_code))
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

def append_to_csv(json_response, fileName):
    
    #A counter variable
    counter = 0

    #Open OR create the target CSV file
    csvFile = open(fileName, "a", newline="", encoding='utf-8')
    csvWriter = csv.writer(csvFile)
    header = ['author_id', 'created_at', 'tweet_id', 'lang', 'like_count', 'quote_count', 'reply_count', 'retweet_count', 'in_reply_to_user_id', 'referenced_tweets_type', 'referenced_tweets_id']
    csvWriter.writerow(header)
    #Loop through each tweet
    for tweet in json_response['data']:
        
        # We will create a variable for each since some of the keys might not exist for some tweets
        # So we will account for that

        # 1. Author ID
        author_id = tweet['author_id']

        # 2. Time created
        created_at = dateutil.parser.parse(tweet['created_at'])

        # 3. Tweet ID
        tweet_id = tweet['id']

        if('in_reply_to_user_id' in tweet):
            in_reply_to_user_id = str(tweet['in_reply_to_user_id'])
        else:
            in_reply_to_user_id = ""

        if('referenced_tweets' in tweet):
            for i in range(0, len(tweet['referenced_tweets'])):
                referenced_tweets_type = tweet['referenced_tweets'][i]['type']
                referenced_tweets_id = str(tweet['referenced_tweets'][i]['id'])
        else:
            referenced_tweets_type = ""
            referenced_tweets_id = ""    
        # 4. Language
        lang = tweet['lang']

        # 5. Tweet metrics
        retweet_count = tweet['public_metrics']['retweet_count']
        reply_count = tweet['public_metrics']['reply_count']
        like_count = tweet['public_metrics']['like_count']
        quote_count = tweet['public_metrics']['quote_count']

        # 6. Tweet text
        #text = tweet['text']
        
        # Assemble all data in a list
        res = [author_id, created_at, tweet_id, lang, like_count, quote_count, reply_count, retweet_count, in_reply_to_user_id, referenced_tweets_type, referenced_tweets_id]
        
        # Append the result to the CSV file
        csvWriter.writerow(res)
        counter += 1

    # When done, close the CSV file
    csvFile.close()

    # Print the number of tweets for this iteration
    print("# of Tweets added from this response: ", counter) 

headers = create_headers(bearer_token)
keyword = "(#Eurovision2022 OR #ESC2022) -is:retweet"
start_time = "2022-05-10T00:00:00.000Z"
end_time = "2022-05-13T00:00:00.000Z"
url = create_url(keyword, start_time, end_time)
json_response = connect_to_endpoint(url[0], headers, url[1])

append_to_csv(json_response, "data2.csv")
