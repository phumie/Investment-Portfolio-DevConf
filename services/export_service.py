import pandas as pd
import io
import base64
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from services.portfolio_service import calculate_etf_allocations, get_weighted_portfolio_return
from utils.helpers import format_currency, format_percentage

def export_to_csv(user, projection_data, alpha_data):
    """Export portfolio data to CSV"""
    # Create a buffer for the CSV data
    buffer = io.StringIO()
    
    # User info section
    user_info = pd.DataFrame({
        'Metric': ['Name', 'Initial Investment', 'Monthly Contribution', 'Tech Allocation', 'Complementary Allocation', 'Investment Duration', 'Risk Tolerance'],
        'Value': [f"{user.first_name} {user.last_name}", user.initial_investment, user.monthly_contribution, 
                  user.tech_allocation, user.complementary_allocation, user.investment_duration, user.risk_tolerance]
    })
    
    # ETF allocations
    etf_allocations = calculate_etf_allocations(user)
    etf_df = pd.DataFrame([
        {
            'Symbol': etf['symbol'],
            'Category': etf['category'],
            'Allocation': etf['allocation'],
            'Value': etf['value']
        } for etf in etf_allocations
    ])
    
    # Weighted returns
    returns = get_weighted_portfolio_return(user)
    returns_df = pd.DataFrame({
        'Period': ['1 Year', '3 Years', '5 Years'],
        'Return': [returns['1y'], returns['3y'], returns['5y']]
    })
    
    # Write data to buffer
    buffer.write("# USER INFORMATION\n")
    user_info.to_csv(buffer, index=False)
    
    buffer.write("\n\n# ETF ALLOCATIONS\n")
    etf_df.to_csv(buffer, index=False)
    
    buffer.write("\n\n# PORTFOLIO RETURNS\n")
    returns_df.to_csv(buffer, index=False)
    
    buffer.write("\n\n# PROJECTION DATA\n")
    projection_data.to_csv(buffer, index=False)
    
    buffer.write("\n\n# ALPHA DATA\n")
    alpha_data.to_csv(buffer, index=False)
    
    # Get the CSV data
    buffer.seek(0)
    return buffer.getvalue()

def create_pdf_report(user, projection_data, alpha_data):
    """Create a PDF report of the portfolio"""
    # Create a buffer for the PDF
    buffer = io.BytesIO()
    
    # Create the PDF document
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    heading_style = styles["Heading1"]
    subheading_style = styles["Heading2"]
    normal_style = styles["Normal"]
    
    # Create content elements
    elements = []
    
    # Title
    elements.append(Paragraph("Portfolio Investment Report", title_style))
    elements.append(Spacer(1, 12))
    
    # Date
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d')}", normal_style))
    elements.append(Spacer(1, 24))
    
    # User Information
    elements.append(Paragraph("User Information", heading_style))
    elements.append(Spacer(1, 12))
    
    user_info = [
        ["Name:", f"{user.first_name} {user.last_name}"],
        ["Initial Investment:", format_currency(user.initial_investment)],
        ["Monthly Contribution:", format_currency(user.monthly_contribution)],
        ["Tech Allocation:", format_percentage(user.tech_allocation)],
        ["Complementary Allocation:", format_percentage(user.complementary_allocation)],
        ["Investment Duration:", f"{user.investment_duration} Years"],
        ["Risk Tolerance:", user.risk_tolerance]
    ]
    
    user_table = Table(user_info, colWidths=[150, 300])
    user_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    
    elements.append(user_table)
    elements.append(Spacer(1, 24))
    
    # ETF Allocations
    elements.append(Paragraph("ETF Allocations", heading_style))
    elements.append(Spacer(1, 12))
    
    etf_allocations = calculate_etf_allocations(user)
    
    if etf_allocations:
        etf_data = [["Symbol", "Category", "Allocation", "Value"]]
        for etf in etf_allocations:
            etf_data.append([
                etf['symbol'],
                etf['category'],
                format_percentage(etf['allocation']),
                format_currency(etf['value'])
            ])
        
        etf_table = Table(etf_data, colWidths=[75, 150, 100, 125])
        etf_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (0, 1), (1, -1), 'LEFT'),
            ('ALIGN', (2, 1), (3, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))
        
        elements.append(etf_table)
    else:
        elements.append(Paragraph("No ETFs selected.", normal_style))
    
    elements.append(Spacer(1, 24))
    
    # Projection Data
    elements.append(Paragraph("Portfolio Projection", heading_style))
    elements.append(Spacer(1, 12))
    
    projection_data_table = [["Year", "Portfolio Value", "S&P 500 Benchmark", "Contributions"]]
    for _, row in projection_data.iterrows():
        projection_data_table.append([
            str(int(row['year'])),
            format_currency(row['portfolio_value']),
            format_currency(row['sp500_benchmark']),
            format_currency(row['initial_plus_contributions'])
        ])
    
    proj_table = Table(projection_data_table, colWidths=[50, 125, 175, 100])
    proj_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    
    elements.append(proj_table)
    elements.append(Spacer(1, 24))
    
    # Alpha Data
    elements.append(Paragraph("Performance vs S&P 500", heading_style))
    elements.append(Spacer(1, 12))
    
    alpha_data_table = [["Year", "Yearly Alpha", "Cumulative Alpha"]]
    for _, row in alpha_data.iterrows():
        alpha_data_table.append([
            str(int(row['year'])),
            format_percentage(row['alpha_yearly']),
            format_percentage(row['alpha_cumulative'])
        ])
    
    alpha_table = Table(alpha_data_table, colWidths=[150, 150, 150])
    alpha_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    
    elements.append(alpha_table)
    elements.append(Spacer(1, 24))
    
    # Disclaimer
    elements.append(Paragraph("Disclaimer", heading_style))
    elements.append(Spacer(1, 12))
    
    disclaimer_text = """
    This report is based on projections using historical data and assumptions. Actual results may vary.
    Past performance is not indicative of future results. Investment decisions should be made based on
    your own research and consultation with a financial advisor.
    """
    elements.append(Paragraph(disclaimer_text, normal_style))
    
    # Build the PDF
    doc.build(elements)
    
    # Get the PDF
    buffer.seek(0)
    return buffer.getvalue()
