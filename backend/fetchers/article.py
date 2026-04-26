import httpx
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-ES,es;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# Ordered from most specific to most general
BODY_SELECTORS = [
    ".article-body",
    ".article__body",
    ".article-content",
    ".news-body",
    ".story-body",
    ".content-detail",
    ".noticia-cuerpo",
    ".articulo-cuerpo",
    "[itemprop='articleBody']",
    "article",
    "main",
]

NOISE_TAGS = ["script", "style", "nav", "header", "footer", "aside",
              "figure", "figcaption", "iframe", "noscript", "form"]


async def fetch_article_text(url: str) -> str:
    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        r = await client.get(url, headers=HEADERS)
        r.raise_for_status()

    soup = BeautifulSoup(r.text, "lxml")

    for tag in soup(NOISE_TAGS):
        tag.decompose()

    for selector in BODY_SELECTORS:
        container = soup.select_one(selector)
        if container:
            paras = [p.get_text(" ", strip=True) for p in container.find_all("p")]
            text = "\n\n".join(p for p in paras if len(p) > 50)
            if text:
                return text

    # fallback: all paragraphs on the page
    paras = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    return "\n\n".join(p for p in paras if len(p) > 50)
