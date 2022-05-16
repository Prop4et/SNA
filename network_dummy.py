import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import copy

def showGraph(g):
    pos = nx.layout.spectral_layout(g)
    pos = nx.spring_layout(g, pos=pos, iterations=50)

    # Create position copies for shadows, and shift shadows
    pos_shadow = copy.deepcopy(pos)
    shift_amount = 0.006
    for idx in pos_shadow:
        pos_shadow[idx][0] += shift_amount
        pos_shadow[idx][1] -= shift_amount

    #~~~~~~~~~~~~
    # Draw graph
    #~~~~~~~~~~~~
    fig = plt.figure(frameon=False)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')

    nx.draw_networkx_nodes(g, pos_shadow, node_color='k', alpha=0.5)
    nx.draw_networkx_nodes(g, pos, node_color="#3182bd", linewidths=1)
    nx.draw_networkx_edges(g, pos, width=1)
    plt.show()

def main():
    #read post df
    df= pd.read_csv('data3.csv', dtype=str)
    #df = pd.concat([df_post, df_comments])
    df.drop(columns=['created_at', 'lang', 'like_count','quote_count','reply_count','retweet_count','referenced_tweets_type','conversation_id'], inplace=True)
    print(df)
    tg: nx.MultiDiGraph = nx.from_pandas_edgelist(
        df, source='tweet_id', target='referenced_tweets_id', edge_attr=True, create_using=nx.MultiDiGraph)
    
    ug: nx.MultiDiGraph = nx.from_pandas_edgelist(df, source='author_id', target='in_reply_to_user_id', edge_attr=None, create_using=nx.MultiDiGraph)
    showGraph(ug)
    
    return 0

if __name__ == '__main__':
    main()