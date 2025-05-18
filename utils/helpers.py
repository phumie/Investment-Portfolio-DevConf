import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from utils.constants import RISK_RETURNS, RISK_VOLATILITY

def generate_random_seed():
    """Generate a random seed for reproducible randomness"""
    return int(datetime.now().timestamp())

def get_random_return(risk_level, category):
    """Get a random return based on risk level and category"""
    mean_return = RISK_RETURNS[risk_level][category]
    volatility = RISK_VOLATILITY[risk_level][category]
    
    # Set random seed for reproducibility
    np.random.seed(generate_random_seed())
    
    # Generate a random return from a normal distribution
    return max(-0.3, min(0.4, np.random.normal(mean_return, volatility)))

def generate_date_range(start_date, periods, freq='Y'):
    """Generate a date range"""
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    
    date_range = pd.date_range(start=start_date, periods=periods, freq=freq)
    return date_range

def format_currency(value):
    """Format a value as currency"""
    return f"R{value:,.2f}"

def format_percentage(value):
    """Format a value as percentage"""
    return f"{value * 100:.2f}%"

def calculate_cagr(initial_value, final_value, years):
    """Calculate Compound Annual Growth Rate"""
    if initial_value <= 0 or years <= 0:
        return 0
    
    return (final_value / initial_value) ** (1 / years) - 1

def calculate_future_value(present_value, rate, time, pmt=0, pmt_type=0):
    """
    Calculate future value of an investment
    
    Args:
        present_value: Initial investment amount
        rate: Annual interest rate (decimal)
        time: Time in years
        pmt: Regular payment amount (default 0)
        pmt_type: When payments are made (0 = end of period, 1 = beginning of period)
    
    Returns:
        Future value of the investment
    """
    if rate == 0:
        return present_value + pmt * time
    
    # Future value of initial investment
    fv_principal = present_value * (1 + rate) ** time
    
    # Future value of regular payments
    if pmt != 0:
        fv_annuity = pmt * ((1 + rate) ** time - 1) / rate
        
        # Adjust for payment timing
        if pmt_type == 1:  # Beginning of period
            fv_annuity *= (1 + rate)
    else:
        fv_annuity = 0
    
    return fv_principal + fv_annuity
