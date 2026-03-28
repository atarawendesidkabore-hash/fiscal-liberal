# Endpoints d'authentification

> Inscription, connexion, refresh token, deconnexion et profil utilisateur.

**Prefix** : `/auth`

---

## POST /auth/register

Creer un nouveau compte utilisateur.

### Request

```json
{
  "email": "jean@cabinet.fr",
  "password": "FiscIA2024!Pro",
  "full_name": "Jean Dupont",
  "firm_name": "Cabinet Dupont",       // optionnel — cree un cabinet + role admin
  "firm_siren": "123456789"            // optionnel — 9 chiffres exactement
}
```

### Validation

| Champ | Contrainte |
|-------|-----------|
| email | Format email valide, unique |
| password | 8-128 caracteres |
| full_name | 1-200 caracteres |
| firm_name | 1-200 caracteres (optionnel) |
| firm_siren | Exactement 9 caracteres (optionnel) |

### Response (201)

```json
{
  "id": "a1b2c3d4-...",
  "email": "jean@cabinet.fr",
  "full_name": "Jean Dupont",
  "role": "admin",
  "firm_id": "e5f6g7h8-...",
  "is_active": true
}
```

### Erreurs

| Code | Detail |
|------|--------|
| 409 | "Cet email est deja utilise." |
| 409 | "Ce SIREN de cabinet est deja enregistre." |
| 422 | Erreur de validation (champ manquant, format invalide) |

---

## POST /auth/login

Authentifier un utilisateur et obtenir des tokens.

### Request

```json
{
  "email": "jean@cabinet.fr",
  "password": "FiscIA2024!Pro"
}
```

### Response (200)

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 900
}
```

### Erreurs

| Code | Detail |
|------|--------|
| 401 | "Email ou mot de passe incorrect." |
| 403 | "Compte desactive." |

---

## POST /auth/refresh

Echanger un refresh token valide contre une nouvelle paire de tokens.

### Request

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

### Response (200)

Meme format que `/auth/login`.

### Comportement

- L'ancien refresh token est **automatiquement revoque** (rotation de tokens)
- Tenter de reutiliser un ancien refresh token retourne 401

### Erreurs

| Code | Detail |
|------|--------|
| 401 | "Refresh token expire." |
| 401 | "Refresh token invalide." |
| 401 | "Refresh token revoque." |
| 401 | "Utilisateur inactif ou supprime." |

---

## POST /auth/logout

Signaler la deconnexion. Le token expire naturellement.

### Request

Aucun body requis. Token dans le header `Authorization`.

### Response (204)

Pas de body.

---

## GET /auth/me

Obtenir le profil de l'utilisateur authentifie.

### Request

```
Authorization: Bearer <access_token>
```

### Response (200)

```json
{
  "id": "a1b2c3d4-...",
  "email": "jean@cabinet.fr",
  "full_name": null,
  "role": "admin",
  "firm_id": "e5f6g7h8-...",
  "is_active": true
}
```

---

## Structure du JWT

### Access token (payload)

```json
{
  "sub": "user_id",
  "email": "jean@cabinet.fr",
  "role": "admin",
  "firm_id": "e5f6g7h8-...",
  "type": "access",
  "jti": "unique-token-id",
  "exp": 1709123456,
  "iat": 1709122556
}
```

### Refresh token (payload)

```json
{
  "sub": "user_id",
  "type": "refresh",
  "jti": "unique-token-id",
  "exp": 1709727356,
  "iat": 1709122556
}
```

### Algorithme et secret

- Algorithme : **HS256**
- Secret : variable d'environnement `FISCIA_JWT_SECRET`
- Librairie : PyJWT (pas python-jose)

---

## Voir aussi

- [Introduction API](../introduction.md) — Vue d'ensemble
- [Gestion d'equipe](../../administration/gestion-equipe.md) — Roles et permissions
