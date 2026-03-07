from __future__ import annotations

import json
import re
from difflib import SequenceMatcher
from functools import lru_cache
from pathlib import Path


def _norm(txt: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", txt.lower()).strip()


@lru_cache(maxsize=1)
def _load_articles() -> list[dict]:
    path = Path(__file__).resolve().parents[1] / "data" / "cgi_articles.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def search(query: str, top_n: int = 5) -> list[dict]:
    q = _norm(query)
    rows = []
    for article in _load_articles():
        corpus = _norm(f"{article.get('article','')} {article.get('title','')} {article.get('text','')}")
        score = SequenceMatcher(None, q, corpus).ratio()
        rows.append(
            {
                "article": article.get("article"),
                "title": article.get("title"),
                "excerpt": article.get("text", "")[:180],
                "version": article.get("version"),
                "score": round(score, 6),
            }
        )
    rows.sort(key=lambda x: x["score"], reverse=True)
    return rows[: max(top_n, 1)]

