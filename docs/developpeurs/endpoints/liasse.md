# Endpoints Liasse 2058-A

> Creation, consultation, liste et suppression de calculs de liasse.

---

## POST /liasse (v1, public)

Calculer une liasse 2058-A sans authentification.

### Request

```json
{
  "liasse": {
    "siren": "987654321",
    "exercice_clos": "2024-12-31",
    "benefice_comptable": 120000,
    "perte_comptable": 0,
    "wi_is_comptabilise": 10000,
    "wg_amendes_penalites": 2000,
    "wm_interets_excedentaires": 3000,
    "wn_reintegrations_diverses": 0,
    "wv_regime_mere_filiale": 0,
    "l8_qp_12pct": 0
  },
  "ca": 5000000,
  "capital_pp": true
}
```

### Parametres query

| Param | Type | Description |
|-------|------|-------------|
| `save` | bool | Sauvegarder le calcul en base (defaut: false) |
| `user_id` | string | ID utilisateur pour la sauvegarde (v1 uniquement) |

### Response (200)

```json
{
  "rf_brut": 135000.0,
  "rf_net": 135000.0,
  "is_total": 29500.0,
  "regime": "PME taux reduit (Art. 219-I-b)",
  "acompte_trimestriel": 7375.0,
  "details": {
    "benefice_comptable": 120000.0,
    "wi_reintegration": 10000.0,
    "wg_reintegration": 2000.0,
    "wm_reintegration": 3000.0,
    "wv_deduction": 0.0
  },
  "disclaimer": "Reponse indicative...",
  "saved_id": "a1b2c3d4-..."  // present seulement si save=true
}
```

### Schema de la liasse

| Champ | Type | Obligatoire | Description |
|-------|------|-------------|-------------|
| siren | string(9) | Oui | SIREN de l'entreprise |
| exercice_clos | string | Oui | Date YYYY-MM-DD |
| benefice_comptable | decimal | Non | Ligne XN (defaut: 0) |
| perte_comptable | decimal | Non | Ligne XN si deficit (defaut: 0) |
| wi_is_comptabilise | decimal | Non | IS en charges (defaut: 0) |
| wg_amendes_penalites | decimal | Non | Amendes (defaut: 0) |
| wm_interets_excedentaires | decimal | Non | Interets CC (defaut: 0) |
| wn_reintegrations_diverses | decimal | Non | Alias: wn_gain_change_qp5 |
| wv_regime_mere_filiale | decimal | Non | Dividendes exoneres (defaut: 0) |
| l8_qp_12pct | decimal | Non | QP 12% PV LT (defaut: 0) |

---

## POST /v2/liasse (auth requise)

Meme fonctionnalite que v1, mais :
- Authentification JWT obligatoire
- Le `user_id` est extrait du token (pas de parametre query)
- Sauvegarde liee au compte authentifie

```bash
POST /v2/liasse?save=true
Authorization: Bearer <token>
Content-Type: application/json
{ ... meme body que v1 ... }
```

---

## GET /v2/liasse/saved

Lister les calculs sauvegardes de l'utilisateur authentifie.

### Parametres query

| Param | Type | Description |
|-------|------|-------------|
| siren | string | Filtrer par SIREN |
| skip | int | Offset (defaut: 0) |
| limit | int | Limite 1-500 (defaut: 100) |

### Response (200)

```json
{
  "count": 3,
  "results": [
    {
      "id": "a1b2c3d4-...",
      "siren": "987654321",
      "exercice_clos": "2024-12-31",
      "rf_brut": 135000.0,
      "rf_net": 135000.0,
      "is_total": 29500.0,
      "regime": "PME taux reduit (Art. 219-I-b)",
      "created_at": "2024-12-15T10:30:00+00:00"
    }
  ],
  "disclaimer": "..."
}
```

---

## GET /v2/liasse/saved/{id}

Detail complet d'un calcul sauvegarde.

### Response (200)

```json
{
  "id": "a1b2c3d4-...",
  "user_id": "e5f6g7h8-...",
  "siren": "987654321",
  "exercice_clos": "2024-12-31",
  "input_data": { ... donnees saisies ... },
  "result_data": { ... resultat complet ... },
  "created_at": "2024-12-15T10:30:00+00:00",
  "updated_at": "2024-12-15T10:30:00+00:00",
  "disclaimer": "..."
}
```

### Erreurs

| Code | Detail |
|------|--------|
| 404 | "Calcul non trouve." |

---

## DELETE /v2/liasse/saved/{id}

Supprimer un calcul sauvegarde. **Role fiscaliste+ requis.**

### Response (200)

```json
{
  "deleted": true,
  "id": "a1b2c3d4-...",
  "disclaimer": "..."
}
```

### Erreurs

| Code | Detail |
|------|--------|
| 403 | Role insuffisant (client ne peut pas supprimer) |
| 404 | "Calcul non trouve." |

---

## Voir aussi

- [Calculs endpoints](calculs.md) — IS, CGI, mere-filiale
- [Guide liasse](../../utilisateurs/liasse-2058a.md) — Guide utilisateur
