import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    try:
        pg_url = "postgresql://postgres:postgres@localhost:5432/urlshortener"
        test_engine = create_engine(pg_url)
        with test_engine.connect() as conn:
            pass
        DATABASE_URL = pg_url
    except Exception:
        DATABASE_URL = "sqlite:///./urlshortener.db"

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

