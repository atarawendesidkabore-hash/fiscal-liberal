# Integration QuickBooks

> Connectez FiscIA Pro a QuickBooks pour synchroniser les donnees comptables.

**Statut** : Prevue v3.2 (Q2 2025)

---

## Vue d'ensemble

L'integration QuickBooks permettra de :

1. **Importer** les donnees du compte de resultat directement dans le formulaire 2058-A
2. **Synchroniser** les calculs IS vers QuickBooks comme ecritures provisionnelles
3. **Mapper** les comptes QuickBooks aux lignes 2058-A

## Configuration prevue

### Etape 1 : Connecter votre compte QuickBooks

1. Allez dans **Parametres > Integrations**
2. Cliquez **Connecter QuickBooks**
3. Autorisez FiscIA Pro dans la fenetre QuickBooks OAuth
4. Selectionnez l'entreprise a connecter

### Etape 2 : Mapper les comptes

FiscIA Pro proposera un mapping automatique des comptes :

| Compte QuickBooks | Ligne 2058-A |
|-------------------|-------------|
| 695 - IS | WI |
| 6712 - Amendes | WG |
| 6615 - Interets CC | WM |
| 761 - Dividendes | WV (si mere-filiale) |

Vous pourrez ajuster le mapping manuellement.

### Etape 3 : Synchronisation

- **Import** : manuel ou automatique a la cloture
- **Export** : ecriture provisionnelle d'IS dans QuickBooks
- **Frequence** : quotidienne ou a la demande

## Depannage

| Probleme | Solution |
|----------|----------|
| Erreur d'autorisation OAuth | Reconnecter via Parametres > Integrations |
| Mapping incorrect | Verifier le plan comptable dans QuickBooks |
| Donnees manquantes | S'assurer que l'exercice est cloture dans QuickBooks |

---

*Cette fonctionnalite est en cours de developpement. Contactez-nous pour rejoindre le programme beta.*
