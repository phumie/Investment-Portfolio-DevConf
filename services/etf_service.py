import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from utils.helpers import get_random_return, generate_date_range
from utils.constants import SP500_SECTOR_WEIGHTS

# Dictionary to store ETF data to avoid regenerating it
cached_etf_data = {}

def get_tech_etfs():
    """Get a list of tech ETFs"""
    tech_etfs = [
        {'symbol': 'XLK', 'name': 'Technology Select Sector SPDR Fund', 'expense_ratio': 0.0010},
        {'symbol': 'VGT', 'name': 'Vanguard Information Technology ETF', 'expense_ratio': 0.0010},
        {'symbol': 'IYW', 'name': 'iShares U.S. Technology ETF', 'expense_ratio': 0.0041},
        {'symbol': 'FTEC', 'name': 'Fidelity MSCI Information Technology Index ETF', 'expense_ratio': 0.0008},
        {'symbol': 'IGM', 'name': 'iShares Expanded Tech Sector ETF', 'expense_ratio': 0.0046},
        {'symbol': 'QTEC', 'name': 'First Trust NASDAQ-100 Technology Sector Index Fund', 'expense_ratio': 0.0057},
        {'symbol': 'RYT', 'name': 'Invesco S&P 500 Equal Weight Technology ETF', 'expense_ratio': 0.0040},
        {'symbol': 'PSI', 'name': 'Invesco Dynamic Semiconductors ETF', 'expense_ratio': 0.0057},
        {'symbol': 'SOXX', 'name': 'iShares Semiconductor ETF', 'expense_ratio': 0.0035},
        {'symbol': 'SMH', 'name': 'VanEck Semiconductor ETF', 'expense_ratio': 0.0035},
        {'symbol': 'TECL', 'name': 'Direxion Daily Technology Bull 3X Shares', 'expense_ratio': 0.0095},
        {'symbol': 'ARKW', 'name': 'ARK Next Generation Internet ETF', 'expense_ratio': 0.0075},
        {'symbol': 'SKYY', 'name': 'First Trust Cloud Computing ETF', 'expense_ratio': 0.0060},
        {'symbol': 'CIBR', 'name': 'First Trust NASDAQ Cybersecurity ETF', 'expense_ratio': 0.0060},
        {'symbol': 'HACK', 'name': 'ETFMG Prime Cyber Security ETF', 'expense_ratio': 0.0060}
    ]
    return tech_etfs

def get_complementary_etfs():
    """Get a list of complementary ETFs (non-tech sectors)"""
    complementary_etfs = [
        {'symbol': 'XLE', 'name': 'Energy Select Sector SPDR Fund', 'sector': 'Energy', 'expense_ratio': 0.0010},
        {'symbol': 'XLB', 'name': 'Materials Select Sector SPDR Fund', 'sector': 'Materials', 'expense_ratio': 0.0010},
        {'symbol': 'XLI', 'name': 'Industrial Select Sector SPDR Fund', 'sector': 'Industrials', 'expense_ratio': 0.0010},
        {'symbol': 'XLY', 'name': 'Consumer Discretionary Select Sector SPDR Fund', 'sector': 'Consumer Discretionary', 'expense_ratio': 0.0010},
        {'symbol': 'XLP', 'name': 'Consumer Staples Select Sector SPDR Fund', 'sector': 'Consumer Staples', 'expense_ratio': 0.0010},
        {'symbol': 'XLV', 'name': 'Health Care Select Sector SPDR Fund', 'sector': 'Healthcare', 'expense_ratio': 0.0010},
        {'symbol': 'XLF', 'name': 'Financial Select Sector SPDR Fund', 'sector': 'Financials', 'expense_ratio': 0.0010},
        {'symbol': 'XLRE', 'name': 'Real Estate Select Sector SPDR Fund', 'sector': 'Real Estate', 'expense_ratio': 0.0010},
        {'symbol': 'XLC', 'name': 'Communication Services Select Sector SPDR Fund', 'sector': 'Communication Services', 'expense_ratio': 0.0010},
        {'symbol': 'XLU', 'name': 'Utilities Select Sector SPDR Fund', 'sector': 'Utilities', 'expense_ratio': 0.0010},
        {'symbol': 'VDE', 'name': 'Vanguard Energy ETF', 'sector': 'Energy', 'expense_ratio': 0.0010},
        {'symbol': 'VAW', 'name': 'Vanguard Materials ETF', 'sector': 'Materials', 'expense_ratio': 0.0010},
        {'symbol': 'VIS', 'name': 'Vanguard Industrials ETF', 'sector': 'Industrials', 'expense_ratio': 0.0010},
        {'symbol': 'VCR', 'name': 'Vanguard Consumer Discretionary ETF', 'sector': 'Consumer Discretionary', 'expense_ratio': 0.0010},
        {'symbol': 'VDC', 'name': 'Vanguard Consumer Staples ETF', 'sector': 'Consumer Staples', 'expense_ratio': 0.0010}
    ]
    return complementary_etfs

