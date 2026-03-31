"""
Admin Routes
- Admin login (username: admin, password: admin — configurable)
- User management: list, toggle active, delete, update
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models.user import User
from datetime import datetime
import bcrypt
import os

router = APIRouter(prefix="/api/admin", tags=["Admin"])

# ─── Admin credentials (env overridable) ─────────────────────────────────────
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")
ADMIN_TOKEN = "admin-secret-token-crop-system"   # simple token for demo

# ─── Schemas ──────────────────────────────────────────────────────────────────
class AdminLoginRequest(BaseModel):
    username: str
    password: str

class UserUpdateRequest(BaseModel):
    name: str | None = None
    email: str | None = None
    location: str | None = None
    is_active: bool | None = None

# ─── Auth helper ──────────────────────────────────────────────────────────────
def require_admin(x_admin_token: str = Header(default=None)):
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Admin access required")

# ─── Routes ───────────────────────────────────────────────────────────────────

@router.post("/login")
def admin_login(req: AdminLoginRequest):
    if req.username != ADMIN_USERNAME or req.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    return {
        "success": True,
        "token": ADMIN_TOKEN,
        "username": ADMIN_USERNAME,
        "message": "Admin login successful",
    }


@router.get("/users", dependencies=[Depends(require_admin)])
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "phone": u.phone,
            "location": u.location,
            "language": u.language,
            "farm_size": u.farm_size,
            "farming_experience": u.farming_experience,
            "is_active": u.is_active if u.is_active is not None else True,
            "is_admin": u.is_admin if u.is_admin is not None else False,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "last_login": u.last_login.isoformat() if u.last_login else None,
        }
        for u in users
    ]


@router.get("/users/stats", dependencies=[Depends(require_admin)])
def user_stats(db: Session = Depends(get_db)):
    total = db.query(User).count()
    active = db.query(User).filter(User.is_active == True).count()  # noqa
    today = datetime.utcnow().date()
    new_today = db.query(User).filter(
        User.created_at >= datetime(today.year, today.month, today.day)
    ).count()
    return {"total": total, "active": active, "inactive": total - active, "new_today": new_today}


@router.patch("/users/{user_id}", dependencies=[Depends(require_admin)])
def update_user(user_id: int, req: UserUpdateRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if req.name is not None:
        user.name = req.name
    if req.email is not None:
        user.email = req.email
    if req.location is not None:
        user.location = req.location
    if req.is_active is not None:
        user.is_active = req.is_active
    db.commit()
    db.refresh(user)
    return {"success": True, "message": "User updated", "user_id": user_id}


@router.delete("/users/{user_id}", dependencies=[Depends(require_admin)])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"success": True, "message": f"User {user_id} deleted"}


@router.post("/users/{user_id}/toggle-active", dependencies=[Depends(require_admin)])
def toggle_user_active(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = not (user.is_active if user.is_active is not None else True)
    db.commit()
    return {"success": True, "is_active": user.is_active, "user_id": user_id}
