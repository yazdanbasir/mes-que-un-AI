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
            CREATE TABLE IF NOT EXISTS pau_sessions (
                id          TEXT PRIMARY KEY,
                started_at  TEXT NOT NULL,
                last_active TEXT NOT NULL,
                turn_count  INTEGER DEFAULT 0
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS pau_turns (
                id               TEXT PRIMARY KEY,
                session_id       TEXT NOT NULL,
                pau_question     TEXT NOT NULL,
                user_answer      TEXT,
                corrected_answer TEXT,
                grammar_note     TEXT,
                flagged_vocab    TEXT,
                created_at       TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES pau_sessions(id)
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
        conn.execute("""
            CREATE TABLE IF NOT EXISTS preferences (
                key   TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        init_saved_articles(conn)
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


# ── Saved articles ────────────────────────────────────────────────────────────

def init_saved_articles(conn) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS saved_articles (
            id        TEXT PRIMARY KEY,
            title     TEXT NOT NULL,
            source    TEXT NOT NULL,
            url       TEXT NOT NULL,
            image_url TEXT,
            summary   TEXT,
            saved_at  TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS read_articles (
            id      TEXT PRIMARY KEY,
            read_at TEXT NOT NULL
        )
    """)


def save_article(article: dict) -> None:
    with _connect() as conn:
        conn.execute(
            """INSERT OR REPLACE INTO saved_articles
               (id, title, source, url, image_url, summary, saved_at)
               VALUES (:id, :title, :source, :url, :image_url, :summary, :saved_at)""",
            article,
        )


def unsave_article(article_id: str) -> None:
    with _connect() as conn:
        conn.execute("DELETE FROM saved_articles WHERE id = ?", (article_id,))


def mark_read(article_id: str) -> None:
    with _connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO read_articles (id, read_at) VALUES (?, ?)",
            (article_id, _now()),
        )


def unmark_read(article_id: str) -> None:
    with _connect() as conn:
        conn.execute("DELETE FROM read_articles WHERE id = ?", (article_id,))


def get_pref(key: str, default: str) -> str:
    with _connect() as conn:
        row = conn.execute("SELECT value FROM preferences WHERE key = ?", (key,)).fetchone()
    return row[0] if row else default


def set_pref(key: str, value: str) -> None:
    with _connect() as conn:
        conn.execute("INSERT OR REPLACE INTO preferences (key, value) VALUES (?, ?)", (key, value))


def get_read_ids() -> list[str]:
    with _connect() as conn:
        rows = conn.execute("SELECT id FROM read_articles").fetchall()
    return [row[0] for row in rows]


def get_saved_articles() -> list[dict]:
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM saved_articles ORDER BY saved_at DESC").fetchall()
    return [dict(row) for row in rows]


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


# ── Pau sessions + turns ───────────────────────────────────────────────────────

def create_pau_session() -> dict:
    import uuid
    session_id = uuid.uuid4().hex
    now = _now()
    with _connect() as conn:
        conn.execute(
            "INSERT INTO pau_sessions (id, started_at, last_active, turn_count) VALUES (?, ?, ?, 0)",
            (session_id, now, now),
        )
    return {"id": session_id, "started_at": now, "last_active": now, "turn_count": 0}


def create_pau_turn(session_id: str, question: str) -> dict:
    import uuid
    turn_id = uuid.uuid4().hex
    now = _now()
    with _connect() as conn:
        conn.execute(
            "INSERT INTO pau_turns (id, session_id, pau_question, created_at) VALUES (?, ?, ?, ?)",
            (turn_id, session_id, question, now),
        )
        conn.execute(
            "UPDATE pau_sessions SET last_active = ?, turn_count = turn_count + 1 WHERE id = ?",
            (now, session_id),
        )
    return {"id": turn_id, "session_id": session_id, "pau_question": question, "created_at": now}


def complete_pau_turn(turn_id: str, user_answer: str, corrected_answer: str, grammar_note: Optional[str], flagged_vocab: str) -> None:
    with _connect() as conn:
        conn.execute(
            """UPDATE pau_turns
               SET user_answer = ?, corrected_answer = ?, grammar_note = ?, flagged_vocab = ?
               WHERE id = ?""",
            (user_answer, corrected_answer, grammar_note, flagged_vocab, turn_id),
        )


def get_pau_sessions() -> list[dict]:
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM pau_sessions ORDER BY last_active DESC").fetchall()
    return [dict(row) for row in rows]


def get_pau_session(session_id: str) -> Optional[dict]:
    with _connect() as conn:
        session_row = conn.execute("SELECT * FROM pau_sessions WHERE id = ?", (session_id,)).fetchone()
        if not session_row:
            return None
        turns = conn.execute(
            "SELECT * FROM pau_turns WHERE session_id = ? ORDER BY created_at ASC",
            (session_id,),
        ).fetchall()
    return {**dict(session_row), "turns": [dict(t) for t in turns]}
