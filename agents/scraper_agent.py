import requests
import feedparser

def get_earnings_surprises(portfolio: dict) -> list:
    """
    Scrapes ALL recent RSS headlines for a portfolio of stocks.
    The keyword filter has been removed to ensure data is always available
    for the retriever agent.
    """
    earnings_news = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    if not portfolio:
        return []

    for ticker, details in portfolio.items():
        region = details.get('region', 'US')
        lang = details.get('lang', 'en-US')
        
        url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region={region}&lang={lang}"
        print(f"Scraping news for {ticker} from region: {region}")

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            feed = feedparser.parse(response.content)
            
            for entry in feed.entries:
                title = entry.title
                earnings_news.append(f"[{ticker}] {title}")
                
        except requests.exceptions.RequestException as e:
            print(f"Could not fetch news for {ticker}: {e}")
            continue
            
    return list(set(earnings_news))