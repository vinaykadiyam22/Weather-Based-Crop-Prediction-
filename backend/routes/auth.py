from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from database import get_db
from models.user import User
from services.otp_service import otp_service
from datetime import datetime
from passlib.context import CryptContext

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

from passlib.context import CryptContext
import bcrypt

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Request/Response Models
class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    phone: str
    location: str
    password: str
    language: str = "en"

class LoginRequest(BaseModel):
    identifier: str  # email or phone
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    location: str
    language: str
    
    class Config:
        from_attributes = True

@router.post("/register", response_model=UserResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == request.email) | (User.phone == request.phone)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or phone already exists"
        )
    
    # Create new user
    user = User(
        name=request.name,
        email=request.email,
        phone=request.phone,
        location=request.location,
        language=request.language,
        hashed_password=get_password_hash(request.password)
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

@router.post("/login", response_model=UserResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login with email/phone and password"""
    # Find user by email or phone
    user = db.query(User).filter(
        (User.email == request.identifier) | (User.phone == request.identifier)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Please contact admin."
        )
        
    if not user.hashed_password or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/phone or password"
        )
        
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    return user

@router.put("/user/{user_id}", response_model=UserResponse)
def update_user(user_id: int, language: str = None, location: str = None, db: Session = Depends(get_db)):
    """Update user settings"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if language:
        user.language = language
    if location:
        user.location = location
    
    db.commit()
    db.refresh(user)
    
    return user

@router.get("/user/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user details"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user
