
# Tech-Focused Investment Portfolio Manager

A Streamlit-based web application for managing and analyzing tech-focused investment portfolios with complementary ETF allocations. Built with [Replit](https://replit.com), a powerful browser-based IDE and cloud development platform that makes it easy to code, collaborate, and deploy applications directly from your browser.

## Features

- Portfolio setup with customizable allocations between tech and complementary ETFs
- Real-time portfolio analysis and visualization
- Investment projections and performance tracking
- Automated PDF and CSV report generation
- Performance comparison with S&P 500 benchmark
- Historical portfolio tracking

## How It Works

The application uses:
- Streamlit for the web interface
- SQLite for data storage
- ReportLab for PDF generation
- Plotly for interactive charts
- Python for backend calculations and ETF data management

The portfolio follows a mandate of:
- 60-80% allocation to Tech ETFs
- 20-40% allocation to Complementary ETFs
- Risk-adjusted returns based on user's risk tolerance

## Setup Instructions

### For Unix/Linux Systems

1. Install Python dependencies:
```bash
python3 -m pip install streamlit pandas plotly reportlab sqlalchemy
```

2. Clone the project and navigate to the directory:
```bash
cd investment-portfolio-devconf
```

3. Initialize the database:
```bash
python3 main.py
```

4. Run the application:
```bash
streamlit run main.py --server.port 5000
```

The application will be available at `http://0.0.0.0:5000`

### For Windows

1. Install Python from python.org if not already installed

2. Open Command Prompt as Administrator and install dependencies:
```cmd
pip install streamlit pandas plotly reportlab sqlalchemy
```

3. Navigate to the project directory:
```cmd
cd investment-portfolio-devconf
```

4. Initialize the database:
```cmd
python main.py
```

5. Run the application:
```cmd
streamlit run main.py --server.port 5000
```

The application will be available at `http://0.0.0.0:5000`

## Project Structure

```
├── components/          # UI components
├── data/               # ETF data and database
├── database/           # Database models and services
├── services/           # Business logic
├── utils/              # Helper functions
└── main.py            # Application entry point
```

## Features

1. **Portfolio Setup**
   - User information collection
   - Investment amount specification
   - ETF selection
   - Risk tolerance setting

2. **Dashboard**
   - Portfolio overview
   - Asset allocation visualization
   - Performance metrics
   - ETF analysis

3. **Reporting**
   - PDF report generation
   - CSV data export
   - Performance vs S&P 500 tracking

4. **Portfolio Management**
   - Real-time updates
   - Historical tracking
   - Rebalancing capabilities

## About Replit

Replit is a modern development environment that runs in your browser, combining the functionality of an IDE with cloud hosting capabilities. It eliminates the need for local setup and makes development and deployment seamless by providing everything you need in one place.
