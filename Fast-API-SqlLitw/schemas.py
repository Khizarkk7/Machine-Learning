"""
Pydantic schemas for data validation and serialization
"""
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from datetime import datetime

# ========== USER SCHEMAS ==========
class UserCreate(BaseModel):
    """Schema for creating a new user"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = Field(None, max_length=100)
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.replace('_', '').isalnum():
            raise ValueError('Username must be alphanumeric')
        return v

class UserResponse(BaseModel):
    """Schema for user responses"""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# ========== TOKEN SCHEMAS ==========
class Token(BaseModel):
    """Schema for authentication token response"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Schema for token data"""
    username: Optional[str] = None

# ========== PROPERTY SCHEMAS ==========
class PropertyCreate(BaseModel):
    """Schema for creating a property"""
    property_title: str = Field(..., min_length=1, max_length=200)
    property_type: str = Field(..., max_length=50)
    location: str = Field(..., max_length=200)
    price: float = Field(..., gt=0, description="Price must be greater than 0")
    area_sqft: Optional[float] = Field(None, gt=0)
    bedrooms: Optional[int] = Field(None, ge=0)
    status: Optional[str] = Field("Available", max_length=20)
    
    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be greater than 0')
        return v

class PropertyUpdate(BaseModel):
    """Schema for updating a property (partial update)"""
    property_title: Optional[str] = Field(None, min_length=1, max_length=200)
    property_type: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=200)
    price: Optional[float] = Field(None, gt=0)
    area_sqft: Optional[float] = Field(None, gt=0)
    bedrooms: Optional[int] = Field(None, ge=0)
    status: Optional[str] = Field(None, max_length=20)

class PropertyResponse(BaseModel):
    """Schema for property responses"""
    id: int
    property_title: str
    property_type: str
    location: str
    price: float
    area_sqft: Optional[float]
    bedrooms: Optional[int]
    status: str
    owner_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True