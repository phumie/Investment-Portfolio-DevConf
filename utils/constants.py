# Page constants
PAGES = {
    "SETUP": "setup",
    "DASHBOARD": "dashboard"
}

# Risk levels
RISK_LEVELS = ["Low", "Medium", "High"]

# Annual returns for different risk levels
RISK_RETURNS = {
    "Low": {
        "tech": 0.08,
        "complementary": 0.05,
        "sp500": 0.06
    },
    "Medium": {
        "tech": 0.12,
        "complementary": 0.07,
        "sp500": 0.08
    },
    "High": {
        "tech": 0.15,
        "complementary": 0.09,
        "sp500": 0.10
    }
}

# Volatility for different risk levels
RISK_VOLATILITY = {
    "Low": {
        "tech": 0.15,
        "complementary": 0.10,
        "sp500": 0.12
    },
    "Medium": {
        "tech": 0.20,
        "complementary": 0.15,
        "sp500": 0.16
    },
    "High": {
        "tech": 0.25,
        "complementary": 0.18,
        "sp500": 0.20
    }
}

# S&P 500 sector weights (for complementary ETF allocation)
SP500_SECTOR_WEIGHTS = {
    "Energy": 0.05,
    "Materials": 0.03,
    "Industrials": 0.08,
    "Consumer Discretionary": 0.10,
    "Consumer Staples": 0.07,
    "Healthcare": 0.15,
    "Financials": 0.13,
    "Real Estate": 0.03,
    "Communication Services": 0.08,
    "Utilities": 0.03
}
