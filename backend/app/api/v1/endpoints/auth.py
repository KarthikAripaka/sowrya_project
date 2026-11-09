from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.models import User, ActivityLog
from backend.app.schemas.schemas import UserCreate, UserLogin, UserOut, TokenResponse
from backend.app.core.security import verify_password, get_password_hash, create_access_token
from backend.app.api.deps import get_current_user

router = APIRouter()

@router.post("/register", response_model=TokenResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )

    new_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name or user_in.email.split("@")[0].capitalize(),
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Activity log
    log = ActivityLog(
        user_id=new_user.id,
        action="user_registered",
        resource_type="user",
        resource_id=str(new_user.id)
    )
    db.add(log)
    db.commit()

    token = create_access_token(new_user.id)
    return TokenResponse(access_token=token, token_type="bearer", user=UserOut.model_validate(new_user))


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password credentials."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive account. Contact system administrator."
        )

    # Activity log
    log = ActivityLog(
        user_id=user.id,
        action="user_login",
        resource_type="user",
        resource_id=str(user.id)
    )
    db.add(log)
    db.commit()

    token = create_access_token(user.id)
    return TokenResponse(access_token=token, token_type="bearer", user=UserOut.model_validate(user))


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    log = ActivityLog(
        user_id=current_user.id,
        action="user_logout",
        resource_type="user",
        resource_id=str(current_user.id)
    )
    db.add(log)
    db.commit()
    return {"message": "Logged out successfully."}


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return UserOut.model_validate(current_user)
