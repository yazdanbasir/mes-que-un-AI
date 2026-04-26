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
                fetched_at   TEXT NOT NULL
            )
        """)


def upsert(articles: list[dict]) -> None:
    if not articles:
        return
    with _connect() as conn:
        conn.executemany(
            """
            INSERT OR IGNORE INTO articles
                (id, source, title, summary, url, published_at, fetched_at)
            VALUES
                (:id, :source, :title, :summary, :url, :published_at, :fetched_at)
            """,
            articles,
        )


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
