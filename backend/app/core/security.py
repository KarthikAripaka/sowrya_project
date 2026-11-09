import datetime
from typing import Optional, Union, Any
from jose import jwt, JWTError
import hashlib
import hmac
import os
from backend.app.core.config import settings

# Robust password hashing using PBKDF2-HMAC-SHA256 (standard, cryptographically secure, zero-dependency)
# and bcrypt compatible formatting.


def get_password_hash(password: str) -> str:
    salt = os.urandom(16).hex()
    iterations = 100_000
    derived = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations
    ).hex()
    return f"pbkdf2:sha256:{iterations}${salt}${derived}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        if hashed_password.startswith("pbkdf2:sha256:"):
            parts = hashed_password.split("$")
            iterations = int(parts[0].split(":")[2])
            salt = parts[1]
            original_hash = parts[2]
            derived = hashlib.pbkdf2_hmac(
                "sha256",
                plain_password.encode("utf-8"),
                salt.encode("utf-8"),
                iterations,
            ).hex()
            return hmac.compare_digest(derived, original_hash)
        # Fallback for plain bcrypt if present
        from passlib.context import CryptContext

        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[datetime.timedelta] = None
) -> str:
    if expires_delta:
        expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta
    else:
        expire = datetime.datetime.now(
            datetime.timezone.utc
        ) + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "access",
    }
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(subject: Union[str, Any]) -> str:
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh",
    }
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None

