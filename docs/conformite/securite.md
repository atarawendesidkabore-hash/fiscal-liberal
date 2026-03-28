# Securite

> Pratiques de securite, architecture de protection et conformite de FiscIA Pro.

---

## Architecture de securite

### Defense en profondeur

FiscIA Pro applique une architecture de securite en couches :

```
Internet
  │
  ├─ TLS 1.3 (chiffrement en transit)
  │
  ├─ Rate limiting (100 req/min par IP)
  │
  ├─ Authentification JWT (tokens signes HS256)
  │
  ├─ Autorisation RBAC (Admin > Fiscaliste > Client)
  │
  ├─ Validation des entrees (Pydantic)
  │
  ├─ ORM parametre (SQLAlchemy — pas de SQL brut)
  │
  └─ Chiffrement au repos (AES-256)
```

## Authentification

### Tokens JWT

| Parametre | Valeur |
|-----------|--------|
| Algorithme | HS256 |
| Duree de vie access token | 30 minutes |
| Duree de vie refresh token | 7 jours |
| Stockage cote client | HttpOnly cookie ou header Authorization |
| Rotation | Automatique au refresh |

### Mots de passe

- **Hachage** : bcrypt avec work factor 12
- **Politique** : minimum 8 caracteres
- **Stockage** : seul le hash est conserve, jamais le mot de passe en clair
- **Tentatives** : blocage temporaire apres 5 echecs consecutifs

### Sessions

- Les tokens sont revoques a la deconnexion
- Tous les tokens d'un utilisateur sont purges lors de la suppression de compte (RGPD Art. 17)
- Pas de sessions persistantes cote serveur (architecture stateless)

## Autorisation (RBAC)

### Roles et permissions

| Permission | Client | Fiscaliste | Admin |
|-----------|--------|------------|-------|
| Calcul IS | Oui | Oui | Oui |
| Liasse 2058-A | Non | Oui | Oui |
| Assistant IA | Non | Oui | Oui |
| Gestion equipe | Non | Non | Oui |
| Audit logs | Non | Non | Oui |
| RGPD admin | Non | Non | Oui |

### Principe du moindre privilege

- Chaque endpoint verifie le role minimum requis
- Les utilisateurs ne voient que leurs propres donnees
- Les admins peuvent voir les donnees de leur cabinet uniquement

## Chiffrement

### En transit

| Composant | Protocole |
|-----------|-----------|
| API publique | TLS 1.3 |
| Communications internes | TLS 1.2+ |
| Webhooks sortants | HTTPS uniquement |

### Au repos

| Donnee | Methode |
|--------|---------|
| Base de donnees | AES-256 (volumes chiffres Scaleway) |
| Sauvegardes | AES-256 |
| Mots de passe | bcrypt (work factor 12) |
| Tokens JWT | Signature HS256, secret en variable d'environnement |

### Gestion des secrets

- Secrets stockes en variables d'environnement (jamais dans le code source)
- Fichier `.env` exclu du depot Git via `.gitignore`
- Rotation du `JWT_SECRET` possible sans interruption de service

## Protection des donnees

### Validation des entrees

Toutes les entrees utilisateur sont validees par Pydantic :

```python
class CalcISInput(BaseModel):
    chiffre_affaires: float = Field(ge=0, le=1_000_000_000_000)
    charges_exploitation: float = Field(ge=0)
    exercice_mois: int = Field(ge=1, le=12, default=12)
```

- Types strictement verifies
- Plages de valeurs controlees
- Rejet immediat des donnees invalides (HTTP 422)

### Prevention des injections

| Vecteur | Protection |
|---------|-----------|
| SQL injection | ORM SQLAlchemy (requetes parametrees) |
| XSS | API JSON uniquement, pas de rendu HTML cote serveur |
| CSRF | Tokens JWT en header (pas de cookies de session) |
| Path traversal | Pas d'acces fichier base sur les entrees utilisateur |

### Rate limiting

| Endpoint | Limite |
|----------|--------|
| API globale | 100 requetes/minute par IP |
| Login | 5 tentatives/minute par IP |
| IA (Ollama) | 10 requetes/minute par utilisateur |
| Export RGPD | 1 requete/heure par utilisateur |

## Infrastructure

### Hebergement

| Composant | Fournisseur | Localisation |
|-----------|-------------|-------------|
| Serveurs applicatifs | Scaleway | Paris, France (DC3) |
| Base de donnees | Scaleway Managed PostgreSQL | Paris, France |
| Sauvegardes | Scaleway Object Storage | Paris, France |

Toutes les donnees sont hebergees en France, conformement aux exigences RGPD.

### Sauvegardes

- **Frequence** : snapshots automatiques toutes les 6 heures
- **Retention** : 30 jours
- **Test de restauration** : mensuel
- **Chiffrement** : AES-256

### Monitoring

- Logs applicatifs structures (JSON)
- Alertes sur erreurs HTTP 5xx
- Monitoring de disponibilite (uptime check toutes les 60s)
- Tableau de bord temps reel (Prometheus + Grafana)

## Securite du developpement

### Pratiques de code

- Revue de code obligatoire avant merge (pull requests)
- Analyse statique automatisee (linting, type checking)
- Tests automatises (unitaires + integration + E2E)
- Pipeline CI/CD avec gates de qualite

### Gestion des dependances

- Dependances pinnees avec versions minimales
- Audit regulier des vulnerabilites connues (`pip audit`)
- Mise a jour proactive des patchs de securite

### Gestion des vulnerabilites

| Severite | Delai de correction |
|----------|-------------------|
| Critique | 24 heures |
| Haute | 72 heures |
| Moyenne | 2 semaines |
| Basse | Prochain sprint |

## Tests de securite

### Tests automatises

- Tests d'authentification (tokens invalides, expires, roles insuffisants)
- Tests d'autorisation (acces inter-cabinets, escalade de privileges)
- Tests de validation (entrees malformees, depassements de limites)
- Tests RGPD (export, suppression, anonymisation)

### Audits

- Audit de securite interne : trimestriel
- Test de penetration externe : annuel
- Scan de vulnerabilites : hebdomadaire (automatise)

## Signalement de vulnerabilites

Si vous decouvrez une faille de securite, contactez-nous de maniere responsable :

- **Email** : security@fiscia.pro
- **Delai de reponse** : 48 heures maximum
- **Politique** : divulgation responsable, pas de poursuites pour les chercheurs de bonne foi

---

## Voir aussi

- [RGPD](gdpr.md) — Conformite RGPD
- [Audit](audit.md) — Pistes d'audit
- [Conformite admin](../administration/conformite.md) — Guide pratique
