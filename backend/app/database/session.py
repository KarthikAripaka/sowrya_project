from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.app.core.config import settings

# Format database URL for SQLite / PostgreSQL
db_url = settings.DATABASE_URL
if db_url.startswith("sqlite+aiosqlite:"):
    db_url = db_url.replace("sqlite+aiosqlite:", "sqlite:")
elif db_url.startswith("postgresql+asyncpg:"):
    db_url = db_url.replace("postgresql+asyncpg:", "postgresql:")

connect_args = {}
if "sqlite" in db_url:
    connect_args = {"check_same_thread": False}

engine = create_engine(
    db_url,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
