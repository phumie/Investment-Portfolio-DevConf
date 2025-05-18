from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

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
    tech_etfs = Column(String)  # Comma-separated list of tech ETFs
    complementary_etfs = Column(String)  # Comma-separated list of complementary ETFs
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<User(id={self.id}, first_name='{self.first_name}', last_name='{self.last_name}')>"