def get_etf_details(symbol):
    """Get details for a specific ETF"""
    # Look for ETF in tech ETFs
    for etf in get_tech_etfs():
        if etf['symbol'] == symbol:
            etf['category'] = 'Tech ETFs'
            return etf
    
    # Look for ETF in complementary ETFs
    for etf in get_complementary_etfs():
        if etf['symbol'] == symbol:
            etf['category'] = 'Complementary ETFs'
            return etf
    
    # ETF not found
    return {
        'symbol': symbol,
        'name': f'Unknown ETF ({symbol})',
        'category': 'Unknown',
        'expense_ratio': 0.0050
    }

def get_etf_return(symbol):
    """Get historical returns for a specific ETF"""
    # We'll generate random returns based on the ETF category
    etf = get_etf_details(symbol)
    
    # Set seed based on symbol for consistency
    random.seed(sum(ord(c) for c in symbol))
    
    # Base returns by category
    if etf['category'] == 'Tech ETFs':
        base_return_1y = 0.12 + random.uniform(-0.05, 0.10)
        base_return_3y = 0.15 + random.uniform(-0.05, 0.15)
        base_return_5y = 0.18 + random.uniform(-0.05, 0.20)
    else:
        base_return_1y = 0.08 + random.uniform(-0.05, 0.07)
        base_return_3y = 0.10 + random.uniform(-0.05, 0.10)
        base_return_5y = 0.12 + random.uniform(-0.05, 0.15)
    
    # Return dictionary
    return {
        '1y': base_return_1y,
        '3y': base_return_3y,
        '5y': base_return_5y
    }

def get_etf_historical_data(symbol, years=5):
    """Get historical price data for a specific ETF"""
    # Check if we've already generated data for this ETF
    if symbol in cached_etf_data:
        return cached_etf_data[symbol]
    
    # Get ETF details
    etf = get_etf_details(symbol)
    category = etf.get('category', 'Unknown')
    
    # Set seed based on symbol for consistency
    random.seed(sum(ord(c) for c in symbol))
    
    # Generate dates
    end_date = datetime.now()
    start_date = end_date - timedelta(days=years * 365)
    dates = pd.date_range(start=start_date, end=end_date, freq='M')
    
    # Base starting value
    start_value = 100.0
    
    # Generate monthly returns based on category
    if category == 'Tech ETFs':
        monthly_returns = np.random.normal(0.01, 0.04, size=len(dates))
    else:
        monthly_returns = np.random.normal(0.007, 0.03, size=len(dates))
    
    # Calculate cumulative values
    values = [start_value]
    for ret in monthly_returns:
        values.append(values[-1] * (1 + ret))
    values = values[1:]  # Remove the initial value
    
    # Create normalized values
    normalized_values = [v / values[0] for v in values]
    
    # Create dataframe
    df = pd.DataFrame({
        'date': dates,
        'value': values,
        'value_normalized': normalized_values
    })
    
    # Cache the data
    cached_etf_data[symbol] = df
    
    return df
