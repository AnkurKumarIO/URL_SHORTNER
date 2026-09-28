from pydantic import BaseModel, HttpUrl

class ShortenRequest(BaseModel):
    url: HttpUrl

class ShortenResponse(BaseModel):
    short_code: str
    short_url: str
    long_url: str

class LinkAnalytics(BaseModel):
    short_code: str
    long_url: str
    total_clicks: int
    created_at: str
