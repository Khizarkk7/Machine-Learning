"""
Database models for Real Estate Property Listing System
"""
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    """
    User model for authentication and authorization
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(String(20), default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship with properties
    properties = relationship("Property", back_populates="owner")

class Property(Base):
    """
    Real Estate Property model
    """
    __tablename__ = "properties"
    
    id = Column(Integer, primary_key=True, index=True)
    property_title = Column(String(200), nullable=False)
    property_type = Column(String(50))  # e.g., House, Apartment, Villa, etc.
    location = Column(String(200), nullable=False)
    price = Column(Float, nullable=False)
    area_sqft = Column(Float)
    bedrooms = Column(Integer)
    status = Column(String(20), default="Available")  # Available, Sold, Rented
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship with owner
    owner = relationship("User", back_populates="properties")   