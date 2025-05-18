import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from database.models import Base, User, ETF, PortfolioSnapshot, ETFSnapshot
from services.etf_service import get_tech_etfs, get_complementary_etfs, get_etf_return
import config
from datetime import datetime

# Create engine using PostgreSQL connection string
engine = create_engine(config.DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_database():
    """Initialize the database, creating tables if they don't exist"""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Populate ETF data if not already present
    populate_etf_data()

def get_db_session():
    """Get a database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

def populate_etf_data():
    """Populate the ETF table with data if it's empty"""
    db = get_db_session()
    
    # Check if ETF table is empty
    etf_count = db.query(ETF).count()
    if etf_count > 0:
        return
    
    # Add tech ETFs
    tech_etfs = get_tech_etfs()
    for etf_data in tech_etfs:
        etf = ETF(
            symbol=etf_data['symbol'],
            name=etf_data['name'],
            category='Tech ETFs',
            expense_ratio=etf_data['expense_ratio']
        )
        db.add(etf)
    
    # Add complementary ETFs
    complementary_etfs = get_complementary_etfs()
    for etf_data in complementary_etfs:
        etf = ETF(
            symbol=etf_data['symbol'],
            name=etf_data['name'],
            category='Complementary ETFs',
            sector=etf_data.get('sector', ''),
            expense_ratio=etf_data['expense_ratio']
        )
        db.add(etf)
    
    db.commit()

def create_user(first_name, last_name, initial_investment, monthly_contribution, 
                tech_allocation, complementary_allocation, investment_duration, 
                risk_tolerance, tech_etfs, complementary_etfs):
    """Create a new user with portfolio settings"""
    db = get_db_session()
    
    # Convert ETF lists to comma-separated strings for backward compatibility
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
    
    # Associate ETFs with user using the relationship tables
    # First get tech ETFs
    if tech_etfs:
        tech_etf_count = len(tech_etfs)
        individual_allocation = tech_allocation / tech_etf_count
        
        for symbol in tech_etfs:
            etf = db.query(ETF).filter(ETF.symbol == symbol).first()
            if etf:
                statement = user_tech_etfs.insert().values(
                    user_id=user.id, 
                    etf_id=etf.id, 
                    allocation_percentage=individual_allocation
                )
                db.execute(statement)
    
    # Then complementary ETFs
    if complementary_etfs:
        comp_etf_count = len(complementary_etfs)
        individual_allocation = complementary_allocation / comp_etf_count
        
        for symbol in complementary_etfs:
            etf = db.query(ETF).filter(ETF.symbol == symbol).first()
            if etf:
                statement = user_complementary_etfs.insert().values(
                    user_id=user.id, 
                    etf_id=etf.id, 
                    allocation_percentage=individual_allocation
                )
                db.execute(statement)
    
    db.commit()
    
    # Create initial portfolio snapshot
    create_portfolio_snapshot(user.id)
    
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
        # Convert ETF lists to comma-separated strings for backward compatibility
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
        
        # Remove old ETF associations
        # For tech ETFs
        from sqlalchemy import text
        db.execute(text(f"DELETE FROM user_tech_etfs WHERE user_id = {user.id}"))
        
        # For complementary ETFs
        db.execute(text(f"DELETE FROM user_complementary_etfs WHERE user_id = {user.id}"))
        
        # Add new ETF associations
        # First tech ETFs
        if tech_etfs:
            tech_etf_count = len(tech_etfs)
            individual_allocation = tech_allocation / tech_etf_count
            
            for symbol in tech_etfs:
                etf = db.query(ETF).filter(ETF.symbol == symbol).first()
                if etf:
                    statement = user_tech_etfs.insert().values(
                        user_id=user.id, 
                        etf_id=etf.id, 
                        allocation_percentage=individual_allocation
                    )
                    db.execute(statement)
        
        # Then complementary ETFs
        if complementary_etfs:
            comp_etf_count = len(complementary_etfs)
            individual_allocation = complementary_allocation / comp_etf_count
            
            for symbol in complementary_etfs:
                etf = db.query(ETF).filter(ETF.symbol == symbol).first()
                if etf:
                    statement = user_complementary_etfs.insert().values(
                        user_id=user.id, 
                        etf_id=etf.id, 
                        allocation_percentage=individual_allocation
                    )
                    db.execute(statement)
        
        db.commit()
        
        # Create new portfolio snapshot
        create_portfolio_snapshot(user.id)
        
        return True
    
    return False

def create_portfolio_snapshot(user_id):
    """Create a snapshot of the user's portfolio"""
    from services.portfolio_service import calculate_etf_allocations, get_portfolio_value
    from services.projection_service import calculate_alpha
    
    db = get_db_session()
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        return None
    
    # Get portfolio data
    portfolio_value = get_portfolio_value(user)
    alpha_data = calculate_alpha(user)
    etf_allocations = calculate_etf_allocations(user)
    
    # Create portfolio snapshot
    snapshot = PortfolioSnapshot(
        user_id=user.id,
        snapshot_date=datetime.now(),
        portfolio_value=portfolio_value,
        cumulative_return=0.0,  # This would be calculated based on historical data
        alpha_vs_sp500=alpha_data["alpha_cumulative"].iloc[-1] if not alpha_data.empty else 0.0
    )
    
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    
    # Create ETF snapshots
    for etf in etf_allocations:
        symbol = etf['symbol']
        returns = get_etf_return(symbol)
        
        etf_snapshot = ETFSnapshot(
            portfolio_snapshot_id=snapshot.id,
            etf_symbol=symbol,
            etf_name=etf.get('name', symbol),
            allocation_percentage=etf['allocation'],
            value=etf['value'],
            return_1y=returns['1y'],
            return_3y=returns['3y'],
            return_5y=returns['5y']
        )
        
        db.add(etf_snapshot)
    
    db.commit()
    
    return snapshot

def get_latest_portfolio_snapshot(user_id):
    """Get the latest portfolio snapshot for a user"""
    db = get_db_session()
    
    snapshot = db.query(PortfolioSnapshot)\
        .filter(PortfolioSnapshot.user_id == user_id)\
        .order_by(PortfolioSnapshot.snapshot_date.desc())\
        .first()
    
    return snapshot

def get_portfolio_snapshot_history(user_id, limit=10):
    """Get historical portfolio snapshots for a user"""
    db = get_db_session()
    
    snapshots = db.query(PortfolioSnapshot)\
        .filter(PortfolioSnapshot.user_id == user_id)\
        .order_by(PortfolioSnapshot.snapshot_date.desc())\
        .limit(limit)\
        .all()
    
    return snapshots

# Import these at the end to avoid circular imports
from database.models import user_tech_etfs, user_complementary_etfs
