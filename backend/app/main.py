from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import shorten, redirect, analytics

# Create database tables automatically on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="URL Shortener API",
    description="High-performance URL Shortener built with FastAPI, PostgreSQL, and Redis.",
    version="1.0.0"
)

# Enable CORS for frontend dashboard (Day 5)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include endpoint routers
app.include_router(shorten.router)
app.include_router(redirect.router)
app.include_router(analytics.router)

@app.get("/")
def health_check():
    return {"status": "online", "message": "URL Shortener API is running!"}
