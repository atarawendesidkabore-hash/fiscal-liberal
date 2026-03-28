# Demarrage rapide

> Creez votre compte et effectuez votre premier calcul IS en 5 minutes.

**Prerequis** : Un navigateur web moderne (Chrome, Firefox, Safari, Edge). Aucune installation requise.

**Temps estime** : 5 minutes

---

## Etape 1 : Creer votre compte

1. Rendez-vous sur **https://app.fiscia.pro/register**
2. Remplissez le formulaire :
   - **Email professionnel** : votre adresse email de cabinet
   - **Mot de passe** : minimum 8 caracteres
   - **Nom complet** : prenom et nom
   - **Nom du cabinet** (optionnel) : si renseigne, vous serez administrateur du cabinet
   - **SIREN du cabinet** (optionnel) : pour lier le cabinet a son identifiant fiscal
3. Cliquez **Creer un compte**
4. Vous etes connecte automatiquement

> **Note** : Si vous fournissez un nom de cabinet, vous obtenez le role **Admin** et pouvez inviter des collaborateurs. Sans nom de cabinet, vous obtenez le role **Client**.

## Etape 2 : Naviguer dans l'interface

Apres connexion, vous accedez au **tableau de bord** :

- **+ Nouveau calcul** : lance le formulaire de liasse 2058-A
- **Mes calculs** : historique de tous vos calculs sauvegardes
- **Stats** : nombre de calculs, IS cumule, SIREN distincts

La barre de navigation donne acces a :
- `/liasse` — Formulaire de saisie 2058-A
- `/dashboard` — Tableau de bord et historique
- `/resultats?id=...` — Detail d'un calcul specifique

## Etape 3 : Premier calcul IS

1. Cliquez **+ Nouveau calcul** ou allez sur `/liasse`
2. Remplissez les champs obligatoires :

| Champ | Description | Exemple |
|-------|-------------|---------|
| SIREN | Identifiant a 9 chiffres de l'entreprise | `987654321` |
| Exercice clos | Date de cloture au format YYYY-MM-DD | `2024-12-31` |
| Benefice comptable | Montant en EUR | `120000` |
| CA HT | Chiffre d'affaires hors taxes | `5000000` |
| Capital PP | Capital detenu >= 75% par des personnes physiques | Cocher si applicable |

3. Remplissez les reintegrations si applicable :
   - **WI** : IS comptabilise en charges (Art. 213 CGI)
   - **WG** : Amendes et penalites (Art. 39-2 CGI)
   - **WM** : Interets excedentaires CC associes (Art. 212 CGI)

4. Cochez **Sauvegarder ce calcul** si vous voulez le retrouver dans votre historique
5. Cliquez **Calculer l'IS**

## Etape 4 : Lire les resultats

Le resultat affiche :

- **RF brut** : Resultat fiscal brut (benefice + reintegrations)
- **RF net** : Resultat fiscal net (base IS)
- **IS total** : Impot sur les societes du
- **Regime** : PME taux reduit (15% + 25%) ou Normal (25%)
- **Acompte trimestriel** : IS / 4 (versements 15/03, 15/06, 15/09, 15/12)

Chaque resultat inclut les references CGI exactes et un disclaimer de validation professionnelle.

## Etape 5 : Sauvegarder et retrouver

Les calculs sauvegardes apparaissent dans le **tableau de bord** :
- Cliquez **Voir** pour afficher le detail complet
- Cliquez **Suppr.** pour supprimer un calcul (role fiscaliste+ requis via l'API v2)

---

## Etapes suivantes

- [Calcul IS en detail](calcul-is.md) — Comprendre les regimes PME et normal
- [Liasse 2058-A](liasse-2058a.md) — Guide ligne par ligne
- [Assistant IA](assistant-ia.md) — Poser des questions fiscales
