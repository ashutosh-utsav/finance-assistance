import re
import json

def analyze_portfolio_risk(portfolio_allocation: dict, earnings_data: list) -> dict:
    """
    Analyzes portfolio risk based on allocation changes and earnings news.

    Args:
        portfolio_allocation (dict): A dictionary of current ticker allocations.
                                     Example: {'TSM': 0.40, 'BABA': 0.15, ...}
        earnings_data (list): A list of scraped earnings headlines.
                              Example: ["[BABA] Alibaba Beats Revenue Estimates..."]

    Returns:
        dict: An analysis summary with AUM changes and earnings insights.
    """
    # --- 1. Analyze Portfolio Allocation Change (using mock 'yesterday' data) ---
    # As per the plan, we'll create mock data for the previous day's portfolio
    # to demonstrate the change analysis.
    previous_allocation = {
        "TSM": 0.38,      # Was 38%, now 40%
        "005930.KS": 0.32,# Was 32%, now 30%
        "BABA": 0.15,     # No change
        "BIDU": 0.15      # No change
    }
    
    # Calculate the total change in AUM. This is a simplified metric.
    # A real-world calculation would be more complex.
    aum_change_summary = []
    for ticker, current_pct in portfolio_allocation.items():
        previous_pct = previous_allocation.get(ticker, 0)
        change = (current_pct - previous_pct) * 100 # Change in percentage points
        if abs(change) > 0.1: # Only report notable changes
             aum_change_summary.append(f"{ticker} allocation changed by {change:+.1f}% points")

    # --- 2. Parse Earnings Surprises from Scraped Text ---
    # This function determines sentiment from headlines rather than parsing a specific %.
    earnings_summary = []
    positive_keywords = ['beat', 'beats', 'exceeds', 'strong', 'rises', 'booms']
    negative_keywords = ['miss', 'missed', 'misses', 'plunge', 'weak', 'falls', 'glut']

    for headline in earnings_data:
        # Extract ticker using regex, e.g., "[BABA]" -> "BABA"
        ticker_match = re.search(r'\[(.*?)\]', headline)
        ticker = ticker_match.group(1) if ticker_match else "Unknown"
        
        # Check for positive or negative keywords
        headline_lower = headline.lower()
        if any(keyword in headline_lower for keyword in positive_keywords):
            earnings_summary.append(f"{ticker}: Beat/Positive outlook reported.")
        elif any(keyword in headline_lower for keyword in negative_keywords):
            earnings_summary.append(f"{ticker}: Miss/Negative outlook reported.")

    # --- 3. Assemble the Final Analysis ---
    analysis = {
        "portfolio_change_analysis": aum_change_summary or ["No significant allocation changes."],
        "earnings_analysis_summary": earnings_summary or ["No major earnings news found."]
    }

    return analysis


# This part allows you to test the file directly
if __name__ == '__main__':
    print("--- Analysis Agent Test ---")

    # Mock data that would come from your other agents
    # 1. From api_agent.py (get_portfolio_allocation)
    mock_portfolio = {
        "TSM": 0.40,
        "005930.KS": 0.30,
        "BABA": 0.15,
        "BIDU": 0.15
    }

    # 2. From scraper_agent.py (get_earnings_surprises)
    mock_earnings = [
        "[BABA] Alibaba Beats Revenue Estimates On E-Commerce Strength",
        "[005930.KS] Samsung Electronics flags a likely 96% plunge in Q2 profit due to a chip glut.",
        "[TSM] TSMC forecasts strong Q3 revenue, citing massive AI chip demand."
    ]

    # Run the analysis
    final_analysis = analyze_portfolio_risk(mock_portfolio, mock_earnings)

    # Pretty-print the JSON output
    print("\n--- Generated Analysis ---")
    print(json.dumps(final_analysis, indent=4))