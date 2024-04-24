import yfinance as yf
import random 
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

unix_timestamp = 1713563085

TICKERS = [
"AAPL",  # Apple Inc.
"MSFT",  # Microsoft Corporation
"AMZN",  # Amazon.com, Inc.
"GOOGL", # Alphabet Inc. - Class A shares
"BRK.A", # Berkshire Hathaway Inc. - Class A shares
"BRK.B", # Berkshire Hathaway Inc. - Class B shares
"META",  # Meta Platforms, Inc., formerly Facebook
"TSLA",  # Tesla, Inc.
"JNJ",   # Johnson & Johnson
"V",     # Visa Inc.
"JPM",   # JPMorgan Chase & Co.
"SPY",   # SPDR S&P 500 ETF Trust
"QQQ",   # Invesco QQQ Trust
"IWM",   # iShares Russell 2000 ETF
"VTI"    # Vanguard Total Stock Market ETF
]
def getTicker() ->str:
    ticker =random.choice(TICKERS)
    return ticker

def getNews(ticker) -> dict:
    print(ticker)
    news = yf.Ticker(ticker).news[0]


    publish_time = datetime.fromtimestamp(news['providerPublishTime'])
    
    # Get the current timestamp and subtract 24 hours
    current_time = datetime.now()
    time_24hrs_ago = current_time - timedelta(hours=24)
    
    # Check if the article was published within the last 24 hours
    if publish_time >= time_24hrs_ago:
        # Format the datetime object to a desired string representation
        formatted_time = publish_time.strftime("%A, %B %d, %Y, at %I:%M:%S %p")
        print(formatted_time)
        # Print or process the article as needed
        print(news['title'])
        # print(new['content'])
        print('---')
        url = news["link"]
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the content with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the article content, you might need to inspect the HTML structure
            # and tags to adjust the method of finding the correct content.
            for pragraph in soup.find_all('p'):
                if 'class=' in pragraph.text:
                    continue
                else:
                    print(pragraph.text)
            
            # Save or print the content
            # if article:
            #     print(article.text)
            # else:
            #     print(f'Article content not found for URL: {url}')
        else:
            print(f'Failed to retrieve the page: {url}')

    
    return ''
        

getNews()