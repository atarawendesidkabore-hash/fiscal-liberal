"""LLM routing layer: local-first with cloud fallback contract."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class FiscalContext:
    module: str


@dataclass(slots=True)
class LLMResponse:
    provider: str
    suggestions: list[str] = field(default_factory=list)
    raw: str = ""


class LLMRouter:
    """
    Placeholder router implementing local-first policy.
    In production this routes between Ollama local and Claude API.
    """

    async def route_query(self, query: str, context: FiscalContext, is_confidentiel: bool) -> LLMResponse:
        provider = "ollama_local" if is_confidentiel else "cloud_fallback"
        suggestions = [
            f"Module {context.module}: verifier coherence WI/WG/WV/WM/WN et ligne L8.",
            "Verifier les conditions PME avant validation du taux reduit 15%.",
        ]
        return LLMResponse(provider=provider, suggestions=suggestions, raw=query[:280])

