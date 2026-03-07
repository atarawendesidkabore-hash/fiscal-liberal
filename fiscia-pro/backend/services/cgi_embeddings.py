"""CGI embeddings service placeholder."""

from __future__ import annotations


class CGIEmbeddingsService:
    def build_embedding(self, article_text: str) -> list[float]:
        # Deterministic lightweight placeholder until model integration.
        return [float(len(article_text) % 100) / 100.0]

