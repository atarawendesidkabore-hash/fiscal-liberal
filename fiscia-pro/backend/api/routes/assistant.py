"""AI assistant route placeholder."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from ...services import FiscalContext, LLMRouter

router = APIRouter(prefix="/assistant", tags=["assistant"])


class AssistantInput(BaseModel):
    query: str
    module: str = "assistant"
    is_confidentiel: bool = False


@router.post("/query")
async def ask_assistant(payload: AssistantInput) -> dict:
    llm = LLMRouter()
    resp = await llm.route_query(
        query=payload.query,
        context=FiscalContext(module=payload.module),
        is_confidentiel=payload.is_confidentiel,
    )
    return {"provider": resp.provider, "suggestions": resp.suggestions, "raw": resp.raw}

