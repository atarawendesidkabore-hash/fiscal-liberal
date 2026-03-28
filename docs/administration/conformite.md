# Conformite et RGPD (Admin)

> Guide administrateur pour l'export des donnees, l'audit trail et les rapports de conformite.

**Prerequis** : Role **Admin**

---

## Export des donnees (RGPD Art. 20)

Chaque utilisateur peut exporter l'integralite de ses donnees :

```bash
GET /gdpr/export
Authorization: Bearer <user_token>
```

L'export contient :
- **Profil utilisateur** : email, nom, role, date de creation
- **Consentements** : historique de tous les consentements donnes/revoques
- **Calculs** : tous les calculs sauvegardes avec donnees d'entree et resultats
- **Audit logs** : toutes les actions effectuees par l'utilisateur

Format : JSON structure, facilement convertible en CSV ou Excel.

## Droit a l'effacement (RGPD Art. 17)

Un utilisateur peut demander la suppression de toutes ses donnees :

```bash
DELETE /gdpr/delete-me
Authorization: Bearer <user_token>
```

Cette action :
1. **Supprime** tous les calculs de l'utilisateur
2. **Anonymise** les audit logs (user_id remplace par "DELETED", IP supprimee)
3. **Revoque** tous les consentements actifs
4. **Purge** tous les tokens
5. **Desactive** le compte et supprime les donnees personnelles (email, nom)

> **Irreversible** : cette action ne peut pas etre annulee. Les audit logs anonymises sont conserves pour des raisons de conformite.

## Suivi des consentements

FiscIA Pro trace 3 types de consentements :

| Type | Description | Base legale |
|------|-------------|-------------|
| `data_processing` | Traitement des donnees pour le service | Art. 6.1.b RGPD |
| `marketing` | Communications marketing | Art. 6.1.a RGPD |
| `analytics` | Statistiques d'utilisation | Art. 6.1.a RGPD |

### Enregistrer un consentement

```bash
POST /gdpr/consent
Authorization: Bearer <user_token>
{
  "consent_type": "data_processing",
  "granted": true
}
```

### Lister les consentements actifs

```bash
GET /gdpr/consent
Authorization: Bearer <user_token>
```

## Audit trail

### Acces aux logs

Les Admins accedent a l'ensemble des audit logs du cabinet :

```bash
GET /audit-logs?skip=0&limit=100
Authorization: Bearer <admin_token>
```

Filtres disponibles :
- `user_id` : filtrer par utilisateur
- `action` : filtrer par type d'action (create_liasse, delete_liasse, login)

### Actions tracees

| Action | Module | Description |
|--------|--------|-------------|
| `create_liasse` | liasse | Creation d'un calcul |
| `delete_liasse` | liasse | Suppression d'un calcul |
| `login` | auth | Connexion utilisateur |
| `register` | auth | Inscription |
| `gdpr_export` | gdpr | Export de donnees |
| `gdpr_delete` | gdpr | Suppression de donnees |

## Politique de retention

| Donnee | Duree de conservation | Justification |
|--------|----------------------|---------------|
| Calculs | 3 ans | Obligation comptable minimale |
| Audit logs | 3 ans | Conformite et tracabilite |
| Comptes utilisateurs | Duree du contrat + 3 ans | Obligation legale |
| Logs techniques | 12 mois | Securite |

### Rapport de retention

```bash
GET /gdpr/retention/report
Authorization: Bearer <admin_token>
```

Retourne le nombre de calculs total et le nombre de calculs expirant selon la politique de retention.

### Purge manuelle

```bash
POST /gdpr/retention/purge
Authorization: Bearer <admin_token>
```

Supprime les calculs plus anciens que la periode de retention (3 ans par defaut).

---

## Voir aussi

- [RGPD](../conformite/gdpr.md) — Documentation RGPD complete
- [Securite](../conformite/securite.md) — Pratiques de securite
