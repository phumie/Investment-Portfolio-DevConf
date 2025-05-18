import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generate_etf_historical_data(symbol, start_date, end_date, initial_price=100.0, annual_return=0.1, volatility=0.15):
    """
    Generate synthetic historical data for an ETF
    
    Args:
        symbol: ETF symbol
        start_date: Start date for the data
        end_date: End date for the data
        initial_price: Initial price
        annual_return: Expected annual return
        volatility: Annual volatility
    
    Returns:
        DataFrame with historical data
    """
    # Convert dates to datetime if they are strings
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Calculate number of days
    days = (end_date - start_date).days
    
    # Generate dates
    dates = [start_date + timedelta(days=i) for i in range(days)]
    
    # Set random seed based on symbol for consistency
    random.seed(sum(ord(c) for c in symbol))
    
    # Calculate daily parameters
    daily_return = annual_return / 252
    daily_volatility = volatility / np.sqrt(252)
    
    # Generate random returns
    returns = np.random.normal(daily_return, daily_volatility, days)
    
    # Calculate prices
    prices = [initial_price]
    for ret in returns:
        prices.append(prices[-1] * (1 + ret))
    prices = prices[1:]  # Remove the initial price
    
    # Create dataframe
    df = pd.DataFrame({
        'date': dates,
        'price': prices
    })
    
    return df

def get_sp500_historical_data(start_date, end_date):
    """
    Generate synthetic historical data for S&P 500
    
    Args:
        start_date: Start date for the data
        end_date: End date for the data
    
    Returns:
        DataFrame with historical data
    """
    return generate_etf_historical_data(
        symbol='SPY',
        start_date=start_date,
        end_date=end_date,
        initial_price=4000.0,
        annual_return=0.08,
        volatility=0.15
    )
