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

_LOOKUP_SYSTEM = """You are a Spanish language tutor. The user is reading a Spanish article and selected a word or phrase they don't understand.
Always respond in this exact format (no extra text):

DEFINICIÓN: [definition in Spanish, max 1 sentence] / [same definition in English, max 1 sentence]
TRADUCCIÓN: [English translation, 1-5 words]
CATEGORÍA: [one of: subjuntivo, verbo reflexivo, expresión idiomática, vocabulario fútbol, locución prepositiva, vocabulario periodístico, falso amigo, otro]"""

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

# ── Comprehension ─────────────────────────────────────────────────────────────

_COMPREHENSION_SYSTEM = """Eres un profesor de español. Un estudiante acaba de leer un extracto de un artículo deportivo.
Genera exactamente 3 preguntas de comprensión en español, basadas únicamente en el texto proporcionado.
Pregunta sobre hechos concretos: quién, qué pasó, cuál fue el resultado, por qué ocurrió algo.
Devuelve solo las 3 preguntas, una por línea, sin numeración ni texto adicional."""

_EVALUATION_SYSTEM = """You are a Spanish reading tutor. A student answered comprehension questions about a Spanish sports article.
For each question and answer pair, give exactly one line of feedback in English.
- If the answer is empty or blank: write "No answer given."
- If the answer is correct: confirm what they got right in one sentence.
- If the answer is wrong or incomplete: say what they missed in one sentence.
Do not add any summary, conclusion, or extra lines at the end. One line per question, nothing more."""


async def generate_comprehension_questions(content: str) -> list[str]:
    client = get_client()
    excerpt = content[:3000]
    resp = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": _COMPREHENSION_SYSTEM},
            {"role": "user", "content": excerpt},
        ],
        max_tokens=200,
        temperature=0.4,
    )
    text = (resp.choices[0].message.content or "").strip()
    return [q.strip() for q in text.splitlines() if q.strip()][:3]


async def evaluate_comprehension(content: str, questions: list[str], answers: list[str]) -> str:
    client = get_client()
    excerpt = content[:2000]
    qa = "\n".join(f"Q: {q}\nA: {a}" for q, a in zip(questions, answers))
    resp = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": _EVALUATION_SYSTEM},
            {"role": "user", "content": f"Article excerpt:\n{excerpt}\n\nQ&A:\n{qa}"},
        ],
        max_tokens=250,
        temperature=0.3,
    )
    return (resp.choices[0].message.content or "").strip()


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

_PRODUCTION_SYSTEM = """Eres un tutor de español evaluando si un estudiante ha usado correctamente una palabra o expresión.

Reglas estrictas:
- Solo corrige errores que REALMENTE existen en la frase escrita. No inventes errores.
- Si la frase es correcta, di que está bien y por qué funciona.
- Si hay un error real, cita exactamente lo que escribió el estudiante y explica el problema en una frase.
- Máximo 2 frases. Sin saludos ni preámbulos."""


async def evaluate_production(phrase: str, student_sentence: str) -> str:
    client = get_client()
    resp = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": _PRODUCTION_SYSTEM},
            {"role": "user", "content": f'Expresión a usar: "{phrase}"\nFrase escrita por el estudiante: "{student_sentence}"'},
        ],
        max_tokens=120,
        temperature=0.2,
    )
    return (resp.choices[0].message.content or "").strip()
