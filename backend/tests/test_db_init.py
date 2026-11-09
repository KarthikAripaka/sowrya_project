import sys
import os
sys.path.insert(0, os.path.abspath("."))

from backend.app.database.session import engine, Base, SessionLocal
from backend.app.models.models import User
from backend.app.core.security import get_password_hash

def main():
    print("Step 1: creating database tables...", flush=True)
    Base.metadata.create_all(bind=engine)
    print("Step 2: tables created successfully!", flush=True)

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "demo@medicalai.org").first()
        if not user:
            u = User(email="demo@medicalai.org", hashed_password=get_password_hash("MedicalAI2026!"), full_name="Dr. Alex Rivera")
            db.add(u)
            db.commit()
            print("Step 3: demo user inserted!", flush=True)
        else:
            print("Step 3: demo user verified in database!", flush=True)
    finally:
        db.close()

    print("Step 4: database check completed successfully!", flush=True)

if __name__ == "__main__":
    main()
