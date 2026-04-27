from pydantic import BaseModel
from typing import Optional


class Article(BaseModel):
    id: str
    source: str
    title: str
    summary: Optional[str]
    url: str
    published_at: Optional[str]
    fetched_at: str
    image_url: Optional[str]


class ReviewResult(BaseModel):
    feedback: str
