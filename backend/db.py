import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).parent / "articles.db"

# SRS intervals in days per stage (0-indexed)
SRS_INTERVALS = [1, 3, 7, 14, 30]


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def init() -> None:
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id           TEXT PRIMARY KEY,
                source       TEXT NOT NULL,
                title        TEXT NOT NULL,
                summary      TEXT,
                url          TEXT NOT NULL,
                published_at TEXT,
                fetched_at   TEXT NOT NULL,
                image_url    TEXT
            )
        """)
        cols = [row[1] for row in conn.execute("PRAGMA table_info(articles)").fetchall()]
        if "image_url" not in cols:
            conn.execute("ALTER TABLE articles ADD COLUMN image_url TEXT")

        conn.execute("""
            CREATE TABLE IF NOT EXISTS narratives (
                article_id TEXT PRIMARY KEY,
                content    TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS saved_phrases (
                id          TEXT PRIMARY KEY,
                phrase      TEXT NOT NULL,
                sentence    TEXT NOT NULL,
                translation TEXT,
                definition  TEXT,
                category    TEXT,
                article_id  TEXT,
                source      TEXT,
                saved_at    TEXT NOT NULL,
                srs_stage   INTEGER NOT NULL DEFAULT 0,
                next_review TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        # migrate existing saved_phrases tables
        sp_cols = [row[1] for row in conn.execute("PRAGMA table_info(saved_phrases)").fetchall()]
        for col, defn in [
            ("category",    "TEXT"),
            ("srs_stage",   "INTEGER NOT NULL DEFAULT 0"),
            ("next_review", "TEXT NOT NULL DEFAULT (datetime('now'))"),
        ]:
            if col not in sp_cols:
                conn.execute(f"ALTER TABLE saved_phrases ADD COLUMN {col} {defn}")


# ── Articles ──────────────────────────────────────────────────────────────────

def upsert(articles: list[dict]) -> None:
    if not articles:
        return
    with _connect() as conn:
        conn.executemany(
            """
            INSERT INTO articles
                (id, source, title, summary, url, published_at, fetched_at, image_url)
            VALUES
                (:id, :source, :title, :summary, :url, :published_at, :fetched_at, :image_url)
            ON CONFLICT(id) DO UPDATE SET
                title        = excluded.title,
                summary      = excluded.summary,
                published_at = excluded.published_at,
                fetched_at   = excluded.fetched_at,
                image_url    = excluded.image_url
            """,
            articles,
        )


def get_by_id(article_id: str) -> Optional[dict]:
    with _connect() as conn:
        row = conn.execute("SELECT * FROM articles WHERE id = ?", (article_id,)).fetchone()
    return dict(row) if row else None


def get_all(source: Optional[str] = None) -> list[dict]:
    with _connect() as conn:
        if source:
            rows = conn.execute(
                "SELECT * FROM articles WHERE source = ? ORDER BY COALESCE(published_at, fetched_at) DESC",
                (source,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM articles ORDER BY COALESCE(published_at, fetched_at) DESC"
            ).fetchall()
    return [dict(row) for row in rows]


# ── Narratives ────────────────────────────────────────────────────────────────

def get_narrative(article_id: str) -> Optional[str]:
    with _connect() as conn:
        row = conn.execute("SELECT content FROM narratives WHERE article_id = ?", (article_id,)).fetchone()
    return row[0] if row else None


def save_narrative(article_id: str, content: str) -> None:
    with _connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO narratives (article_id, content, created_at) VALUES (?, ?, ?)",
            (article_id, content, _now()),
        )


# ── Saved phrases + SRS ───────────────────────────────────────────────────────

def save_phrase(phrase: dict) -> None:
    with _connect() as conn:
        conn.execute(
            """INSERT OR REPLACE INTO saved_phrases
               (id, phrase, sentence, translation, definition, category,
                article_id, source, saved_at, srs_stage, next_review)
               VALUES (:id, :phrase, :sentence, :translation, :definition, :category,
                       :article_id, :source, :saved_at, :srs_stage, :next_review)""",
            phrase,
        )


def get_phrases() -> list[dict]:
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM saved_phrases ORDER BY saved_at DESC").fetchall()
    return [dict(row) for row in rows]


def get_due_phrases() -> list[dict]:
    """Return phrases whose next_review is now or in the past."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM saved_phrases WHERE next_review <= ? ORDER BY next_review ASC",
            (_now(),),
        ).fetchall()
    return [dict(row) for row in rows]


def advance_srs(phrase_id: str, remembered: bool) -> None:
    """Advance or reset SRS stage and set next_review date."""
    from datetime import timedelta
    with _connect() as conn:
        row = conn.execute("SELECT srs_stage FROM saved_phrases WHERE id = ?", (phrase_id,)).fetchone()
        if not row:
            return
        current = row[0]
        if remembered:
            new_stage = min(current + 1, len(SRS_INTERVALS) - 1)
        else:
            new_stage = 0
        days = SRS_INTERVALS[new_stage]
        next_review = (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()
        conn.execute(
            "UPDATE saved_phrases SET srs_stage = ?, next_review = ? WHERE id = ?",
            (new_stage, next_review, phrase_id),
        )


def delete_phrase(phrase_id: str) -> None:
    with _connect() as conn:
        conn.execute("DELETE FROM saved_phrases WHERE id = ?", (phrase_id,))
