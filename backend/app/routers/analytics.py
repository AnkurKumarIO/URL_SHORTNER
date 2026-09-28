from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Link, Click
from app.schemas import LinkAnalytics

router = APIRouter()

@router.get("/analytics/{short_code}")
def get_link_analytics(short_code: str, db: Session = Depends(get_db)):
    link_record = db.query(Link).filter(Link.short_code == short_code).first()
    if not link_record:
        raise HTTPException(status_code=404, detail="Short code not found.")

    total_clicks = db.query(func.count(Click.id)).filter(Click.link_id == link_record.id).scalar()

    # Get recent click timestamps
    recent_clicks = (
        db.query(Click.clicked_at, Click.referrer)
        .filter(Click.link_id == link_record.id)
        .order_by(Click.clicked_at.desc())
        .limit(10)
        .all()
    )

    return {
        "short_code": link_record.short_code,
        "long_url": link_record.long_url,
        "created_at": link_record.created_at.isoformat(),
        "total_clicks": total_clicks,
        "recent_clicks": [
            {"clicked_at": c[0].isoformat(), "referrer": c[1]} for c in recent_clicks
        ]
    }

@router.get("/analytics")
def get_all_links_summary(db: Session = Depends(get_db)):
    """Summary of all shortened links and total click counts for dashboard."""
    links = db.query(Link).all()
    results = []
    for link in links:
        total_clicks = db.query(func.count(Click.id)).filter(Click.link_id == link.id).scalar()
        results.append({
            "short_code": link.short_code,
            "long_url": link.long_url,
            "created_at": link.created_at.isoformat(),
            "total_clicks": total_clicks
        })
    return results
