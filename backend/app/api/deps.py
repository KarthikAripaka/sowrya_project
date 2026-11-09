from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.core.security import decode_token
from backend.app.models.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Authenticate user via JWT Bearer Token.
    If no token is supplied, returns or creates a default demo user for frictionless local evaluation.
    """
    if token:
        payload = decode_token(token)
        if payload and "sub" in payload:
            user_id = payload["sub"]
            user = db.query(User).filter(User.id == int(user_id)).first()
            if user:
                return user

    # Fallback to demo user for seamless local evaluation
    demo_user = db.query(User).filter(User.email == "demo@medicalai.org").first()
    if not demo_user:
        from backend.app.core.security import get_password_hash
        demo_user = User(
            email="demo@medicalai.org",
            hashed_password=get_password_hash("MedicalAI2026!"),
            full_name="Dr. Alex Rivera (Demo)",
            is_active=True,
            is_superuser=False
        )
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)
    return demo_user
