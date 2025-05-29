import yfinance as yf
import pandas as pd

def get_asia_tech_data(tickers: list) -> dict:
    """
    Fetches the latest stock price and key metrics for a given list of tickers.
    NOTE: This function is kept for potential future use but is not the primary
    way portfolio data is retrieved in the dynamic setup.
    """
    if not tickers:
        return {}
    try:
        ticker_data = yf.Tickers(tickers)
        data_dict = {}
        for ticker_object in ticker_data.tickers.values():
            stock_info = ticker_object.info
            if stock_info and stock_info.get('symbol'):
                ticker_symbol = stock_info.get('symbol')
                data_dict[ticker_symbol] = {
                    "companyName": stock_info.get('longName'),
                    "currentPrice": stock_info.get('regularMarketPreviousClose'),
                    "currency": stock_info.get('currency')
                }
        return data_dict
    except Exception as e:
        print(f"An error occurred in get_asia_tech_data: {e}")
        return {}

