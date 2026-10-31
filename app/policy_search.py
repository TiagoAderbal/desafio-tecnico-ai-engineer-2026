import re
import unicodedata

from .settings import DATA_DIR


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.casefold())
    return "".join(ch for ch in text if not unicodedata.combining(ch))


def _sections() -> list[tuple[str, str]]:
    path = DATA_DIR / "politicas.md"
    content = path.read_text(encoding="utf-8")
    chunks = re.split(r"(?m)^## ", content)
    sections = []
    for chunk in chunks:
        if not chunk.strip():
            continue
        title, _, body = chunk.partition("\n")
        sections.append((title.strip(), body.strip()))
    return sections


def search_policy(query: str) -> dict:
    """Busca os tópicos do manual com maior sobreposição lexical."""
    terms = {term for term in normalize(query).split() if len(term) > 2}
    scored = []
    for title, body in _sections():
        haystack = normalize(f"{title} {body}")
        score = sum(1 for term in terms if term in haystack)
        if score:
            scored.append((score, title, body))
    scored.sort(key=lambda item: item[0], reverse=True)
    if not scored:
        return {"found": False, "message": "Nenhum tópico específico foi localizado no manual. Encaminhar à equipe antes de afirmar uma regra."}
    return {
        "found": True,
        "sections": [{"title": title, "content": body[:2400]} for _, title, body in scored[:2]],
    }
