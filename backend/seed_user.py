
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from database import SessionLocal, init_db
from models.user import User
import bcrypt

def get_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def seed_test_user():
    init_db()
    db = SessionLocal()
    try:
        # Clean up existing test data to avoid IntegrityError
        print("[SEED] Cleaning up existing test users...")
        db.query(User).filter((User.email == "test@example.com") | (User.phone == "9999999999")).delete()
        db.commit()

        print("[SEED] Creating fresh test user...")
        new_user = User(
            name="Test Farmer",
            email="test@example.com",
            phone="9999999999",
            location="Andhra Pradesh",
            language="te",
            hashed_password=get_password_hash("password123")
        )
        db.add(new_user)
        db.commit()
        print("[OK] Test user created: test@example.com / password123")
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Could not seed user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_test_user()
