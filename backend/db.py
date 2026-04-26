import sqlite3
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).parent / "articles.db"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


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
        # migrate existing DBs that predate the image_url column
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
                article_id  TEXT,
                source      TEXT,
                saved_at    TEXT NOT NULL
            )
        """)


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
        row = conn.execute(
            "SELECT * FROM articles WHERE id = ?", (article_id,)
        ).fetchone()
    return dict(row) if row else None


def get_narrative(article_id: str) -> Optional[str]:
    with _connect() as conn:
        row = conn.execute(
            "SELECT content FROM narratives WHERE article_id = ?", (article_id,)
        ).fetchone()
    return row[0] if row else None


def save_narrative(article_id: str, content: str) -> None:
    from datetime import datetime, timezone
    with _connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO narratives (article_id, content, created_at) VALUES (?, ?, ?)",
            (article_id, content, datetime.now(timezone.utc).isoformat()),
        )


def save_phrase(phrase: dict) -> None:
    with _connect() as conn:
        conn.execute(
            """INSERT OR REPLACE INTO saved_phrases
               (id, phrase, sentence, translation, definition, article_id, source, saved_at)
               VALUES (:id, :phrase, :sentence, :translation, :definition, :article_id, :source, :saved_at)""",
            phrase,
        )


def get_phrases() -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM saved_phrases ORDER BY saved_at DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def delete_phrase(phrase_id: str) -> None:
    with _connect() as conn:
        conn.execute("DELETE FROM saved_phrases WHERE id = ?", (phrase_id,))


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
