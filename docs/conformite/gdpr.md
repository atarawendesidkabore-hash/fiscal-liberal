# Conformite RGPD

> Documentation complete sur la conformite RGPD de FiscIA Pro.

---

## Engagement RGPD

FiscIA Pro est conforme au Reglement General sur la Protection des Donnees (UE 2016/679). Ce document decrit nos pratiques, vos droits et les mecanismes mis en place.

## Roles et responsabilites

| Entite | Role RGPD | Description |
|--------|-----------|-------------|
| FiscIA Pro SAS | Sous-traitant (Art. 28) | Traite les donnees pour le compte du cabinet |
| Cabinet client | Responsable de traitement (Art. 24) | Determine les finalites du traitement |
| Scaleway SAS | Sous-traitant secondaire | Hebergement infrastructure |

## Donnees traitees

### Donnees personnelles

| Categorie | Donnees | Base legale | Retention |
|-----------|---------|-------------|-----------|
| Identification | Email, nom, prenom | Execution du contrat (6.1.b) | Duree contrat + 3 ans |
| Authentification | Hash bcrypt du mot de passe | Execution du contrat (6.1.b) | Duree contrat |
| Connexion | Adresse IP, user-agent | Interet legitime (6.1.f) | 12 mois |
| Consentements | Type, date, statut | Obligation legale (6.1.c) | 5 ans |

### Donnees metiers

| Categorie | Donnees | Base legale | Retention |
|-----------|---------|-------------|-----------|
| Calculs IS | SIREN, liasse, resultats | Execution du contrat (6.1.b) | 3 ans |
| Audit trail | Actions, horodatage | Interet legitime (6.1.f) | 3 ans |

## Droits des personnes concernees

FiscIA Pro implemente les droits RGPD via l'API et l'interface :

| Droit | Article | Implementation |
|-------|---------|----------------|
| Acces | Art. 15 | `GET /gdpr/export` |
| Rectification | Art. 16 | `PATCH /auth/me` (a venir) |
| Effacement | Art. 17 | `DELETE /gdpr/delete-me` |
| Portabilite | Art. 20 | `GET /gdpr/export` (JSON structure) |
| Opposition | Art. 21 | `POST /gdpr/consent` (revocation) |
| Limitation | Art. 18 | Contact DPO |

### Delais de reponse

- Demande standard : **30 jours maximum** (Art. 12.3)
- Demande complexe : extensible a 60 jours avec notification
- Demande via API : **immediat** (automatise)

## Mesures techniques

### Chiffrement

| Niveau | Methode |
|--------|---------|
| En transit | TLS 1.3 |
| Au repos | AES-256 (disques Scaleway) |
| Mots de passe | bcrypt (work factor 12) |
| Tokens | JWT HS256, rotation automatique |

### Minimisation

- Seules les donnees strictement necessaires sont collectees
- Pas de tracking publicitaire
- Pas de cookies tiers sans consentement explicite
- Anonymisation des audit logs lors de la suppression d'un compte

### Pseudonymisation

- Les calculs sont identifies par UUID, pas par nom
- Les audit logs peuvent etre anonymises (user_id → "DELETED")

## Accord de traitement des donnees (DPA)

Un DPA conforme a l'Art. 28 RGPD est disponible sur demande pour les clients de la formule Cabinet. Il couvre :

- Description du traitement
- Obligations du sous-traitant
- Mesures de securite techniques et organisationnelles
- Sous-traitants secondaires (Scaleway)
- Clause de notification de violation (72h)
- Assistance au responsable de traitement

Contact : dpo@fiscia.pro

## Violation de donnees

En cas de violation de donnees (Art. 33-34) :

1. **Notification CNIL** : sous 72 heures
2. **Notification clients** : si risque eleve pour les droits des personnes
3. **Documentation** : registre de violations maintenu en interne

## DPO

Delegue a la protection des donnees :

- Email : dpo@fiscia.pro
- Adresse : FiscIA Pro SAS, 42 rue de la Boetie, 75008 Paris

---

## Voir aussi

- [Securite](securite.md) — Pratiques de securite
- [Audit](audit.md) — Pistes d'audit
- [Conformite admin](../administration/conformite.md) — Guide pratique
