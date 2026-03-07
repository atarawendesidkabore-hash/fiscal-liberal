from __future__ import annotations

import re


class GuardrailError(RuntimeError):
    pass


MANDATORY_DISCLAIMER = (
    "⚖️ Disclaimer : la présente réponse est fournie à titre indicatif sur la base des informations communiquées.\n"
    "Elle ne constitue pas un avis fiscal engageant la responsabilité du cabinet.\n"
    "Toute décision doit faire l’objet d’une analyse personnalisée d’un professionnel qualifié."
)


def enforce_guardrails(answer: str, context: dict) -> str:
    if re.search(r"\bIS\b", answer, flags=re.IGNORECASE) and re.search(
        r"\d[\d\s.,]*\s*(€|eur)", answer, flags=re.IGNORECASE
    ):
        if not context.get("pme_checked", False):
            raise GuardrailError("G001: IS detecte sans verification PME.")

    if ("WV" in answer or "WN" in answer) and not context.get("mere_conditions_present", False):
        raise GuardrailError("G002: WV/WN mentionne sans verification des conditions mere-filiale.")

    if context.get("confidential", False) and re.search(r"https?://|www\.", answer, flags=re.IGNORECASE):
        raise GuardrailError("G003: URL interdite en contexte confidentiel.")

    for match in re.finditer(r"Art\.\s*[^,\n;.]+", answer):
        chunk = answer[match.start() : min(len(answer), match.end() + 80)]
        if "LFI" not in chunk and "LFR" not in chunk:
            raise GuardrailError(f"G004: version manquante pour reference article: {match.group(0)}")

    if MANDATORY_DISCLAIMER not in answer:
        raise GuardrailError("G005: disclaimer obligatoire absent.")

    return answer

