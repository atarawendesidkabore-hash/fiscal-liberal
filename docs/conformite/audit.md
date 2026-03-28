# Audit et tracabilite

> Pistes d'audit, retention des donnees et reporting de conformite.

---

## Vue d'ensemble

FiscIA Pro enregistre automatiquement toutes les actions significatives dans un journal d'audit immutable. Ce journal permet :

- La **tracabilite** de toutes les operations fiscales
- La **conformite** avec les obligations legales et reglementaires
- Le **diagnostic** en cas d'incident ou de litige
- L'**analyse** des usages pour l'amelioration du service

## Actions tracees

### Module Authentification

| Action | Declencheur | Donnees enregistrees |
|--------|-------------|---------------------|
| `login` | Connexion reussie | user_id, IP, user-agent |
| `login_failed` | Echec de connexion | email tente, IP |
| `register` | Inscription | user_id, email, role |
| `logout` | Deconnexion | user_id |
| `token_refresh` | Renouvellement de token | user_id |

### Module Calculs

| Action | Declencheur | Donnees enregistrees |
|--------|-------------|---------------------|
| `create_liasse` | Nouveau calcul IS / liasse | user_id, liasse_id, parametres |
| `delete_liasse` | Suppression d'un calcul | user_id, liasse_id |
| `ai_query` | Question a l'assistant IA | user_id, mode, prompt (tronque) |

### Module RGPD

| Action | Declencheur | Donnees enregistrees |
|--------|-------------|---------------------|
| `gdpr_export` | Export de donnees (Art. 20) | user_id |
| `gdpr_delete` | Suppression de compte (Art. 17) | user_id (anonymise apres) |
| `consent_granted` | Consentement donne | user_id, consent_type |
| `consent_revoked` | Consentement retire | user_id, consent_type |

### Module Administration

| Action | Declencheur | Donnees enregistrees |
|--------|-------------|---------------------|
| `user_invited` | Invitation d'un membre | admin_id, email invite |
| `user_removed` | Suppression d'un membre | admin_id, user_id supprime |
| `role_changed` | Changement de role | admin_id, user_id, ancien/nouveau role |
| `retention_purge` | Purge de retention | admin_id, nombre de calculs supprimes |

## Structure d'un enregistrement d'audit

Chaque entree du journal contient :

```json
{
  "id": "a1b2c3d4-...",
  "user_id": "u5e6f7g8-...",
  "action": "create_liasse",
  "module": "liasse",
  "detail": "Calcul IS PME - CA 500000 EUR",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0 ...",
  "created_at": "2025-03-15T14:30:00Z"
}
```

### Champs

| Champ | Type | Description |
|-------|------|-------------|
| `id` | UUID v4 | Identifiant unique de l'entree |
| `user_id` | UUID v4 | Utilisateur ayant effectue l'action |
| `action` | String | Code de l'action (voir tableaux ci-dessus) |
| `module` | String | Module source (auth, liasse, gdpr, admin) |
| `detail` | String | Description lisible de l'action |
| `ip_address` | String | Adresse IP du client |
| `user_agent` | String | Navigateur ou client API |
| `created_at` | DateTime (UTC) | Horodatage de l'action |

## Consultation des logs

### Pour les administrateurs

```bash
GET /audit-logs?skip=0&limit=100
Authorization: Bearer <admin_token>
```

### Filtres disponibles

| Parametre | Type | Description |
|-----------|------|-------------|
| `user_id` | UUID | Filtrer par utilisateur |
| `action` | String | Filtrer par type d'action |
| `skip` | Integer | Pagination (offset) |
| `limit` | Integer | Nombre de resultats (max 100) |

### Exemple de reponse

```json
{
  "logs": [
    {
      "id": "a1b2c3d4-...",
      "user_id": "u5e6f7g8-...",
      "action": "create_liasse",
      "module": "liasse",
      "detail": "Calcul IS PME",
      "ip_address": "192.168.1.100",
      "created_at": "2025-03-15T14:30:00Z"
    }
  ],
  "total": 1247,
  "skip": 0,
  "limit": 100
}
```

## Retention des donnees

### Politique de retention

| Type de donnee | Duree de conservation | Base legale |
|----------------|----------------------|-------------|
| Audit logs | 3 ans | Obligation de tracabilite comptable |
| Calculs IS | 3 ans | Prescription fiscale (Art. L169 LPF) |
| Comptes utilisateurs | Duree contrat + 3 ans | Execution du contrat |
| Logs techniques (IP, user-agent) | 12 mois | Interet legitime (securite) |
| Consentements RGPD | 5 ans | Preuve de conformite |

### Rapport de retention

Les administrateurs peuvent generer un rapport de retention :

```bash
GET /gdpr/retention/report
Authorization: Bearer <admin_token>
```

Reponse :

```json
{
  "total_calculations": 1523,
  "expired_calculations": 47,
  "retention_days": 1095,
  "cutoff_date": "2022-03-15T00:00:00Z"
}
```

### Purge automatique

La purge des donnees expirees peut etre declenchee manuellement :

```bash
POST /gdpr/retention/purge
Authorization: Bearer <admin_token>
```

Cette action :
1. Identifie les calculs plus anciens que la periode de retention (3 ans)
2. Supprime ces calculs de la base de donnees
3. Enregistre l'action dans le journal d'audit (`retention_purge`)
4. Retourne le nombre de calculs supprimes

> **Recommandation** : programmez une purge trimestrielle pour maintenir la conformite.

## Anonymisation

Lors de la suppression d'un compte utilisateur (RGPD Art. 17), les audit logs sont **anonymises** et non supprimes :

| Champ | Avant | Apres |
|-------|-------|-------|
| `user_id` | `u5e6f7g8-...` | `DELETED` |
| `ip_address` | `192.168.1.100` | `null` |
| `user_agent` | `Mozilla/5.0 ...` | `null` |
| `action` | Inchange | Inchange |
| `detail` | Inchange | Inchange |
| `created_at` | Inchange | Inchange |

Cette approche preserve la tracabilite des actions tout en respectant le droit a l'effacement.

## Immutabilite

Les enregistrements d'audit sont **append-only** :

- Aucune modification possible apres creation
- Aucune suppression individuelle (sauf anonymisation RGPD)
- L'horodatage est genere cote serveur (non modifiable par le client)
- Les identifiants sont des UUID v4 non sequentiels

## Reporting de conformite

### Export des logs

Les audit logs sont inclus dans l'export RGPD (`GET /gdpr/export`) pour chaque utilisateur.

### Indicateurs cles

Pour un reporting de conformite, surveillez :

| Indicateur | Seuil d'alerte | Action |
|-----------|----------------|--------|
| Echecs de connexion | > 10/heure par IP | Verifier tentative de brute-force |
| Suppressions de compte | > 5/jour | Verifier satisfaction utilisateur |
| Exports RGPD | > 3/jour par utilisateur | Verifier usage abusif |
| Purges de retention | 0 en 6 mois | Planifier une purge |

---

## Voir aussi

- [RGPD](gdpr.md) — Conformite RGPD complete
- [Securite](securite.md) — Pratiques de securite
- [Conformite admin](../administration/conformite.md) — Guide pratique
