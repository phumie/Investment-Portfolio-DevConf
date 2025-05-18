from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

# Association tables for many-to-many relationships
user_tech_etfs = Table(
    'user_tech_etfs',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('etf_id', Integer, ForeignKey('etfs.id'), primary_key=True),
    Column('allocation_percentage', Float, default=0.0)
)

user_complementary_etfs = Table(
    'user_complementary_etfs',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('etf_id', Integer, ForeignKey('etfs.id'), primary_key=True),
    Column('allocation_percentage', Float, default=0.0)
)

class ETF(Base):
    __tablename__ = 'etfs'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)  # Tech or Complementary
    sector = Column(String)  # For complementary ETFs
    expense_ratio = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    tech_portfolios = relationship("User", secondary=user_tech_etfs, back_populates="tech_etfs_relationship")
    complementary_portfolios = relationship("User", secondary=user_complementary_etfs, back_populates="complementary_etfs_relationship")
    
    def __repr__(self):
        return f"<ETF(id={self.id}, symbol='{self.symbol}', name='{self.name}', category='{self.category}')>"

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    initial_investment = Column(Float, nullable=False)
    monthly_contribution = Column(Float, default=0.0)
    tech_allocation = Column(Float, nullable=False)
    complementary_allocation = Column(Float, nullable=False)
    investment_duration = Column(Integer, nullable=False)
    risk_tolerance = Column(String, nullable=False)
    
    # For backward compatibility - will be deprecated
    tech_etfs = Column(String)  # Comma-separated list of tech ETFs
    complementary_etfs = Column(String)  # Comma-separated list of complementary ETFs
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    tech_etfs_relationship = relationship("ETF", secondary=user_tech_etfs, back_populates="tech_portfolios")
    complementary_etfs_relationship = relationship("ETF", secondary=user_complementary_etfs, back_populates="complementary_portfolios")
    portfolio_snapshots = relationship("PortfolioSnapshot", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, first_name='{self.first_name}', last_name='{self.last_name}')>"

class PortfolioSnapshot(Base):
    __tablename__ = 'portfolio_snapshots'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    snapshot_date = Column(DateTime, default=func.now())
    portfolio_value = Column(Float, nullable=False)
    cumulative_return = Column(Float, default=0.0)  # As a decimal
    alpha_vs_sp500 = Column(Float, default=0.0)  # Alpha as a decimal
    
    # Relationships
    user = relationship("User", back_populates="portfolio_snapshots")
    etf_snapshots = relationship("ETFSnapshot", back_populates="portfolio_snapshot", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PortfolioSnapshot(id={self.id}, user_id={self.user_id}, date='{self.snapshot_date}', value={self.portfolio_value})>"

class ETFSnapshot(Base):
    __tablename__ = 'etf_snapshots'
    
    id = Column(Integer, primary_key=True)
    portfolio_snapshot_id = Column(Integer, ForeignKey('portfolio_snapshots.id'), nullable=False)
    etf_symbol = Column(String, nullable=False)
    etf_name = Column(String, nullable=False)
    allocation_percentage = Column(Float, nullable=False)
    value = Column(Float, nullable=False)
    return_1y = Column(Float)
    return_3y = Column(Float)
    return_5y = Column(Float)
    
    # Relationships
    portfolio_snapshot = relationship("PortfolioSnapshot", back_populates="etf_snapshots")
    
    def __repr__(self):
        return f"<ETFSnapshot(id={self.id}, etf_symbol='{self.etf_symbol}', allocation={self.allocation_percentage}, value={self.value})>"
