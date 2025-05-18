import streamlit as st
import pandas as pd
from services.portfolio_service import calculate_etf_allocations
from services.etf_service import get_etf_details, get_etf_return

def display_portfolio_summary(user, current_value):
    """Display a summary of the portfolio"""
    # Calculate projected value at end of investment duration
    # This is a simplified calculation for display purposes
    annual_return = 0.08  # Assumed annual return for summary display
    years = user.investment_duration
    monthly_contribution = user.monthly_contribution
    
    future_value = current_value * (1 + annual_return) ** years
    if monthly_contribution > 0:
        # Calculate future value of monthly contributions
        future_value_contributions = monthly_contribution * 12 * ((1 + annual_return) ** years - 1) / annual_return
        future_value += future_value_contributions
    
    # Calculate total contributions
    total_contributions = user.initial_investment + (monthly_contribution * 12 * years)
    
    # Calculate projected profit
    projected_profit = future_value - total_contributions
    
    # Create a summary dataframe
    summary_data = {
        'Metric': [
            'Current Investment', 
            'Monthly Contribution',
            'Investment Duration',
            'Risk Level',
            'Projected Final Value',
            'Total Contributions',
            'Projected Profit',
            'Target vs S&P 500'
        ],
        'Value': [
            f'R{user.initial_investment:,.2f}',
            f'R{user.monthly_contribution:,.2f}',
            f'{user.investment_duration} Years',
            user.risk_tolerance,
            f'R{future_value:,.2f}',
            f'R{total_contributions:,.2f}',
            f'R{projected_profit:,.2f}',
            '+1% Annual Alpha'
        ]
    }
    
    summary_df = pd.DataFrame(summary_data)
    
    # Style the dataframe
    st.dataframe(
        summary_df,
        hide_index=True,
        column_config={
            'Metric': st.column_config.TextColumn('Metric'),
            'Value': st.column_config.TextColumn('Value')
        },
        use_container_width=True
    )

def display_etf_list(user):
    """Display a list of ETFs in the portfolio with their allocations"""
    # Get ETF allocations
    etf_allocations = calculate_etf_allocations(user)
    
    # Create dataframes for tech and complementary ETFs
    tech_etfs = []
    complementary_etfs = []
    
    for etf in etf_allocations:
        # Get ETF details and returns
        details = get_etf_details(etf['symbol'])
        returns = get_etf_return(etf['symbol'])
        
        etf_data = {
            'Symbol': etf['symbol'],
            'Name': details['name'],
            'Category': etf['category'],
            'Allocation (%)': f"{etf['allocation'] * 100:.2f}%",
            'Value (ZAR)': f"R{etf['value']:,.2f}",
            '1Y Return (%)': f"{returns['1y'] * 100:.2f}%",
            '3Y Return (%)': f"{returns['3y'] * 100:.2f}%",
            '5Y Return (%)': f"{returns['5y'] * 100:.2f}%"
        }
        
        if etf['category'] == 'Tech ETFs':
            tech_etfs.append(etf_data)
        else:
            complementary_etfs.append(etf_data)
    
    # Create dataframes
    tech_df = pd.DataFrame(tech_etfs)
    complementary_df = pd.DataFrame(complementary_etfs)
    
    # Display Tech ETFs
    st.subheader("Tech ETFs")
    if tech_df.empty:
        st.info("No Tech ETFs selected")
    else:
        st.dataframe(
            tech_df,
            hide_index=True,
            use_container_width=True
        )
    
    # Display Complementary ETFs
    st.subheader("Complementary ETFs")
    if complementary_df.empty:
        st.info("No Complementary ETFs selected")
    else:
        st.dataframe(
            complementary_df,
            hide_index=True,
            use_container_width=True
        )
