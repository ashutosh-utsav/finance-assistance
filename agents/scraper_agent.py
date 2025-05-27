import requests
import feedparser
from bs4 import BeautifulSoup

# Define the tickers you want to get news for
TICKERS = ["TSM", "005930.KS", "BIDU", "BABA"]

# Keywords to identify earnings-related news
EARNINGS_KEYWORDS = ['earnings', 'beat', 'miss', 'estimate', 'surprise', 'profit', 'revenue']

def get_earnings_surprises(tickers: list = TICKERS) -> list:
    """
    Scrapes RSS feeds for a list of stock tickers to find news about
    earnings surprises.

    Args:
        tickers (list): A list of stock ticker symbols.

    Returns:
        list: A list of strings, where each string is the title of a
              news article related to an earnings report.
    """
    earnings_news = []
    
    # Set a user-agent to mimic a browser and avoid being blocked
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    for ticker in tickers:
        # Construct the Yahoo Finance RSS feed URL for each ticker
        url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US"
        
        try:
            # Fetch the RSS feed content
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

            # Parse the feed
            feed = feedparser.parse(response.content)

            # Iterate through each news item in the feed
            for entry in feed.entries:
                title = entry.title
                
                # Check if any of our keywords are in the title (case-insensitive)
                if any(keyword in title.lower() for keyword in EARNINGS_KEYWORDS):
                    # Clean up any potential HTML in the summary for future use
                    soup = BeautifulSoup(entry.summary, 'html.parser')
                    summary_text = soup.get_text()

                    # For this step, the title is a great summary.
                    # We add the ticker for context.
                    earnings_news.append(f"[{ticker}] {title}")

        except requests.exceptions.RequestException as e:
            print(f"Could not fetch news for {ticker}: {e}")
            continue # Move to the next ticker

    # Return a unique list of news items
    return list(set(earnings_news))

# This part allows you to test the file directly
if __name__ == '__main__':
    print("--- Scraping for Earnings News ---")
    
    # Note: RSS feeds are dynamic. If there is no recent earnings news,
    # this list might be empty.
    surprises = get_earnings_surprises()
    
    if surprises:
        for item in surprises:
            print(item)
    else:
        print("No recent earnings-related news found for the given tickers.")
        print("This is normal if companies haven't reported recently.")