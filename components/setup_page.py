import streamlit as st
import pandas as pd
from database.db_service import create_user, get_user_by_id
from utils.constants import PAGES, RISK_LEVELS
from services.etf_service import get_tech_etfs, get_complementary_etfs
import config

def show_setup_page():
    """Display the setup page for user information and initial investment details"""
    st.header("Portfolio Setup")
    
    # Check if user is already set up
    if st.session_state.user_id is not None:
        user = get_user_by_id(st.session_state.user_id)
        st.success(f"Welcome back, {user.first_name} {user.last_name}!")
        
        # Allow user to proceed to dashboard
        if st.button("Go to Dashboard"):
            st.session_state.page = PAGES["DASHBOARD"]
            st.rerun()
        
        # Allow user to start over
        if st.button("Start Over with New Profile"):
            st.session_state.user_id = None
            st.rerun()
            
        return
    
    # Form for collecting user information
    with st.form("user_setup_form"):
        st.subheader("Personal Information")
        
        # Two columns for first and last name
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name", help="Enter your first name")
        
        with col2:
            last_name = st.text_input("Last Name", help="Enter your last name")
        
        # Investment details
        st.subheader("Investment Details")
        
        initial_investment = st.number_input(
            "Initial Investment Amount (ZAR)",
            min_value=1000.0,
            max_value=1000000000.0,
            value=100000.0,
            step=1000.0,
            help="Enter the amount you want to invest initially in ZAR"
        )
        
        monthly_contribution = st.number_input(
            "Monthly Contribution (ZAR)",
            min_value=0.0,
            max_value=1000000.0,
            value=0.0,
            step=100.0,
            help="Enter your monthly contribution amount (optional)"
        )
        
        # Portfolio allocation
        st.subheader("Portfolio Allocation")
        st.write(f"Default allocation based on mandate: {int(config.DEFAULT_TECH_ALLOCATION * 100)}% Tech ETFs, "
                f"{int(config.DEFAULT_COMPLEMENTARY_ALLOCATION * 100)}% Complementary ETFs")
        
        tech_allocation = st.slider(
            "Tech ETF Allocation (%)",
            min_value=60,
            max_value=80,
            value=int(config.DEFAULT_TECH_ALLOCATION * 100),
            step=1,
            help=f"Recommended: {int(config.DEFAULT_TECH_ALLOCATION * 100)}% in Tech ETFs"
        )
        
        complementary_allocation = 100 - tech_allocation
        st.write(f"Complementary ETF Allocation: {complementary_allocation}%")
        
        # Investment duration
        investment_duration = st.slider(
            "Investment Duration (Years)",
            min_value=1,
            max_value=10,
            value=config.DEFAULT_INVESTMENT_HORIZON,
            step=1,
            help="Select your investment time horizon"
        )
        
        # Risk tolerance
        risk_tolerance = st.select_slider(
            "Risk Tolerance",
            options=RISK_LEVELS,
            value="Medium",
            help="Select your risk tolerance level"
        )
        
        # ETF selections
        st.subheader("ETF Selection")
        
        # Tech ETFs
        tech_etfs = get_tech_etfs()
        tech_etf_options = [etf['symbol'] for etf in tech_etfs]
        
        selected_tech_etfs = st.multiselect(
            "Select Tech ETFs",
            options=tech_etf_options,
            default=tech_etf_options[:3],
            help="Select ETFs for the tech portion of your portfolio"
        )
        
        # Complementary ETFs
        complementary_etfs = get_complementary_etfs()
        complementary_etf_options = [etf['symbol'] for etf in complementary_etfs]
        
        selected_complementary_etfs = st.multiselect(
            "Select Complementary ETFs",
            options=complementary_etf_options,
            default=complementary_etf_options[:3],
            help="Select ETFs for the complementary portion of your portfolio"
        )
        
        # Warn if no ETFs selected
        if not selected_tech_etfs:
            st.warning("Please select at least one Tech ETF")
        
        if not selected_complementary_etfs:
            st.warning("Please select at least one Complementary ETF")
        
        # Submit button
        submitted = st.form_submit_button("Create Portfolio")
        
        if submitted:
            if not first_name or not last_name:
                st.error("Please enter your first and last name")
            elif not selected_tech_etfs or not selected_complementary_etfs:
                st.error("Please select at least one ETF from each category")
            else:
                # Convert allocations to decimal
                tech_allocation_decimal = tech_allocation / 100
                complementary_allocation_decimal = complementary_allocation / 100
                
                # Create the user and portfolio in the database
                user_id = create_user(
                    first_name=first_name,
                    last_name=last_name,
                    initial_investment=initial_investment,
                    monthly_contribution=monthly_contribution,
                    tech_allocation=tech_allocation_decimal,
                    complementary_allocation=complementary_allocation_decimal,
                    investment_duration=investment_duration,
                    risk_tolerance=risk_tolerance,
                    tech_etfs=selected_tech_etfs,
                    complementary_etfs=selected_complementary_etfs
                )
                
                # Save the user ID in session state
                st.session_state.user_id = user_id
                st.session_state.page = PAGES["DASHBOARD"]
                
                # Show success message and redirect
                st.success("Portfolio created successfully! Redirecting to dashboard...")
                st.rerun()

    # Display some information about ETFs
    with st.expander("Available ETF Information"):
        st.subheader("Tech ETFs")
        st.dataframe(pd.DataFrame(tech_etfs))
        
        st.subheader("Complementary ETFs")
        st.dataframe(pd.DataFrame(complementary_etfs))
