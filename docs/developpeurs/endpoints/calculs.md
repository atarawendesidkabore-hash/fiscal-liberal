# Endpoints de calcul

> Calcul IS, recherche CGI, verification mere-filiale et assistant IA.

---

## POST /calc-is

Calcul IS simple a partir d'un resultat fiscal fixe de 100 000 EUR.

### Request

```json
{
  "ca": 5000000,
  "capital_pp": true
}
```

### Response (200)

```json
{
  "rf": 100000,
  "regime": "PME taux reduit (Art. 219-I-b)",
  "tranche_15pct": 6375.0,
  "tranche_25pct": 14375.0,
  "is_total": 20750.0,
  "acompte_trimestriel": 5187.5,
  "disclaimer": "Reponse indicative..."
}
```

---

## POST /search

Recherche d'articles dans le Code General des Impots.

### Request

```json
{
  "query": "taux reduit PME"
}
```

### Response (200)

```json
{
  "results": [
    {
      "article": "219",
      "title": "Taux de l'impot sur les societes",
      "text": "...",
      "score": 0.85
    }
  ],
  "disclaimer": "..."
}
```

### Erreurs

| Code | Detail |
|------|--------|
| 404 | "Aucun article trouve." |

---

## POST /mere

Verification des conditions du regime mere-filiale (Art. 145 CGI).

### Request

```json
{
  "pct_capital": 7.0,
  "annees_detention": 3,
  "nominatif": true,
  "pleine_propriete": true,
  "filiale_is": true,
  "paradis_fiscal": false,
  "dividende_brut": 50000,
  "credit_impot": 0
}
```

### Response (200)

```json
{
  "eligible": true,
  "conditions": {
    "pct_capital": true,
    "annees_detention": true,
    "nominatifs": true,
    "pleine_propriete": true,
    "filiale_is": true,
    "paradis_fiscal": true
  },
  "deduction_wv": 50000.0,
  "reintegration_wn_qp5": 2500.0,
  "impact_rf": -47500.0,
  "disclaimer": "..."
}
```

---

## AI Endpoints

### GET /v2/ai/status

Verifier la disponibilite de l'assistant IA (public, sans auth).

```json
{
  "available": true,
  "model": "fiscia-fiscal-is-v3"
}
```

### POST /v2/ai/explain

Question IA en langage libre. **Auth requise.**

```json
{
  "prompt": "Comment traiter les dividendes mere-filiale ?",
  "mode": "mere",          // is | liasse | mere | general
  "temperature": 0.05      // 0.0-1.0 (default 0.05)
}
```

**Validation** : `prompt` de 10 a 5000 caracteres, `mode` parmi les 4 valeurs.

### Response (200)

```json
{
  "response": "Les dividendes mere-filiale beneficient d'une exoneration...",
  "model": "fiscia-fiscal-is-v3",
  "mode": "mere",
  "elapsed_ms": 2340,
  "tokens_evaluated": 150,
  "tokens_generated": 80,
  "disclaimer": "Reponse indicative generee par IA locale. Validation professionnelle requise."
}
```

### POST /v2/ai/explain-is

Explication IS detaillee. Envoie automatiquement un prompt structure au modele.

```json
{
  "ca": 5000000,
  "capital_pp": true
}
```

### POST /v2/ai/explain-liasse

Explication liasse 2058-A detaillee. Meme schema que `POST /liasse`.

### POST /v2/ai/explain-mere

Explication Art. 145 detaillee. Meme schema que `POST /mere`.

### Erreurs AI

| Code | Detail |
|------|--------|
| 401 | Non authentifie |
| 422 | Prompt trop court (< 10 caracteres) |
| 503 | "Ollama non accessible" |
| 504 | "Ollama timeout" |

---

## Voir aussi

- [Liasse endpoints](liasse.md) — CRUD liasse 2058-A
- [Auth endpoints](auth.md) — Authentification
