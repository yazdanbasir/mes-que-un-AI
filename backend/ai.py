import os
import re
from groq import AsyncGroq

_client: AsyncGroq | None = None


def get_client() -> AsyncGroq:
    global _client
    if _client is None:
        key = os.environ.get("GROQ_API_KEY")
        if not key:
            raise RuntimeError("GROQ_API_KEY not set")
        _client = AsyncGroq(api_key=key)
    return _client


# ── Lookup ────────────────────────────────────────────────────────────────────

_LOOKUP_SYSTEM = """Eres un tutor de español. El usuario está leyendo un artículo y ha seleccionado una palabra o frase.
Responde SIEMPRE en este formato exacto (sin texto adicional):

DEFINICIÓN: [definición en español simple, máximo 2 frases]
TRADUCCIÓN: [traducción al inglés]
CATEGORÍA: [una de: verbo reflexivo, subjuntivo, vocabulario fútbol, expresión idiomática, vocabulario general]"""

_DEF_RE  = re.compile(r'DEFINICI[OÓ]N\s*:+\s*\*{0,2}(.*?)(?=TRADUCCI|\Z)', re.IGNORECASE | re.DOTALL)
_TRA_RE  = re.compile(r'TRADUCCI[OÓ]N\s*:+\s*\*{0,2}(.*?)(?=CATEGOR|\Z)',  re.IGNORECASE | re.DOTALL)
_CAT_RE  = re.compile(r'CATEGOR[IÍ]A\s*:+\s*\*{0,2}(.*)',                  re.IGNORECASE)


async def lookup(phrase: str, sentence: str) -> dict:
    client = get_client()
    resp = await client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": _LOOKUP_SYSTEM},
            {"role": "user", "content": f'Frase: "{phrase}"\nContexto: "{sentence}"'},
        ],
        max_tokens=180,
        temperature=0.3,
    )
    text = resp.choices[0].message.content or ""
    def_match = _DEF_RE.search(text)
    tra_match = _TRA_RE.search(text)
    cat_match = _CAT_RE.search(text)
    return {
        "definition":  def_match.group(1).strip().strip("*").strip() if def_match else "",
        "translation": tra_match.group(1).strip().strip("*").strip() if tra_match else "",
        "category":    cat_match.group(1).strip().strip("*").strip() if cat_match else "",
    }


# ── TPRS Narrative ────────────────────────────────────────────────────────────

_NARRATIVE_SYSTEM = """Eres un profesor de español creando ejercicios de lectura para estudiantes de nivel A2-B1.
Dado el titular y resumen de una noticia deportiva, escribe una micro-narrativa TPRS de 3-5 frases:
- Tiempo presente simple
- Vocabulario nivel A2-B1
- Incluye quién, qué pasó, resultado
- Solo en español, sin traducciones ni explicaciones
- Sin título, solo el texto narrativo"""


async def generate_narrative(title: str, summary: str) -> str:
    client = get_client()
    resp = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": _NARRATIVE_SYSTEM},
            {"role": "user", "content": f"Titular: {title}\nResumen: {summary or 'No disponible'}"},
        ],
        max_tokens=200,
        temperature=0.5,
    )
    return (resp.choices[0].message.content or "").strip()


# ── SRS production feedback ───────────────────────────────────────────────────

_PRODUCTION_SYSTEM = """Eres un tutor de español. El estudiante ha escrito una frase usando una palabra o expresión que está aprendiendo.
Evalúa si el uso es natural y correcto. Responde en una o dos frases máximo, en español.
Sé directo: di si está bien o qué cambiarías, y por qué. Sin saludos ni preámbulos."""


async def evaluate_production(phrase: str, student_sentence: str) -> str:
    client = get_client()
    resp = await client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": _PRODUCTION_SYSTEM},
            {"role": "user", "content": f'Expresión: "{phrase}"\nFrase del estudiante: "{student_sentence}"'},
        ],
        max_tokens=120,
        temperature=0.4,
    )
    return (resp.choices[0].message.content or "").strip()
