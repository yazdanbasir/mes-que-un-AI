from contextlib import asynccontextmanager
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import db
from fetchers.rss import fetch_all
from models import Article


async def _refresh() -> None:
    articles = await fetch_all()
    db.upsert(articles)
    print(f"[refresh] stored {len(articles)} articles")


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init()
    await _refresh()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(_refresh, "interval", minutes=20)
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", "http://localhost:5173", "http://localhost:8001"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/articles", response_model=list[Article])
def get_articles(source: Optional[str] = None):
    return db.get_all(source)


@app.get("/api/articles/refresh")
async def manual_refresh():
    await _refresh()
    return {"status": "ok"}
