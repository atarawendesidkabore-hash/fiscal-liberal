"""CGI semantic search placeholder route."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from ...services.cgi_embeddings import CGIEmbeddingsService

router = APIRouter(prefix="/recherche-cgi", tags=["recherche_cgi"])


class SearchInput(BaseModel):
    query: str


@router.post("")
async def recherche_cgi(payload: SearchInput) -> dict:
    service = CGIEmbeddingsService()
    vector = service.build_embedding(payload.query)
    return {
        "query": payload.query,
        "embedding_preview": vector,
        "results": [],
        "message": "Endpoint scaffolded. Connect pgvector retrieval in next sprint.",
    }

