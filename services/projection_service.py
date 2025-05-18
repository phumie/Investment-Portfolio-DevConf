import pandas as pd
import numpy as np
from utils.constants import RISK_RETURNS
from utils.helpers import calculate_future_value
import config

def get_portfolio_projection(user):
    """Get projection data for the portfolio"""
    # Get parameters
    initial_investment = float(user.initial_investment)
    monthly_contribution = float(user.monthly_contribution)
    annual_contribution = monthly_contribution * 12
    years = user.investment_duration
    risk_level = user.risk_tolerance
    
    # Get returns based on risk level
    tech_return = RISK_RETURNS[risk_level]['tech']
    complementary_return = RISK_RETURNS[risk_level]['complementary']
    sp500_return = RISK_RETURNS[risk_level]['sp500']
    
    # Calculate weighted portfolio return
    portfolio_return = (tech_return * user.tech_allocation) + (complementary_return * user.complementary_allocation)
    
    # Generate year range
    years_range = list(range(years + 1))
    
    # Initialize projection data
    portfolio_values = []
    sp500_values = []
    initial_plus_contributions = []
    
    # Calculate values for each year
    for year in years_range:
        # Portfolio value
        portfolio_value = calculate_future_value(
            initial_investment,
            portfolio_return,
            year,
            annual_contribution
        )
        portfolio_values.append(portfolio_value)
        
        # S&P 500 benchmark
        sp500_value = calculate_future_value(
            initial_investment,
            sp500_return,
            year,
            annual_contribution
        )
        sp500_values.append(sp500_value)
        
        # Initial investment plus contributions
        contributions_value = initial_investment + (annual_contribution * year)
        initial_plus_contributions.append(contributions_value)
    
    # Create dataframe
    projection_data = pd.DataFrame({
        'year': years_range,
        'portfolio_value': portfolio_values,
        'sp500_benchmark': sp500_values,
        'initial_plus_contributions': initial_plus_contributions
    })
    
    return projection_data

def calculate_alpha(user):
    """Calculate alpha (outperformance vs S&P 500)"""
    projection_data = get_portfolio_projection(user)
    
    # Calculate yearly alpha
    alpha_yearly = []
    alpha_cumulative = []
    cumulative = 0
    
    # Skip first year (year 0) as there's no return yet
    for i in range(1, len(projection_data)):
        prev_portfolio = projection_data['portfolio_value'][i-1]
        curr_portfolio = projection_data['portfolio_value'][i]
        prev_sp500 = projection_data['sp500_benchmark'][i-1]
        curr_sp500 = projection_data['sp500_benchmark'][i]
        
        # Calculate returns
        portfolio_return = curr_portfolio / prev_portfolio - 1
        sp500_return = curr_sp500 / prev_sp500 - 1
        
        # Calculate alpha
        alpha = portfolio_return - sp500_return
        alpha_yearly.append(alpha)
        
        # Add to cumulative alpha
        cumulative += alpha
        alpha_cumulative.append(cumulative)
    
    # Add 0 for year 0
    alpha_yearly = [0] + alpha_yearly
    alpha_cumulative = [0] + alpha_cumulative
    
    # Create dataframe
    alpha_data = pd.DataFrame({
        'year': projection_data['year'],
        'alpha_yearly': alpha_yearly,
        'alpha_cumulative': alpha_cumulative
    })
    
    return alpha_data
