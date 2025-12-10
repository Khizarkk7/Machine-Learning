"""
Main FastAPI application for Real Estate Property Listing System
Roll No: SE231009
Name: Khuzaima Saqib
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
import uvicorn

# Import modules
from database import engine, get_db, Base, SessionLocal
from models import User, Property
from schemas import (
    UserCreate, UserResponse, Token, 
    PropertyCreate, PropertyUpdate, PropertyResponse
)
from auth import (
    get_password_hash, verify_password, 
    create_access_token, get_current_user, 
    get_current_active_user, ACCESS_TOKEN_EXPIRE_MINUTES
)
from datetime import timedelta

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Real Estate Property Listing System",
    description="API for managing real estate properties with JWT authentication",
    version="1.0.0"
)

# ========== AUTHENTICATION ENDPOINTS ==========
@app.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    
    - **username**: Unique username (alphanumeric)
    - **email**: Valid email address
    - **password**: Minimum 6 characters
    - **full_name**: Optional full name
    """
    # Check if username already exists
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    db_email = db.query(User).filter(User.email == user.email).first()
    if db_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        role="user"  # Default role
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@app.post("/auth/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login and get access token
    
    - **username**: Your username
    - **password**: Your password
    """
    # Find user
    user = db.query(User).filter(User.username == form_data.username).first()
    
    # Verify user exists and password is correct
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/profile", response_model=UserResponse)
def get_user_profile(current_user: User = Depends(get_current_active_user)):
    """
    Get current user profile (protected route)
    """
    return current_user

#  PROPERTY CRUD ENDPOINTS 
@app.post("/api/properties/", response_model=PropertyResponse, status_code=status.HTTP_201_CREATED)
def create_property(
    property_data: PropertyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new property (authenticated users only)
    
    - **property_title**: Title of the property
    - **property_type**: Type (House, Apartment, Villa, etc.)
    - **location**: Property location
    - **price**: Must be greater than 0
    - **area_sqft**: Optional area in square feet
    - **bedrooms**: Optional number of bedrooms
    - **status**: Property status (default: Available)
    """
    # Create property with current user as owner
    db_property = Property(
        **property_data.dict(),
        owner_id=current_user.id
    )
    
    db.add(db_property)
    db.commit()
    db.refresh(db_property)
    
    return db_property

@app.get("/api/properties/", response_model=List[PropertyResponse])
def get_properties(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all properties with pagination
    
    - Regular users: Only see their own properties
    - Admin users: See all properties
    """
    if current_user.role == "admin":
        properties = db.query(Property).offset(skip).limit(limit).all()
    else:
        properties = db.query(Property).filter(
            Property.owner_id == current_user.id
        ).offset(skip).limit(limit).all()
    
    return properties

@app.get("/api/properties/{property_id}", response_model=PropertyResponse)
def get_property(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific property by ID
    
    - Regular users: Can only access their own properties
    - Admin users: Can access any property
    """
    property = db.query(Property).filter(Property.id == property_id).first()
    
    if not property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    # Check auth
    if current_user.role != "admin" and property.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this property"
        )
    
    return property

@app.patch("/api/properties/{property_id}", response_model=PropertyResponse)
def update_property(
    property_id: int,
    property_update: PropertyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a property (partial update)
    
    - Regular users: Can only update their own properties
    - Admin users: Can update any property
    """
    property = db.query(Property).filter(Property.id == property_id).first()
    
    if not property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    # Check authorization
    if current_user.role != "admin" and property.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this property"
        )
    
    # Update only provided fields
    update_data = property_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(property, field, value)
    
    db.commit()
    db.refresh(property)
    
    return property

@app.delete("/api/properties/{property_id}")
def delete_property(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a property
    
    - Regular users: Can only delete their own properties
    - Admin users: Can delete any property
    """
    property = db.query(Property).filter(Property.id == property_id).first()
    
    if not property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    
    # Check authorization
    if current_user.role != "admin" and property.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this property"
        )
    
    db.delete(property)
    db.commit()
    
    return {"message": "Property deleted successfully"}

# ========== ROOT ENDPOINT ==========
@app.get("/")
def root():
    """
    Root endpoint with API information
    """
    return {
        "message": "Real Estate Property Listing System API",
        "developer": "Khuzaima Saqib",
        "roll_no": "SE231009",
        "endpoints": {
            "POST /auth/register": "Register new user",
            "POST /auth/token": "Login and get JWT token",
            "GET /auth/profile": "Get current user profile",
            "POST /api/properties/": "Create new property",
            "GET /api/properties/": "Get all properties",
            "GET /api/properties/{id}": "Get specific property",
            "PATCH /api/properties/{id}": "Update property",
            "DELETE /api/properties/{id}": "Delete property"
        },
        "documentation": "/docs"
    }

# ========== CREATE DEFAULT USERS ==========
@app.on_event("startup")
def create_default_users():
    """
    Create default admin and user accounts on startup
    """
    db = SessionLocal()
    
    try:
        # Create admin user (if not exists)
        admin_username = "admin_1009"  # Last 4 digits of SE231009
        admin_user = db.query(User).filter(User.username == admin_username).first()
        
        if not admin_user:
            admin_user = User(
                username=admin_username,
                email="admin_1009@estate.com",
                hashed_password=get_password_hash("admin123"),
                full_name="System Administrator",
                role="admin"
            )
            db.add(admin_user)
            print(f"✅ Created admin user: {admin_username}")
        
        # Create regular user (if not exists)
        user_username = "user_1009"  # Last 4 digits of SE231009
        regular_user = db.query(User).filter(User.username == user_username).first()
        
        if not regular_user:
            regular_user = User(
                username=user_username,
                email="user_1009@estate.com",
                hashed_password=get_password_hash("user123"),
                full_name="Regular User",
                role="user"
            )
            db.add(regular_user)
            print(f"✅ Created regular user: {user_username}")
        
        db.commit()
        
        # Create sample properties
        properties_count = db.query(Property).count()
        if properties_count == 0:
            # Admin properties
            admin_property1 = Property(
                property_title="Luxury Villa in Islamabad",
                property_type="Villa",
                location="Islamabad, Sector F-7",
                price=45000000,
                area_sqft=5500,
                bedrooms=5,
                status="Available",
                owner_id=admin_user.id if admin_user.id else 1
            )
            
            admin_property2 = Property(
                property_title="Commercial Plaza in Lahore",
                property_type="Commercial",
                location="Lahore, Gulberg",
                price=85000000,
                area_sqft=12000,
                bedrooms=0,
                status="Available",
                owner_id=admin_user.id if admin_user.id else 1
            )
            
            db.add_all([admin_property1, admin_property2])
            
            # Regular user properties
            if regular_user.id:
                user_property1 = Property(
                    property_title="3-Bed Apartment Karachi",
                    property_type="Apartment",
                    location="Karachi, Clifton",
                    price=25000000,
                    area_sqft=1800,
                    bedrooms=3,
                    status="Sold",
                    owner_id=regular_user.id
                )
                
                user_property2 = Property(
                    property_title="Plot in Bahria Town",
                    property_type="Plot",
                    location="Rawalpindi, Bahria Town",
                    price=8500000,
                    area_sqft=1000,
                    bedrooms=0,
                    status="Available",
                    owner_id=regular_user.id
                )
                
                db.add_all([user_property1, user_property2])
            
            db.commit()
            print("✅ Created 4 sample properties")
        
    except Exception as e:
        print(f"⚠️  Error creating default users: {e}")
        db.rollback()
    finally:
        db.close()

# RUN APPLICATION 
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)