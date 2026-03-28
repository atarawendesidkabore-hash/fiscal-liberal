# Gestion d'equipe

> Ajouter et gerer les membres de votre cabinet dans FiscIA Pro.

**Prerequis** : Role **Admin** (obtenu en creant un cabinet lors de l'inscription)

---

## Roles disponibles

| Role | Niveau | Permissions |
|------|--------|-------------|
| **Admin** | 3 | Tout : gestion equipe, facturation, audit logs, suppression |
| **Fiscaliste** | 2 | Calculs, sauvegarde, suppression de ses propres calculs |
| **Client** | 1 | Calculs, consultation, sauvegarde (lecture seule sur les calculs des autres) |

La hierarchie est cumulative : un Admin a toutes les permissions d'un Fiscaliste, qui a toutes celles d'un Client.

## Ajouter un membre

1. L'utilisateur s'inscrit sur `https://app.fiscia.pro/register` **sans** fournir de nom de cabinet
2. L'Admin associe l'utilisateur au cabinet via l'API :

```bash
# Assigner un utilisateur a votre cabinet (API Admin)
PATCH /v2/users/{user_id}
Authorization: Bearer <admin_token>
{
  "firm_id": "<votre_firm_id>",
  "role": "fiscaliste"
}
```

## Modifier le role d'un membre

Seul un Admin peut modifier les roles :

```bash
PATCH /v2/users/{user_id}
Authorization: Bearer <admin_token>
{
  "role": "admin"  # ou "fiscaliste" ou "client"
}
```

## Desactiver un compte

Pour suspendre l'acces d'un membre sans supprimer ses donnees :

```bash
PATCH /v2/users/{user_id}
Authorization: Bearer <admin_token>
{
  "is_active": false
}
```

L'utilisateur ne pourra plus se connecter. Ses calculs restent accessibles aux autres membres du cabinet.

## Monitoring d'activite

### Audit logs

Les Admins ont acces aux journaux d'audit de tous les membres :

```bash
GET /audit-logs?user_id={user_id}&action=create_liasse
Authorization: Bearer <admin_token>
```

Chaque entree contient :
- `user_id` : qui a effectue l'action
- `action` : type d'operation (create_liasse, delete_liasse, login, etc.)
- `module` : composant concerne (liasse, auth, gdpr)
- `siren` : SIREN concerne (si applicable)
- `ip_address` : adresse IP de l'utilisateur
- `created_at` : horodatage precis

### Isolation des donnees

Les calculs sont isoles par `user_id`. Un utilisateur ne peut voir que ses propres calculs via les endpoints v2 (qui utilisent le JWT pour filtrer).

Les Admins peuvent acceder aux audit logs de tous les membres du cabinet.

---

## Voir aussi

- [Conformite](conformite.md) — Export GDPR et audit trail
- [API : Auth endpoints](../developpeurs/endpoints/auth.md) — Documentation technique
