import sys
import os
import getopt
import csv
import configparser
import requests
import dateutil.parser
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time 

#read config
def read_config():
    config = configparser.ConfigParser()
    config.read('./config.ini')

    return {'api_key': config['twitter']['api_key'], 'api_key_secret': config['twitter']['api_key_secret'], 'bearer_token': config['twitter']['bearer_token'], 'access_token': config['twitter']['access_token'], 'access_token_secret': config['twitter']['access_token_secret']}

def parse():
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv, 'q:f:d:l:')
        if len(opts) != 4:
            return [None, None, None, None]
    except getopt.GetoptError:
        print('usage: api.py -q <\'query\'> -f <filename> -d <YYYY-MM-DDT:hh:mm:ss.000Z>')
        return [None, None, None, None]

    for opt, arg in opts:
        if opt in ['-f']:
            filename = arg
        if opt in ['-q']:
            query = arg
        if opt in ['-d']:
            date = arg
        if opt in ['-l']:
            max_tweets = int(arg)
    return [query, filename, date, max_tweets]

def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers

def create_url(keyword, start_date = None, end_date = None, max_results = 10, search_url = "https://api.twitter.com/2/tweets/search/recent"):
    
    #change params based on the endpoint you are using
    query_params = {'query': keyword,
                    'start_time': start_date,
                    'end_time': end_date,
                    'max_results': max_results,
                    'expansions': 'author_id,in_reply_to_user_id',
                    'tweet.fields': 'id,author_id,in_reply_to_user_id,conversation_id,created_at,public_metrics,referenced_tweets',
                    'next_token': {}}

    return (search_url, query_params)

def timeNext(timestr):
    print(dateutil.parser.parse(timestr))
    print(time.strptime(timestr, '%Y-%m-%dT%H:%M:%S.%fZ'))
    t = str(dateutil.parser.parse(timestr)+relativedelta(seconds=1))
    

def connect_to_endpoint(url, headers, params, total, timestamp, next_token = None):
    params['next_token'] = next_token   #params object received from create_url function
    response = requests.request("GET", url, headers = headers, params = params)
    if response.status_code != 200:
        print("Endpoint Response Code: " + str(response.status_code) + "\ngot: " + str(total) + " tweets\n" + "last timestamp: " + timestamp)
        raise Exception(response.status_code, response.text)
    return response.json()

def append_to_csv(json_response, fileName):
    
    #A counter variable
    counter = 0

    #Open OR create the target CSV file
    csvFile = open(fileName, 'a', newline='', encoding='utf-8')
    csvWriter = csv.writer(csvFile)
    
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
        # 4. replied user ID
        if('in_reply_to_user_id' in tweet):
            in_reply_to_user_id = str(tweet['in_reply_to_user_id'])
        else:
            in_reply_to_user_id = ""
        # 5. reply type and replied tweet ID
        if('referenced_tweets' in tweet):
            for i in range(0, len(tweet['referenced_tweets'])):
                referenced_tweets_type = tweet['referenced_tweets'][i]['type']
                referenced_tweets_id = str(tweet['referenced_tweets'][i]['id'])
        else:
            referenced_tweets_type = ""
            referenced_tweets_id = ""    
        # 6. Language
        #lang = tweet['lang']

        # 7. Tweet metrics
        #retweet_count = tweet['public_metrics']['retweet_count']
        reply_count = tweet['public_metrics']['reply_count']
        like_count = tweet['public_metrics']['like_count']
        quote_count = tweet['public_metrics']['quote_count']

        # 8. Conversation ID
        conversation_id = tweet['conversation_id']
        
        # Assemble all data in a list
        res = [author_id, created_at, tweet_id, in_reply_to_user_id, like_count, reply_count, quote_count, referenced_tweets_type, referenced_tweets_id, conversation_id]
        
        # Append the result to the CSV file
        csvWriter.writerow(res)
        counter += 1

    # When done, close the CSV file
    csvFile.close()

    # Print the number of tweets for this iteration
    print("# of Tweets added from this response: ", counter)
    return counter 

def takeDate(filename):
    if not os.path.isfile(filename):
        return 0
    df = pd.read_csv(filename, dtype=str)
    if df.size == 0:
        return 0
    timestamp = df.iloc[-1]['created_at']
    return timestamp.split(' ')[0]+"T"+timestamp.split(' ')[1].split('+')[0]+".000Z"

def writeHeader(filename):
    if os.path.isfile(filename):
        return 0
    csvFile = open(filename, "a", newline="", encoding='utf-8')
    header = ['author_id', 'created_at', 'tweet_id', 'in_reply_to_user_id', 'like_count', 'reply_count', 'quote_count', 'referenced_tweets_type', 'referenced_tweets_id', 'conversation_id']
    csvWriter = csv.writer(csvFile)
    csvWriter.writerow(header)
    print('A new file has been created, header wrote')
    csvFile.close()

def main():
    
    query, filename, date, max_tweets = parse()
    if query is None or filename is None: 
        exit("error while passing arguments")
    
    config_dict = read_config()

    writeHeader(filename)
    headers = create_headers(config_dict['bearer_token'])

    total = 0
    counter = 0
    requests = 0

    #if file exists then i need to take the last date there
    app_val = takeDate(filename)
    if app_val:
        date = app_val
    while total < max_tweets:
        url = create_url(query, end_date=date, max_results=100)
        json_response = connect_to_endpoint(url[0], headers, url[1], total, date)
        if('data' in json_response):
            date = json_response['data'][len(json_response['data'])-1]['created_at']
            counter = append_to_csv(json_response, filename)
        else:
            print('no more tweets to be returned')
            break
        total += counter
        requests += 1
        if requests == 430:
            requests = 0
            time.sleep(1000)

if __name__ == "__main__":
    main()
