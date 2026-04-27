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

DEFINICION: [definition in Spanish, max 1 sentence] / [same definition in English, max 1 sentence]
TRADUCCION: [English translation, 1-5 words]
CATEGORIA: [one of: subjuntivo, verbo reflexivo, expresion idiomatica, vocabulario futbol, locucion prepositiva, vocabulario periodistico, falso amigo, otro]"""

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


# ── Comprehension ─────────────────────────────────────────────────────────────

_COMPREHENSION_SYSTEM = (
    "Eres un profesor de espanol. Un estudiante acaba de leer un extracto de un articulo deportivo.\n"
    "Genera exactamente 3 preguntas de comprension en espanol, basadas unicamente en el texto proporcionado.\n"
    "Pregunta sobre hechos concretos: quien, que paso, cual fue el resultado, por que ocurrio algo.\n\n"
    "Para cada pregunta, incluye tambien un inicio de frase en espanol (3-6 palabras) que ayude al "
    "estudiante a empezar su respuesta.\n\n"
    "Formato exacto, sin texto adicional:\n"
    "P: [pregunta]\n"
    "I: [inicio de frase]\n"
    "P: [pregunta]\n"
    "I: [inicio de frase]\n"
    "P: [pregunta]\n"
    "I: [inicio de frase]"
)

_EVALUATION_SYSTEM = (
    "You are a Spanish reading tutor. A student answered comprehension questions about a Spanish sports article.\n"
    "For each question and answer pair, give exactly one line of feedback in English.\n"
    "- If the answer is empty or blank: write \"No answer given.\"\n"
    "- If the answer is correct: confirm what they got right in one sentence.\n"
    "- If the answer is wrong or incomplete: say what they missed in one sentence.\n"
    "Do not add any summary, conclusion, or extra lines at the end. One line per question, nothing more."
)


async def generate_comprehension_questions(content: str) -> dict:
    client = get_client()
    excerpt = content[:3000]
    resp = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": _COMPREHENSION_SYSTEM},
            {"role": "user", "content": excerpt},
        ],
        max_tokens=300,
        temperature=0.4,
    )
    text = (resp.choices[0].message.content or "").strip()
    questions, starters = [], []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("P:"):
            questions.append(line[2:].strip())
        elif line.startswith("I:"):
            starters.append(line[2:].strip())
    return {"questions": questions[:3], "starters": starters[:3]}


async def evaluate_comprehension(content: str, questions: list[str], answers: list[str]) -> str:
    client = get_client()
    excerpt = content[:2000]
    qa = "\n".join(f"Q: {q}\nA: {a if a.strip() else '[no answer]'}" for q, a in zip(questions, answers))
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


# ── TPRS Narrative ────────────────────────────────────────────────────────────

_NARRATIVE_SYSTEM = (
    "Eres un profesor de espanol creando ejercicios de lectura para estudiantes de nivel A2-B1.\n"
    "Dado el titular y resumen de una noticia deportiva, escribe una micro-narrativa TPRS de 3-5 frases:\n"
    "- Tiempo presente simple\n"
    "- Vocabulario nivel A2-B1\n"
    "- Incluye quien, que paso, resultado\n"
    "- Solo en espanol, sin traducciones ni explicaciones\n"
    "- Sin titulo, solo el texto narrativo"
)


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

_PRODUCTION_SYSTEM = (
    "Eres un tutor de espanol evaluando si un estudiante ha usado correctamente una palabra o expresion.\n\n"
    "Reglas estrictas:\n"
    "- Solo corrige errores que REALMENTE existen en la frase escrita. No inventes errores.\n"
    "- Si la frase es correcta, di que esta bien y por que funciona.\n"
    "- Si hay un error real, cita exactamente lo que escribio el estudiante y explica el problema en una frase.\n"
    "- Maximo 2 frases. Sin saludos ni preambulos."
)


async def evaluate_production(phrase: str, student_sentence: str) -> str:
    client = get_client()
    resp = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": _PRODUCTION_SYSTEM},
            {"role": "user", "content": f'Expresion a usar: "{phrase}"\nFrase escrita por el estudiante: "{student_sentence}"'},
        ],
        max_tokens=120,
        temperature=0.2,
    )
    return (resp.choices[0].message.content or "").strip()
