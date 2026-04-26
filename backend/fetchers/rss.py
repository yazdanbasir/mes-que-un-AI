import asyncio
import hashlib
import re
from datetime import datetime, timezone
from typing import Optional

import feedparser

SOURCES: dict[str, str] = {
    "marca":          "https://e00-marca.uecdn.es/rss/futbol/primera-division.xml",
    "as":             "https://as.com/rss/tags/futbol.xml",
    "sport":          "https://www.sport.es/rss/portada.rss",
    "mundodeportivo": "https://www.mundodeportivo.com/feed/rss/",
    "lavanguardia":   "https://www.lavanguardia.com/rss/deporte.xml",
    "elpais":         "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/deportes/portada",
}

_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(text: str) -> str:
    return _TAG_RE.sub("", text).strip()


def _get_image(entry) -> Optional[str]:
    for thumb in entry.get("media_thumbnail", []):
        url = thumb.get("url")
        if url:
            return url
    for m in entry.get("media_content", []):
        if m.get("medium") == "image" or m.get("type", "").startswith("image/"):
            url = m.get("url")
            if url:
                return url
    for enc in entry.get("enclosures", []):
        if enc.get("type", "").startswith("image/"):
            return enc.get("href") or enc.get("url")
    return None


def _parse_date(entry) -> Optional[str]:
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if parsed:
        return datetime(*parsed[:6], tzinfo=timezone.utc).isoformat()
    return None


def _fetch_source_sync(name: str, url: str) -> list[dict]:
    feed = feedparser.parse(url)
    now = datetime.now(timezone.utc).isoformat()
    articles = []
    for entry in feed.entries:
        link = entry.get("link", "")
        if not link:
            continue
        title = _strip_html(entry.get("title", "")).strip()
        if not title:
            continue
        summary_raw = entry.get("summary") or entry.get("description") or ""
        summary = _strip_html(summary_raw) or None
        articles.append({
            "id":           hashlib.sha1(link.encode()).hexdigest()[:16],
            "source":       name,
            "title":        title,
            "summary":      summary,
            "url":          link,
            "published_at": _parse_date(entry),
            "fetched_at":   now,
            "image_url":    _get_image(entry),
        })
    return articles


async def fetch_source(name: str, url: str) -> list[dict]:
    return await asyncio.to_thread(_fetch_source_sync, name, url)


async def fetch_all() -> list[dict]:
    tasks = [fetch_source(name, url) for name, url in SOURCES.items()]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    articles = []
    for name, result in zip(SOURCES.keys(), results):
        if isinstance(result, Exception):
            print(f"[rss] failed to fetch {name}: {result}")
        else:
            articles.extend(result)
    return articles
