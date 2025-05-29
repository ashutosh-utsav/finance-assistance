import re

def analyze_portfolio_risk(current_portfolio: dict, previous_portfolio: dict, earnings_data: list) -> dict:
    """
    Analyzes portfolio risk by comparing the current portfolio to a previous state
    and analyzing the sentiment of recent earnings news.
    """
    # Portfolio Change Analysis 
    change_summary_lines = []
    if not previous_portfolio:
        change_summary_lines.append("No previous day data available to calculate portfolio changes.")
    else:
        all_tickers = set(current_portfolio.keys()) | set(previous_portfolio.keys())
        for ticker in sorted(list(all_tickers)):
            current_pct = current_portfolio.get(ticker, {}).get('allocation', 0) * 100
            previous_pct = previous_portfolio.get(ticker, {}).get('allocation', 0) * 100
            
            change = current_pct - previous_pct
            
            if abs(change) > 0.01: # Only report notable changes
                change_summary_lines.append(
                    f"Allocation for {ticker} changed by {change:+.1f} percentage points (from {previous_pct:.1f}% to {current_pct:.1f}%)."
                )

    # Earnings News Sentiment Analysis 
    sentiment_summary_lines = []
    positive_keywords = ['beat', 'beats', 'exceeds', 'strong', 'rises', 'booms']
    negative_keywords = ['miss', 'missed', 'misses', 'plunge', 'weak', 'falls', 'glut']

    for headline in earnings_data:
        ticker_match = re.search(r'\[(.*?)\]', headline)
        ticker = ticker_match.group(1) if ticker_match else "Unknown"
        
        headline_lower = headline.lower()
        if any(keyword in headline_lower for keyword in positive_keywords):
            sentiment_summary_lines.append(f"{ticker}: Positive sentiment detected in news.")
        elif any(keyword in headline_lower for keyword in negative_keywords):
            sentiment_summary_lines.append(f"{ticker}: Negative sentiment detected in news.")
            
    # Assemble Final Analysis 
    analysis = {
        "portfolio_change_analysis": change_summary_lines or ["No significant allocation changes detected."],
        "portfolio_sentiment_analysis": sentiment_summary_lines or ["No news with strong sentiment found for the portfolio."]
    }
    return analysis