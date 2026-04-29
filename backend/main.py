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
from pau_questions import get_opening_question


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


# ── Saved articles ────────────────────────────────────────────────────────────

class SaveArticleRequest(BaseModel):
    id: str
    title: str
    source: str
    url: str
    image_url: Optional[str] = None
    summary: Optional[str] = None


@app.post("/api/saved")
def save_article(req: SaveArticleRequest):
    db.save_article({
        "id":        req.id,
        "title":     req.title,
        "source":    req.source,
        "url":       req.url,
        "image_url": req.image_url,
        "summary":   req.summary,
        "saved_at":  datetime.now(timezone.utc).isoformat(),
    })
    return {"status": "ok"}


@app.get("/api/saved")
def get_saved():
    return db.get_saved_articles()


@app.delete("/api/saved/{article_id}")
def unsave_article(article_id: str):
    db.unsave_article(article_id)
    return {"status": "ok"}


@app.get("/api/prefs/{key}")
def get_pref(key: str, default: str = ""):
    return {"value": db.get_pref(key, default)}


@app.post("/api/prefs/{key}")
def set_pref(key: str, body: dict):
    db.set_pref(key, str(body.get("value", "")))
    return {"status": "ok"}


@app.get("/api/read")
def get_read():
    return db.get_read_ids()


@app.post("/api/read/{article_id}")
def mark_read(article_id: str):
    db.mark_read(article_id)
    return {"status": "ok"}


@app.delete("/api/read/{article_id}")
def unmark_read(article_id: str):
    db.unmark_read(article_id)
    return {"status": "ok"}


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


# ── Pau ───────────────────────────────────────────────────────────────────────

class PauRespondRequest(BaseModel):
    turn_id: str
    answer: str


@app.post("/api/pau/sessions")
def start_pau_session():
    session = db.create_pau_session()
    opening = get_opening_question()
    turn = db.create_pau_turn(session["id"], opening["question"])
    return {
        "session_id": session["id"],
        "question": opening["question"],
        "turn_id": turn["id"],
    }


@app.post("/api/pau/sessions/{session_id}/respond")
async def respond_to_pau(session_id: str, req: PauRespondRequest):
    import json as _json

    session_data = db.get_pau_session(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")

    current_turn = next((t for t in session_data["turns"] if t["id"] == req.turn_id), None)
    if not current_turn:
        raise HTTPException(status_code=404, detail="Turn not found")

    history = [t for t in session_data["turns"] if t.get("user_answer")]

    try:
        result = await ai.pau_respond(current_turn["pau_question"], req.answer.strip(), history)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    correction = result.get("correction", {})
    pau_response = result.get("pau_response", "¡Interesante!")
    next_question = result.get("next_question", "¿Qué más puedes contarme?")
    flagged_vocab = result.get("flagged_vocab", [])

    db.complete_pau_turn(
        req.turn_id,
        req.answer.strip(),
        correction.get("corrected", req.answer),
        correction.get("note"),
        _json.dumps(flagged_vocab),
    )

    saved_to_revision = []
    for item in flagged_vocab:
        if item.get("phrase"):
            phrase_id = uuid.uuid4().hex
            db.save_phrase({
                "id":          phrase_id,
                "phrase":      item["phrase"],
                "sentence":    item.get("sentence", ""),
                "translation": None,
                "definition":  item.get("note", ""),
                "category":    "gramática",
                "article_id":  None,
                "source":      "pau",
                "saved_at":    datetime.now(timezone.utc).isoformat(),
                "srs_stage":   0,
                "next_review": datetime.now(timezone.utc).isoformat(),
            })
            saved_to_revision.append(item["phrase"])

    next_turn = db.create_pau_turn(session_id, next_question)

    return {
        "correction": correction,
        "pau_response": pau_response,
        "next_question": next_question,
        "next_turn_id": next_turn["id"],
        "flagged_vocab": flagged_vocab,
        "saved_to_revision": saved_to_revision,
    }


@app.get("/api/pau/sessions")
def get_pau_sessions():
    return db.get_pau_sessions()


@app.get("/api/pau/sessions/{session_id}")
def get_pau_session(session_id: str):
    session = db.get_pau_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
