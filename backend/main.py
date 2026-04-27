import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

import ai
import db
from fetchers.article import fetch_article_text
from fetchers.rss import fetch_all
from models import Article, ReviewResult


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
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)


# ── Articles ──────────────────────────────────────────────────────────────────

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


@app.get("/api/articles/{article_id}/content")
async def get_article_content(article_id: str):
    article = db.get_by_id(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    try:
        text = await fetch_article_text(article["url"])
        return {"content": text}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.post("/api/articles/{article_id}/narrative")
async def get_narrative(article_id: str):
    cached = db.get_narrative(article_id)
    if cached:
        return {"narrative": cached}
    article = db.get_by_id(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    try:
        narrative = await ai.generate_narrative(article["title"], article["summary"] or "")
        db.save_narrative(article_id, narrative)
        return {"narrative": narrative}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


# ── Comprehension ─────────────────────────────────────────────────────────────

class ComprehensionRequest(BaseModel):
    content: str


class ComprehensionEvalRequest(BaseModel):
    content: str
    questions: list[str]
    answers: list[str]


@app.post("/api/articles/{article_id}/comprehension/questions")
async def get_comprehension_questions(article_id: str, req: ComprehensionRequest):
    try:
        questions = await ai.generate_comprehension_questions(req.content)
        return {"questions": questions}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.post("/api/articles/{article_id}/comprehension/evaluate")
async def evaluate_comprehension(article_id: str, req: ComprehensionEvalRequest):
    try:
        feedback = await ai.evaluate_comprehension(req.content, req.questions, req.answers)
        return {"feedback": feedback}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


# ── Lookup ────────────────────────────────────────────────────────────────────

class LookupRequest(BaseModel):
    phrase: str
    sentence: str


@app.post("/api/lookup")
async def lookup(req: LookupRequest):
    if not req.phrase.strip():
        raise HTTPException(status_code=400, detail="phrase is required")
    try:
        result = await ai.lookup(req.phrase.strip(), req.sentence.strip())
        return result
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


# ── Deck ──────────────────────────────────────────────────────────────────────

class SavePhraseRequest(BaseModel):
    phrase: str
    sentence: str
    translation: Optional[str] = None
    definition: Optional[str] = None
    category: Optional[str] = None
    article_id: Optional[str] = None
    source: Optional[str] = None


@app.post("/api/deck")
def save_phrase(req: SavePhraseRequest):
    phrase_id = uuid.uuid4().hex
    db.save_phrase({
        "id":          phrase_id,
        "phrase":      req.phrase,
        "sentence":    req.sentence,
        "translation": req.translation,
        "definition":  req.definition,
        "category":    req.category,
        "article_id":  req.article_id,
        "source":      req.source,
        "saved_at":    datetime.now(timezone.utc).isoformat(),
        "srs_stage":   0,
        "next_review": datetime.now(timezone.utc).isoformat(),
    })
    return {"status": "ok", "id": phrase_id}


@app.get("/api/deck")
def get_deck():
    return db.get_phrases()


@app.get("/api/deck/due")
def get_due():
    return db.get_due_phrases()


@app.delete("/api/deck/{phrase_id}")
def delete_phrase(phrase_id: str):
    db.delete_phrase(phrase_id)
    return {"status": "ok"}


@app.get("/api/deck/export")
def export_deck():
    from fastapi.responses import StreamingResponse
    import csv, io
    phrases = db.get_phrases()
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=["phrase", "sentence", "translation", "definition", "category", "source", "saved_at"])
    writer.writeheader()
    writer.writerows(phrases)
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=deck.csv"},
    )


class AdvanceSRSRequest(BaseModel):
    remembered: bool


@app.post("/api/deck/{phrase_id}/review")
def advance_srs(phrase_id: str, req: AdvanceSRSRequest):
    db.advance_srs(phrase_id, req.remembered)
    return {"status": "ok"}


class ProductionRequest(BaseModel):
    phrase: str
    sentence: str


@app.post("/api/deck/{phrase_id}/evaluate")
async def evaluate_production(phrase_id: str, req: ProductionRequest):
    try:
        feedback = await ai.evaluate_production(req.phrase, req.sentence)
        return {"feedback": feedback}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
