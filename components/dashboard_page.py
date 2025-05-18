import streamlit as st
import pandas as pd
from database.db_service import get_user_by_id, update_user_portfolio
from utils.constants import PAGES, RISK_LEVELS
from services.portfolio_service import get_portfolio_allocation, get_portfolio_value
from services.projection_service import get_portfolio_projection, calculate_alpha
from services.etf_service import get_tech_etfs, get_complementary_etfs
from services.export_service import export_to_csv, create_pdf_report
from components.chart_components import (
    display_allocation_pie_chart,
    display_projection_chart,
    display_etf_performance_chart,
    display_alpha_chart
)
from components.summary_components import display_portfolio_summary, display_etf_list
import config

def show_dashboard_page():
    """Display the portfolio dashboard page"""
    # Redirect to setup if user is not set up
    if st.session_state.user_id is None:
        st.warning("Please set up your profile first")
        if st.button("Go to Setup"):
            st.session_state.page = PAGES["SETUP"]
            st.rerun()
        return
    
    # Get user data
    user = get_user_by_id(st.session_state.user_id)
    if not user:
        st.error("User not found. Please set up your profile again.")
        st.session_state.user_id = None
        st.session_state.page = PAGES["SETUP"]
        st.rerun()
        return
    
    st.header(f"{user.first_name}'s Portfolio Dashboard")
    
    # Portfolio adjustment section in sidebar
    with st.sidebar:
        st.subheader("Adjust Portfolio")
        
        with st.form("portfolio_adjustment_form"):
            # Investment adjustments
            st.markdown("### Investment Parameters")
            
            new_initial_investment = st.number_input(
                "Initial Investment (ZAR)",
                min_value=1000.0,
                value=float(user.initial_investment),
                step=1000.0
            )
            
            new_monthly_contribution = st.number_input(
                "Monthly Contribution (ZAR)",
                min_value=0.0,
                value=float(user.monthly_contribution),
                step=100.0
            )
            
            # Allocation adjustments
            st.markdown("### Allocation")
            
            new_tech_allocation = st.slider(
                "Tech ETF Allocation (%)",
                min_value=60,
                max_value=80,
                value=int(user.tech_allocation * 100),
                step=1
            )
            
            new_complementary_allocation = 100 - new_tech_allocation
            st.write(f"Complementary ETF Allocation: {new_complementary_allocation}%")
            
            # Duration and risk adjustments
            st.markdown("### Timeframe & Risk")
            
            new_investment_duration = st.slider(
                "Investment Duration (Years)",
                min_value=1,
                max_value=10,
                value=user.investment_duration,
                step=1
            )
            
            new_risk_tolerance = st.select_slider(
                "Risk Tolerance",
                options=RISK_LEVELS,
                value=user.risk_tolerance
            )
            
            # ETF selection adjustments
            st.markdown("### ETF Selection")
            
            # Tech ETFs
            tech_etfs = get_tech_etfs()
            tech_etf_options = [etf['symbol'] for etf in tech_etfs]
            user_tech_etfs = user.tech_etfs.split(',') if user.tech_etfs else []
            
            new_selected_tech_etfs = st.multiselect(
                "Tech ETFs",
                options=tech_etf_options,
                default=user_tech_etfs
            )
            
            # Complementary ETFs
            complementary_etfs = get_complementary_etfs()
            complementary_etf_options = [etf['symbol'] for etf in complementary_etfs]
            user_complementary_etfs = user.complementary_etfs.split(',') if user.complementary_etfs else []
            
            new_selected_complementary_etfs = st.multiselect(
                "Complementary ETFs",
                options=complementary_etf_options,
                default=user_complementary_etfs
            )
            
            # Update button
            update_submitted = st.form_submit_button("Update Portfolio")
            
            if update_submitted:
                if not new_selected_tech_etfs or not new_selected_complementary_etfs:
                    st.error("Please select at least one ETF from each category")
                else:
                    # Convert allocations to decimal
                    new_tech_allocation_decimal = new_tech_allocation / 100
                    new_complementary_allocation_decimal = new_complementary_allocation / 100
                    
                    # Update the user's portfolio
                    update_user_portfolio(
                        user_id=user.id,
                        initial_investment=new_initial_investment,
                        monthly_contribution=new_monthly_contribution,
                        tech_allocation=new_tech_allocation_decimal,
                        complementary_allocation=new_complementary_allocation_decimal,
                        investment_duration=new_investment_duration,
                        risk_tolerance=new_risk_tolerance,
                        tech_etfs=new_selected_tech_etfs,
                        complementary_etfs=new_selected_complementary_etfs
                    )
                    
                    st.success("Portfolio updated successfully!")
                    st.rerun()
        
        # Navigation button to setup page
        if st.button("Back to Setup"):
            st.session_state.page = PAGES["SETUP"]
            st.rerun()
    
    # Main dashboard content
    tab1, tab2, tab3 = st.tabs(["Portfolio Overview", "Projections", "ETF Analysis"])
    
    # Tab 1: Portfolio Overview
    with tab1:
        # Get portfolio data
        allocation_data = get_portfolio_allocation(user)
        current_value = get_portfolio_value(user)
        
        # Display summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Current Investment", f"R{user.initial_investment:,.2f}")
        with col2:
            st.metric("Monthly Contribution", f"R{user.monthly_contribution:,.2f}")
        with col3:
            st.metric("Investment Duration", f"{user.investment_duration} Years")
        with col4:
            st.metric("Risk Tolerance", user.risk_tolerance)
        
        # Display allocation charts
        st.subheader("Portfolio Allocation")
        col1, col2 = st.columns([2, 3])
        with col1:
            display_allocation_pie_chart(allocation_data)
        
        with col2:
            display_portfolio_summary(user, current_value)
        
        # ETF list
        st.subheader("Selected ETFs")
        display_etf_list(user)
    
    # Tab 2: Projections
    with tab2:
        projection_data = get_portfolio_projection(user)
        alpha_data = calculate_alpha(user)
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            final_value = projection_data["portfolio_value"].iloc[-1]
            initial_with_contributions = user.initial_investment + (user.monthly_contribution * 12 * user.investment_duration)
            total_profit = final_value - initial_with_contributions
            st.metric("Projected Final Value", f"R{final_value:,.2f}")
        with col2:
            st.metric("Total Profit", f"R{total_profit:,.2f}")
        with col3:
            cagr = ((final_value / user.initial_investment) ** (1 / user.investment_duration) - 1) * 100
            st.metric("Projected CAGR", f"{cagr:.2f}%")
        with col4:
            final_alpha = alpha_data["alpha_cumulative"].iloc[-1] * 100
            st.metric("Alpha vs S&P 500", f"{final_alpha:.2f}%", f"{final_alpha - config.ALPHA_TARGET * 100:.2f}%")
        
        # Projection chart
        st.subheader("Investment Growth Projection")
        display_projection_chart(projection_data)
        
        # Alpha chart
        st.subheader("Performance vs S&P 500")
        display_alpha_chart(alpha_data)
        
        # Export options
        st.subheader("Export Reports")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Export as CSV"):
                csv_data = export_to_csv(user, projection_data, alpha_data)
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name=f"{user.first_name}_{user.last_name}_portfolio.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("Generate PDF Report"):
                pdf_data = create_pdf_report(user, projection_data, alpha_data)
                st.download_button(
                    label="Download PDF",
                    data=pdf_data,
                    file_name=f"{user.first_name}_{user.last_name}_portfolio_report.pdf",
                    mime="application/pdf"
                )
    
    # Tab 3: ETF Analysis
    with tab3:
        st.subheader("ETF Performance Analysis")
        
        # Get user's ETFs
        user_tech_etfs = user.tech_etfs.split(',') if user.tech_etfs else []
        user_complementary_etfs = user.complementary_etfs.split(',') if user.complementary_etfs else []
        
        # ETF selection for chart
        selected_etfs_for_chart = st.multiselect(
            "Select ETFs to Compare",
            options=user_tech_etfs + user_complementary_etfs,
            default=user_tech_etfs[:2] + user_complementary_etfs[:1] if user_tech_etfs and user_complementary_etfs else []
        )
        
        if selected_etfs_for_chart:
            display_etf_performance_chart(selected_etfs_for_chart)
        else:
            st.info("Please select ETFs to compare their performance")
