# Gestion de la facturation (Admin)

> Guide administrateur pour la gestion des paiements, factures et abonnements.

**Prerequis** : Role **Admin**

---

## Moyens de paiement acceptes

| Moyen | Disponibilite | Detail |
|-------|--------------|--------|
| Carte bancaire | Toutes formules | Visa, Mastercard, CB |
| Prelevement SEPA | Annuel uniquement | Mandat SEPA en ligne |
| Virement bancaire | Cabinet sur devis | RIB fourni sur demande |

## Historique des factures

Toutes les factures sont accessibles dans **Parametres > Facturation** :

- Format PDF avec mentions legales completes
- TVA a 20% (France metropolitaine)
- Numerotation sequentielle conforme
- Envoi automatique par email le 1er du mois

## Changement de formule

| Transition | Prise d'effet | Prorata |
|-----------|---------------|---------|
| Starter → Pro | Immediat | Oui (credit au prorata) |
| Pro → Cabinet | Immediat | Oui |
| Cabinet → Pro | Prochaine facturation | Non |
| Pro → Starter | Prochaine facturation | Non |

> **Attention** : Un downgrade peut entrainer la perte d'acces a certaines fonctionnalites (IA, API, multi-cabinet). Les donnees restent accessibles en lecture seule.

## Formule annuelle

- Paiement de 10 mois pour 12 mois d'utilisation (-17%)
- Facturation en une seule fois
- Non remboursable au prorata (engagement 12 mois)
- Renouvellement automatique sauf resiliation 30 jours avant

## Gestion multi-cabinet (formule Cabinet)

La formule Cabinet permet de gerer plusieurs entites juridiques sous un meme compte :

- Chaque cabinet a son propre SIREN et ses propres utilisateurs
- La facturation est centralisee sur un seul compte payeur
- Les donnees sont isolees entre cabinets

---

## Voir aussi

- [Facturation utilisateur](../utilisateurs/facturation.md)
- [CGV](https://fiscia.pro/cgv)
