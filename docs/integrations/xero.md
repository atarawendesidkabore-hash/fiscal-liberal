# Integration Xero

> Connectez FiscIA Pro a Xero pour automatiser l'import des donnees comptables.

**Statut** : Prevue v3.2 (Q2 2025)

---

## Vue d'ensemble

L'integration Xero permettra de :

1. **Importer** le grand livre et le compte de resultat pour pre-remplir la liasse 2058-A
2. **Exporter** les ecritures provisionnelles d'IS vers Xero
3. **Mapper** les codes analytiques Xero aux lignes du formulaire fiscal

## Configuration prevue

### Connexion

1. **Parametres > Integrations > Connecter Xero**
2. Authentification OAuth 2.0 avec votre compte Xero
3. Selection de l'organisation Xero

### Mapping des comptes

| Categorie Xero | Ligne 2058-A | Sens |
|----------------|-------------|------|
| Tax Expense (IS) | WI | Reintegration |
| Fines & Penalties | WG | Reintegration |
| Interest on Loans | WM | Reintegration (si excedentaire) |
| Dividend Income | WV | Deduction (si Art. 145) |

### Frequence de synchronisation

| Mode | Frequence | Description |
|------|-----------|-------------|
| Manuel | A la demande | Import ponctuel avant calcul |
| Automatique | Quotidien | Sync nocturne a 02:00 UTC |
| Temps reel | Webhook | Notification Xero a chaque ecriture |

## Depannage

| Probleme | Solution |
|----------|----------|
| Token expire | Reconnecter dans Parametres > Integrations |
| Organisation non trouvee | Verifier les permissions dans Xero |
| Devise incorrecte | FiscIA Pro fonctionne en EUR uniquement |

---

*Cette fonctionnalite est en cours de developpement. Contactez-nous pour rejoindre le programme beta.*
