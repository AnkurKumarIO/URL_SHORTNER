from fastapi import FastAPI
from app.database import engine, Base
from app.routers import shorten, redirect

# Create database tables automatically on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="URL Shortener API",
    description="High-performance URL Shortener built with FastAPI, PostgreSQL, and Redis.",
    version="1.0.0"
)

# Include endpoint routers
app.include_router(shorten.router)
app.include_router(redirect.router)

@app.get("/")
def health_check():
    return {"status": "online", "message": "URL Shortener API is running!"}
