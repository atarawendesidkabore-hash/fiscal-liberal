"""
Recherche simple dans le catalogue CGI (difflib.SequenceMatcher).
"""
import json
import re
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List

_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "cgi_articles.json"
_ARTICLES: List[Dict] = []


def _load() -> List[Dict]:
    global _ARTICLES
    if not _ARTICLES:
        with open(_DATA_PATH, encoding="utf-8") as f:
            _ARTICLES = json.load(f)
    return _ARTICLES


def _norm(txt: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", txt.lower())


def search(query: str, top_n: int = 5) -> List[Dict]:
    """
    Retourne les top_n articles CGI les plus proches de la requete.
    Chaque entree contient: article, title, excerpt, version, score.
    """
    articles = _load()
    q = _norm(query)
    scored = []

    for art in articles:
        corpus = _norm(f"{art['article']} {art['title']} {art['text']}")
        ratio = SequenceMatcher(None, q, corpus).ratio()
        scored.append((ratio, art))

    scored.sort(key=lambda x: x[0], reverse=True)

    results = []
    for score, art in scored[:top_n]:
        results.append({
            "article": art["article"],
            "title": art["title"],
            "excerpt": art["text"][:200] + ("..." if len(art["text"]) > 200 else ""),
            "version": art["version"],
            "score": round(score, 4),
        })

    return results
