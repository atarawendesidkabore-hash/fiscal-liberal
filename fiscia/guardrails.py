"""
Matrice de guardrails fiscaux - 5 regles de securite minimum.
"""
import re


class GuardrailError(RuntimeError):
    pass


def enforce_guardrails(answer: str, context: dict) -> str:
    """
    Valide une reponse IA/calcul contre les guardrails fiscaux.
    Leve GuardrailError si une regle est violee.
    Retourne la reponse inchangee si tout est conforme.
    """

    # G001 - IS amount present -> PME check must have been done
    if re.search(r"IS\s+[\d\s]+[.,]?\d*\s*(?:EUR|€)", answer, re.IGNORECASE):
        if not context.get("pme_checked", False):
            raise GuardrailError(
                "G001: Un montant d'IS est present mais la verification PME "
                "(Art. 219-I-b CGI) n'a pas ete effectuee."
            )

    # G002 - WV or WN mentioned -> mere-filiale conditions must be present
    if re.search(r"\bW[VN]\b", answer):
        if not context.get("mere_conditions_present", False):
            raise GuardrailError(
                "G002: Les lignes WV/WN sont mentionnees sans verification "
                "des 6 conditions Art. 145 CGI."
            )

    # G003 - Confidential context -> no external URLs
    if context.get("confidential", False):
        if re.search(r"https?://", answer):
            raise GuardrailError(
                "G003: La reponse contient une URL externe alors que le "
                "contexte est confidentiel. Aucune donnee ne doit quitter "
                "le serveur local."
            )

    # G004 - Every cited article must include a version string
    art_mentions = re.findall(r"Art\.\s*\d+[A-Za-z\s\-]*CGI", answer)
    if art_mentions:
        version_patterns = ["LFI 20", "LFR 20", "LFI 19", "LFR 19"]
        has_version = any(v in answer for v in version_patterns)
        if not has_version:
            raise GuardrailError(
                "G004: Des articles CGI sont cites sans indication de la "
                "version applicable (ex: 'LFI 2024'). Chaque article doit "
                "specifier sa version."
            )

    # G005 - Mandatory disclaimer
    if "disclaimer" not in answer.lower() and "indicati" not in answer.lower():
        raise GuardrailError(
            "G005: Le disclaimer obligatoire est absent de la reponse. "
            "Chaque reponse fiscale doit inclure l'avertissement professionnel."
        )

    return answer
