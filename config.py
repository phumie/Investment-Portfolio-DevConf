import os
from sqlalchemy.engine.url import URL

# Environment configuration
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")

# Database configuration - prefer PostgreSQL in Replit
DATABASE_URL = os.getenv("DATABASE_URL")

# If DATABASE_URL is not available, construct it from individual components or use SQLite
if not DATABASE_URL:
    DB_DIALECT = os.getenv("DB_DIALECT", "sqlite")
    
    # For SQLite (fallback)
    SQLITE_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "portfolio.db")
    
    # For PostgreSQL
    PG_HOST = os.getenv("PGHOST", "localhost")
    PG_PORT = int(os.getenv("PGPORT", "5432"))  # Convert to int
    PG_USER = os.getenv("PGUSER", "postgres")
    PG_PASSWORD = os.getenv("PGPASSWORD", "")
    PG_DATABASE = os.getenv("PGDATABASE", "portfolio")
    
    # Construct the database URL based on the dialect
    if DB_DIALECT == "sqlite":
        DATABASE_URL = f"sqlite:///{SQLITE_DB_PATH}"
    elif DB_DIALECT == "postgresql":
        DATABASE_URL = URL.create(
            drivername="postgresql",
            username=PG_USER,
            password=PG_PASSWORD,
            host=PG_HOST,
            port=PG_PORT,
            database=PG_DATABASE,
            query={
                'sslmode': 'require',
                'connect_timeout': '30',
                'keepalives': '1',
                'keepalives_idle': '30',
                'keepalives_interval': '10',
                'keepalives_count': '5'
            }
        )
    else:
        # Default to SQLite if the dialect is not recognized
        DATABASE_URL = f"sqlite:///{SQLITE_DB_PATH}"

# Application settings
APP_TITLE = "Tech-Forward Investment Portfolio Manager"
APP_DESCRIPTION = "Manage and visualize your tech-focused investment portfolio based on the mandate."

# Portfolio settings
DEFAULT_TECH_ALLOCATION = 0.7  # 70% in Tech ETFs
DEFAULT_COMPLEMENTARY_ALLOCATION = 0.3  # 30% in Complementary Sector ETFs
DEFAULT_INVESTMENT_HORIZON = 5  # 5-year horizon
ALPHA_TARGET = 0.01  # 1% annual outperformance
