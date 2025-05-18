import pandas as pd
from services.etf_service import get_etf_details, get_etf_return

def get_portfolio_allocation(user):
    """Get the portfolio allocation data for charts"""
    allocation_data = {
        'category': ['Tech ETFs', 'Complementary ETFs'],
        'allocation': [user.tech_allocation, user.complementary_allocation]
    }
    
    return pd.DataFrame(allocation_data)

def calculate_etf_allocations(user):
    """Calculate the allocation for each ETF in the portfolio"""
    # Get ETF lists
    tech_etfs = user.tech_etfs.split(',') if user.tech_etfs else []
    complementary_etfs = user.complementary_etfs.split(',') if user.complementary_etfs else []
    
    # Calculate allocations
    tech_etf_count = len(tech_etfs)
    complementary_etf_count = len(complementary_etfs)
    
    # Handle empty ETF lists
    if tech_etf_count == 0 and complementary_etf_count == 0:
        return []
    
    # Equal allocation within each category
    tech_allocation_per_etf = user.tech_allocation / max(1, tech_etf_count)
    complementary_allocation_per_etf = user.complementary_allocation / max(1, complementary_etf_count)
    
    # Calculate portfolio value
    portfolio_value = get_portfolio_value(user)
    
    # Create allocation data
    allocations = []
    
    for symbol in tech_etfs:
        allocations.append({
            'symbol': symbol,
            'category': 'Tech ETFs',
            'allocation': tech_allocation_per_etf,
            'value': portfolio_value * tech_allocation_per_etf
        })
    
    for symbol in complementary_etfs:
        allocations.append({
            'symbol': symbol,
            'category': 'Complementary ETFs',
            'allocation': complementary_allocation_per_etf,
            'value': portfolio_value * complementary_allocation_per_etf
        })
    
    return allocations

def get_portfolio_value(user):
    """Get the current value of the portfolio"""
    # For simplicity, we'll just return the initial investment
    # In a real app, this would calculate current value based on ETF prices
    return float(user.initial_investment)

def get_weighted_portfolio_return(user):
    """Calculate the weighted return of the portfolio based on ETF allocations"""
    # Get ETF allocations
    allocations = calculate_etf_allocations(user)
    
    if not allocations:
        return {
            '1y': 0,
            '3y': 0,
            '5y': 0
        }
    
    # Initialize weighted returns
    weighted_returns = {
        '1y': 0,
        '3y': 0,
        '5y': 0
    }
    
    # Calculate weighted returns
    for etf in allocations:
        symbol = etf['symbol']
        allocation = etf['allocation']
        
        # Get ETF returns
        returns = get_etf_return(symbol)
        
        # Add weighted returns
        for period in weighted_returns:
            weighted_returns[period] += returns[period] * allocation
    
    return weighted_returns
