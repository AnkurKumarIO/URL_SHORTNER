from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.models import Link
from app.schemas import ShortenRequest, ShortenResponse
from app.utils import generate_random_short_code
from app.cache import set_cached_url

router = APIRouter()

@router.post("/shorten", response_model=ShortenResponse)
def shorten_url(payload: ShortenRequest, request: Request, db: Session = Depends(get_db)):
    long_url_str = str(payload.url)
    
    # Try generating a unique short code with retries for handling collisions
    for _ in range(5):
        short_code = generate_random_short_code(6)
        new_link = Link(short_code=short_code, long_url=long_url_str)
        try:
            db.add(new_link)
            db.commit()
            db.refresh(new_link)
            
            # Populate Redis cache immediately
            set_cached_url(short_code, long_url_str)
            
            base_url = str(request.base_url).rstrip("/")
            return ShortenResponse(
                short_code=short_code,
                short_url=f"{base_url}/r/{short_code}",
                long_url=long_url_str
            )
        except IntegrityError:
            db.rollback()
            continue

    raise HTTPException(status_code=500, detail="Failed to generate unique short code. Please try again.")
