from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from database import get_db
from models.user import User
from services.otp_service import otp_service
from datetime import datetime

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# Request/Response Models
class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    phone: str
    location: str
    language: str = "en"

class LoginRequest(BaseModel):
    identifier: str  # email or phone
    method: str  # "email" or "sms"

class VerifyOTPRequest(BaseModel):
    identifier: str  # email or phone
    otp: str
    method: str

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
        language=request.language
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

@router.post("/login/request-otp")
def request_otp(request: LoginRequest, db: Session = Depends(get_db)):
    """Request OTP for login"""
    # Find user
    if request.method == "email":
        user = db.query(User).filter(User.email == request.identifier).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        result = otp_service.send_email_otp(user.email, user.name)
    elif request.method == "sms":
        user = db.query(User).filter(User.phone == request.identifier).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        result = otp_service.send_sms_otp(user.phone)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid method. Use 'email' or 'sms'"
        )
    
    response = {
        "message": "OTP sent successfully",
        "method": request.method,
        "result": result
    }
    # In mock mode, include OTP in response so user can see it on login page (dev only)
    if result.get("status") == "mock" and result.get("message"):
        if "OTP:" in result.get("message", ""):
            import re
            match = re.search(r"OTP:\s*(\d+)", result["message"])
            if match:
                response["otp"] = match.group(1)
        if result.get("plain_content"):
            import re
            match = re.search(r"OTP is:\s*(\d+)", result.get("plain_content", ""))
            if match:
                response["otp"] = match.group(1)
    return response

@router.post("/login/verify-otp", response_model=UserResponse)
def verify_otp(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    """Verify OTP and login"""
    # Verify OTP
    if request.method == "email":
        is_valid = otp_service.verify_email_otp(request.identifier, request.otp)
        user = db.query(User).filter(User.email == request.identifier).first()
    elif request.method == "sms":
        is_valid = otp_service.verify_phone_otp(request.identifier, request.otp)
        user = db.query(User).filter(User.phone == request.identifier).first()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid method"
        )
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired OTP"
        )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
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
