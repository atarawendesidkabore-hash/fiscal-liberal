# API FiscIA Pro — Introduction

> Vue d'ensemble de l'API REST, authentification, rate limits et gestion des erreurs.

**Base URL** : `https://api.fiscia.pro` (production) | `http://localhost:8000` (dev)

**Version** : 3.0

**Format** : JSON

---

## Authentification

L'API utilise des **JWT (JSON Web Tokens)** pour l'authentification.

### Obtenir un token

```bash
# 1. S'inscrire
POST /auth/register
Content-Type: application/json
{
  "email": "jean@cabinet.fr",
  "password": "FiscIA2024!Pro",
  "full_name": "Jean Dupont",
  "firm_name": "Cabinet Dupont",
  "firm_siren": "123456789"
}

# 2. Se connecter
POST /auth/login
Content-Type: application/json
{
  "email": "jean@cabinet.fr",
  "password": "FiscIA2024!Pro"
}

# Reponse:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 900
}
```

### Utiliser le token

Ajoutez le header `Authorization` a chaque requete :

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Duree de vie des tokens

| Token | Duree | Usage |
|-------|-------|-------|
| Access token | 15 minutes | Authentification des requetes |
| Refresh token | 7 jours | Renouvellement de l'access token |

### Renouveler un token

```bash
POST /auth/refresh
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

L'ancien refresh token est automatiquement revoque (rotation).

## Endpoints publics vs authentifies

### Publics (sans token)

| Methode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/health/full` | Health check complet (DB + Ollama) |
| POST | `/auth/register` | Inscription |
| POST | `/auth/login` | Connexion |
| POST | `/search` | Recherche CGI |
| POST | `/calc-is` | Calcul IS simple |
| POST | `/liasse` | Liasse 2058-A (v1, sans auth) |
| POST | `/mere` | Verification mere-filiale |

### Authentifies (v2, token requis)

| Methode | Endpoint | Role minimum | Description |
|---------|----------|-------------|-------------|
| POST | `/v2/liasse` | client | Liasse 2058-A avec sauvegarde |
| GET | `/v2/liasse/saved` | client | Lister ses calculs |
| GET | `/v2/liasse/saved/{id}` | client | Detail d'un calcul |
| DELETE | `/v2/liasse/saved/{id}` | fiscaliste | Supprimer un calcul |
| GET | `/audit-logs` | admin | Consulter les audit logs |
| POST | `/v2/ai/explain` | client | Question IA libre |
| POST | `/v2/ai/explain-is` | client | Explication IS par l'IA |
| POST | `/v2/ai/explain-liasse` | client | Explication liasse par l'IA |
| POST | `/v2/ai/explain-mere` | client | Explication Art. 145 par l'IA |
| GET | `/v2/ai/status` | - | Statut de l'IA (public) |

### GDPR (token requis)

| Methode | Endpoint | Role | Description |
|---------|----------|------|-------------|
| POST | `/gdpr/consent` | client | Enregistrer un consentement |
| GET | `/gdpr/consent` | client | Lister ses consentements |
| GET | `/gdpr/export` | client | Exporter ses donnees |
| DELETE | `/gdpr/delete-me` | client | Supprimer son compte |
| GET | `/gdpr/retention/report` | admin | Rapport de retention |
| POST | `/gdpr/retention/purge` | admin | Purger les donnees expirees |

## Rate limits

| Formule | Requetes/minute | Calculs/mois |
|---------|----------------|--------------|
| Starter | 30 | 50 |
| Pro | 100 | Illimite |
| Cabinet | 300 | Illimite |

En cas de depassement, l'API retourne `429 Too Many Requests`.

## Gestion des erreurs

Toutes les erreurs suivent le format standard :

```json
{
  "detail": "Description de l'erreur en francais"
}
```

### Codes HTTP

| Code | Signification |
|------|---------------|
| 200 | Succes |
| 201 | Cree avec succes |
| 204 | Supprime avec succes |
| 400 | Requete invalide |
| 401 | Non authentifie |
| 403 | Acces refuse (role insuffisant) |
| 404 | Ressource non trouvee |
| 409 | Conflit (email/SIREN deja utilise) |
| 422 | Erreur de validation (champ manquant, guardrail) |
| 429 | Rate limit depasse |
| 503 | Service indisponible (Ollama down, DB down) |

## Monitoring

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check simple |
| `GET /health/database` | Sante de la base de donnees |
| `GET /health/full` | Sante complete (DB + Ollama) |
| `GET /metrics` | Metriques Prometheus |

---

## Voir aussi

- [Auth endpoints](endpoints/auth.md)
- [Calculs endpoints](endpoints/calculs.md)
- [Liasse endpoints](endpoints/liasse.md)
