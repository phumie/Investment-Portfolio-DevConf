import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from database.models import Base, User
import config

# Create engine
engine = create_engine(config.DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_database():
    """Initialize the database, creating tables if they don't exist"""
    # Create data directory if it doesn't exist (for SQLite)
    if config.DB_DIALECT == "sqlite":
        os.makedirs(os.path.dirname(config.SQLITE_DB_PATH), exist_ok=True)
    
    # Create tables
    Base.metadata.create_all(bind=engine)

def get_db_session():
    """Get a database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

def create_user(first_name, last_name, initial_investment, monthly_contribution, 
                tech_allocation, complementary_allocation, investment_duration, 
                risk_tolerance, tech_etfs, complementary_etfs):
    """Create a new user with portfolio settings"""
    db = get_db_session()
    
    # Convert ETF lists to comma-separated strings
    tech_etfs_str = ','.join(tech_etfs) if tech_etfs else ''
    complementary_etfs_str = ','.join(complementary_etfs) if complementary_etfs else ''
    
    user = User(
        first_name=first_name,
        last_name=last_name,
        initial_investment=initial_investment,
        monthly_contribution=monthly_contribution,
        tech_allocation=tech_allocation,
        complementary_allocation=complementary_allocation,
        investment_duration=investment_duration,
        risk_tolerance=risk_tolerance,
        tech_etfs=tech_etfs_str,
        complementary_etfs=complementary_etfs_str
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user.id

def get_user_by_id(user_id):
    """Get a user by ID"""
    db = get_db_session()
    return db.query(User).filter(User.id == user_id).first()

def update_user_portfolio(user_id, initial_investment, monthly_contribution, 
                          tech_allocation, complementary_allocation, investment_duration, 
                          risk_tolerance, tech_etfs, complementary_etfs):
    """Update a user's portfolio settings"""
    db = get_db_session()
    user = db.query(User).filter(User.id == user_id).first()
    
    if user:
        # Convert ETF lists to comma-separated strings
        tech_etfs_str = ','.join(tech_etfs) if tech_etfs else ''
        complementary_etfs_str = ','.join(complementary_etfs) if complementary_etfs else ''
        
        user.initial_investment = initial_investment
        user.monthly_contribution = monthly_contribution
        user.tech_allocation = tech_allocation
        user.complementary_allocation = complementary_allocation
        user.investment_duration = investment_duration
        user.risk_tolerance = risk_tolerance
        user.tech_etfs = tech_etfs_str
        user.complementary_etfs = complementary_etfs_str
        
        db.commit()
        db.refresh(user)
        
        return True
    
    return False
