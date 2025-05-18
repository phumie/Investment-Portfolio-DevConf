import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import random
from services.etf_service import get_etf_historical_data
import config

def display_allocation_pie_chart(allocation_data):
    """Display a pie chart of the portfolio allocation"""
    fig = px.pie(
        allocation_data, 
        names='category', 
        values='allocation',
        title='Portfolio Allocation by Category',
        color='category',
        color_discrete_map={
            'Tech ETFs': '#0068c9',
            'Complementary ETFs': '#83c9ff'
        }
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        legend_title_text='',
        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_etf_allocation_pie_chart(etf_allocation_data):
    """Display a pie chart of ETF allocation"""
    fig = px.pie(
        etf_allocation_data, 
        names='symbol', 
        values='allocation',
        title='ETF Allocation',
        hover_data=['name']
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        legend_title_text='',
        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_projection_chart(projection_data):
    """Display a line chart of projected portfolio growth"""
    fig = go.Figure()
    
    # Add portfolio value line
    fig.add_trace(go.Scatter(
        x=projection_data['year'],
        y=projection_data['portfolio_value'],
        mode='lines+markers',
        name='Portfolio Value',
        line=dict(color='#0068c9', width=3)
    ))
    
    # Add initial investment line
    fig.add_trace(go.Scatter(
        x=projection_data['year'],
        y=projection_data['initial_plus_contributions'],
        mode='lines',
        name='Investment + Contributions',
        line=dict(color='#83c9ff', width=2, dash='dash')
    ))
    
    # Add S&P benchmark line
    fig.add_trace(go.Scatter(
        x=projection_data['year'],
        y=projection_data['sp500_benchmark'],
        mode='lines',
        name='S&P 500 Benchmark',
        line=dict(color='#ff9e83', width=2)
    ))
    
    # Update layout
    fig.update_layout(
        title='Projected Portfolio Growth Over Time',
        xaxis_title='Year',
        yaxis_title='Value (ZAR)',
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        hovermode="x unified"
    )
    
    # Add custom hover info
    fig.update_traces(
        hovertemplate='Year: %{x}<br>Value: R%{y:,.2f}<br>'
    )
    
    # Format y-axis as currency
    fig.update_yaxes(tickprefix='R', tickformat=',.0f')
    
    st.plotly_chart(fig, use_container_width=True)

def display_etf_performance_chart(etf_symbols):
    """Display a line chart comparing ETF performance"""
    # Create an empty dataframe for the chart
    performance_data = pd.DataFrame()
    
    # Generate color map for ETFs
    colors = px.colors.qualitative.G10
    color_map = {etf: colors[i % len(colors)] for i, etf in enumerate(etf_symbols)}
    
    # Get historical data for each ETF
    for symbol in etf_symbols:
        data = get_etf_historical_data(symbol)
        if len(performance_data) == 0:
            performance_data = data[['date']].copy()
        
        performance_data[symbol] = data['value_normalized']
    
    # Create the figure
    fig = go.Figure()
    
    for symbol in etf_symbols:
        fig.add_trace(go.Scatter(
            x=performance_data['date'],
            y=performance_data[symbol],
            mode='lines',
            name=symbol,
            line=dict(color=color_map[symbol], width=2)
        ))
    
    # Update layout
    fig.update_layout(
        title='ETF Performance Comparison (Normalized)',
        xaxis_title='Date',
        yaxis_title='Normalized Value',
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        hovermode="x unified"
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_alpha_chart(alpha_data):
    """Display a chart showing alpha (outperformance vs S&P 500)"""
    fig = go.Figure()
    
    # Add alpha line
    fig.add_trace(go.Scatter(
        x=alpha_data['year'],
        y=alpha_data['alpha_cumulative'] * 100,  # Convert to percentage
        mode='lines+markers',
        name='Cumulative Alpha',
        line=dict(color='#0068c9', width=3)
    ))
    
    # Add target line
    target_alpha = [config.ALPHA_TARGET * 100 * (i + 1) for i in range(len(alpha_data))]
    fig.add_trace(go.Scatter(
        x=alpha_data['year'],
        y=target_alpha,
        mode='lines',
        name=f'Target ({config.ALPHA_TARGET * 100}% per year)',
        line=dict(color='#83c9ff', width=2, dash='dash')
    ))
    
    # Add zero line
    fig.add_trace(go.Scatter(
        x=alpha_data['year'],
        y=[0] * len(alpha_data),
        mode='lines',
        name='S&P 500 Benchmark',
        line=dict(color='#ff9e83', width=2)
    ))
    
    # Update layout
    fig.update_layout(
        title='Cumulative Alpha vs S&P 500',
        xaxis_title='Year',
        yaxis_title='Cumulative Alpha (%)',
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        hovermode="x unified"
    )
    
    # Format y-axis as percentage
    fig.update_yaxes(ticksuffix='%')
    
    st.plotly_chart(fig, use_container_width=True)
