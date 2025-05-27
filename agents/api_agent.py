import yfinance as yf
import pandas as pd

# Define the stock tickers for the Asian tech companies
# TSM for TSMC, 005930.KS for Samsung, BIDU for Baidu, BABA for Alibaba
ASIA_TECH_TICKERS = ["TSM", "005930.KS", "BIDU", "BABA"]

def get_asia_tech_data(tickers: list = ASIA_TECH_TICKERS) -> dict:
    """
    Fetches the latest stock price and key metrics for a list of tickers.

    Args:
        tickers (list): A list of stock ticker symbols.

    Returns:
        dict: A dictionary where each key is a ticker and the value is
              another dictionary containing the company's long name,
              the latest price, and the currency.
              Returns an empty dictionary if data can't be fetched.
    """
    try:
        # Create a Tickers object
        ticker_data = yf.Tickers(tickers)
        
        # Dictionary to hold our cleaned data
        data_dict = {}

        # Loop through each ticker object in the Tickers list
        for ticker_object in ticker_data.tickers.values():
            stock_info = ticker_object.info
            
            # Check if info was successfully fetched for the ticker
            if stock_info and stock_info.get('symbol'):
                ticker_symbol = stock_info.get('symbol')
                
                data_dict[ticker_symbol] = {
                    "companyName": stock_info.get('longName'),
                    "currentPrice": stock_info.get('regularMarketPreviousClose'),
                    "currency": stock_info.get('currency')
                }
        
        return data_dict

    except Exception as e:
        print(f"An error occurred: {e}")
        return {}

def get_portfolio_allocation() -> dict:
    """
    Returns a hardcoded portfolio allocation.

    Returns:
        dict: A dictionary representing the portfolio allocation percentages.
    """
    # This is hardcoded for now as per the project plan.
    # In a real-world scenario, this might come from another API or a database.
    portfolio = {
        "TSM": 0.40,      # 40%
        "005930.KS": 0.30,# 30%
        "BABA": 0.15,     # 15%
        "BIDU": 0.15      # 15%
    }
    return portfolio

# This part allows you to test the file directly
if __name__ == '__main__':
    print("--- Fetching Asia Tech Stock Data ---")
    stock_data = get_asia_tech_data()
    if stock_data:
        # Pretty print the dictionary
        import json
        print(json.dumps(stock_data, indent=4))
    else:
        print("Could not fetch stock data.")

    print("\n--- Fetching Hardcoded Portfolio Allocation ---")
    portfolio = get_portfolio_allocation()
    print(portfolio)