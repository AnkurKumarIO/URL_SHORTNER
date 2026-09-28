from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Link
from app.cache import get_cached_url, set_cached_url

router = APIRouter()

@router.get("/r/{short_code}")
def redirect_to_url(short_code: str, db: Session = Depends(get_db)):
    # 1. Check Redis cache first (RAM speed ~1-2ms)
    cached_long_url = get_cached_url(short_code)
    if cached_long_url:
        return RedirectResponse(url=cached_long_url, status_code=307)
    
    # 2. Cache Miss: Fall back to PostgreSQL database query
    link_record = db.query(Link).filter(Link.short_code == short_code).first()
    if not link_record:
        raise HTTPException(status_code=404, detail="Short code not found.")
    
    # 3. Write back to Redis cache for future requests
    set_cached_url(short_code, link_record.long_url)
    
    # 4. Respond with HTTP 307 Temporary Redirect
    return RedirectResponse(url=link_record.long_url, status_code=307)
