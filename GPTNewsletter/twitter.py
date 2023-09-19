import requests
import json

from config import *
from utils import remove_emoji, remove_punctuation, contains_number


def get_twitter_tickers_and_tweets(log):
    log.info('in get_twitter_tickers_and_tweets')

    url = f'https://api.twitter.com/2/lists/{TWITTER_LIST_ID}/tweets'

    headers = {'Authorization' : f'Bearer {TWITTER_BEARER_TOKEN}'}

    params = {
        'max_results': TWEET_COUNT
    }

    response = requests.get(url, headers=headers, params=params)

    print(response.json())
    log.info(json.dumps(response.json(), indent=4, sort_keys=True))

    twitter_tickers = get_tickers_from_tweets(log, response.json()['data'])
    return twitter_tickers


def get_tickers_from_tweets(log, tweets):
    log.info('in get_tickers_from_tweets')

    ticker_list = []
    tickers_and_tweets = []

    for tweet in tweets:
        # print(f'tweet: {tweet}')
        tweet_text = tweet['text']
        tweet_words = tweet_text.split()

        for word in tweet_words:
            if word.startswith('$') and word.isupper() and not contains_number(word):
                word = remove_emoji(word)
                word = remove_punctuation(word)
                ticker_list.append(word)

                #dictionary of tweet and ticker
                ticker_tweet_dict = {}
                ticker_tweet_dict['ticker'] = word
                ticker_tweet_dict['tweet'] = tweet_text
                tickers_and_tweets.append(ticker_tweet_dict)

    log.info(f'Twitter tickers_and_tweets: {json.dumps(tickers_and_tweets, indent=4)}')

    combined_list = combine_tweets_by_ticker(log, tickers_and_tweets)
    return combined_list

def combine_tweets_by_ticker(log, tickers_and_tweets):
    log.info('in combine_tweets_by_ticker')

    ticker_tweets = {}
    ticker_counts = {}

    for entry in tickers_and_tweets:
        ticker = entry['ticker']
        tweet = entry['tweet']

        if ticker in ticker_tweets:
            if tweet not in ticker_tweets[ticker]:
                ticker_tweets[ticker].append(tweet)
                ticker_counts[ticker] += 1
        else:
            ticker_tweets[ticker] = [tweet]
            ticker_counts[ticker] = 1

    #create a list of dictionairies with ticker, tweets, and count
    combined_list = [{'ticker': ticker, 'tweets': tweets, 'tweet_count': count} for ticker, tweets in ticker_tweets.items() for count in [ticker_counts[ticker]]]
    log.info(f'combined_list before sort: {json.dumps(combined_list, indent=4)}')

    #sort by the most mentioned / biggest count
    combined_list.sort(key=lambda x: x['tweet_count'], reverse=True)
    log.info(f'combined_list after sort: {json.dumps(combined_list, indent=4)}')

    #filter the list to only include items with a count greater than X 
    combined_list = [list_element for list_element in combined_list if list_element['tweet_count'] > STOCK_TWEET_MIN_COUNT]
    log.info(f'combined_list after filter by minimum count: {json.dumps(combined_list, indent=4)}')

    return combined_list