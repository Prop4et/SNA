import api
import pandas as pd

def main():
    df = pd.read_csv('data2.csv', dtype='str')
    config_dict = api.read_config()
    headers = api.create_headers(config_dict['bearer_token'])
    api.writeHeader("data3.csv")
    start_time = "2022-05-10T00:00:00.000Z"
    for idx, row in df.iterrows():
        #print(row['author_id'], row['conversation_id'])
        if (int(row['reply_count']) or int(row['quote_count'])) > 0:
            url = api.create_url("conversation_id:"+row['conversation_id']+" -is:retweet", start_time)
            json_response = api.connect_to_endpoint(url[0], headers, url[1])
            api.append_to_csv(json_response, "data3.csv")

if __name__ == '__main__':
    main()