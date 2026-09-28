from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import datetime
from app.database import SessionLocal, get_db
from app.models import Link, Click
from app.cache import get_cached_url, set_cached_url

router = APIRouter()


def record_click_in_background(short_code: str, referrer: str | None, user_agent: str | None):
    """Background task function to record a click event asynchronously in PostgreSQL."""
    db = SessionLocal()
    try:
        link_record = db.query(Link).filter(Link.short_code == short_code).first()
        if link_record:
            # Extract basic info (referrer and country placeholder)
            new_click = Click(
                link_id=link_record.id,
                clicked_at=datetime.datetime.utcnow(),
                referrer=referrer,
                country="Unknown"
            )
            db.add(new_click)
            db.commit()
    except Exception as e:
        db.rollback()
    finally:
        db.close()


@router.get("/r/{short_code}")
def redirect_to_url(
    short_code: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # Schedule click logging as an asynchronous background task
    referrer_hdr = request.headers.get("referer")
    user_agent_hdr = request.headers.get("user-agent")
    background_tasks.add_task(record_click_in_background, short_code, referrer_hdr, user_agent_hdr)

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

    # 4. Respond immediately with HTTP 307 Temporary Redirect
    return RedirectResponse(url=link_record.long_url, status_code=307)
