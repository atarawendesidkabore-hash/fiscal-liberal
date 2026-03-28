# Calcul de l'Impot sur les Societes

> Comprendre le workflow complet de calcul IS, les conditions PME et l'interpretation des resultats.

**Reference** : Art. 219 CGI, LFI 2024

**Temps estime** : 10 minutes de lecture

---

## Vue d'ensemble

FiscIA Pro calcule l'IS en trois etapes :

```
Benefice comptable
  + Reintegrations (WI, WG, WM, WN)
  - Deductions (WV, L8)
  = Resultat Fiscal (RF brut)
  - Deficits anterieurs (XI)
  = RF net (base imposable)
  → Application du taux (15% PME + 25% ou 25% normal)
  = IS total du
```

## Taux d'imposition 2024

### Taux normal : 25%

Applicable a l'integralite du benefice imposable pour toutes les entreprises soumises a l'IS.

### Taux reduit PME : 15%

Applicable sur les **premiers 42 500 EUR** de benefice, a condition que :

| Condition | Detail | Article CGI |
|-----------|--------|-------------|
| CA HT | < 10 000 000 EUR | Art. 219-I-b |
| Capital | Libere et detenu >= 75% par des personnes physiques | Art. 219-I-b |

Si les deux conditions sont remplies :
- **Tranche 1** : 0 a 42 500 EUR → taux 15%
- **Tranche 2** : au-dela de 42 500 EUR → taux 25%

### Exemple concret

```
Entreprise SA DUPONT
  CA HT        : 5 000 000 EUR
  Capital 100% personnes physiques
  RF net       : 100 000 EUR

→ Regime : PME taux reduit (Art. 219-I-b)
  Tranche 15% : 42 500 x 15% =  6 375 EUR
  Tranche 25% : 57 500 x 25% = 14 375 EUR
  IS TOTAL     :                20 750 EUR
  Acompte trim.: 20 750 / 4  =  5 187,50 EUR
```

## Verification de l'eligibilite PME

FiscIA Pro verifie automatiquement les conditions PME :

1. **CA HT < 10 M EUR** : compare le chiffre d'affaires saisi au seuil
2. **Capital PP >= 75%** : verifie la case "Capital detenu par personnes physiques"

Si une condition manque, le taux normal 25% est applique sur la totalite du benefice.

> **Attention** : FiscIA Pro ne verifie pas automatiquement la composition exacte du capital (par exemple, la presence de personnes morales dans l'actionnariat). C'est au fiscaliste de s'assurer que la condition de detention est bien remplie avant de cocher la case.

## Acomptes trimestriels

L'IS est paye en 4 acomptes egaux :

| Date | Echeance |
|------|----------|
| 15 mars | 1er acompte (N) |
| 15 juin | 2e acompte (N) |
| 15 septembre | 3e acompte (N) |
| 15 decembre | 4e acompte (N) |

Chaque acompte = IS total / 4

Le solde est verse avec la declaration de resultats (dans les 3 mois de la cloture, ou le 15 mai pour les exercices clos le 31/12).

## Deficits

### Report en avant (Art. 209 I CGI)

- Duree : **illimitee**
- Plafond : **1 000 000 EUR + 50%** du benefice au-dela de 1 M EUR
- Imputation automatique si des deficits anterieurs sont renseignes

### Report en arriere — Carry-back (Art. 220 quinquies CGI)

- Duree : **1 an** en arriere
- Plafond : **1 000 000 EUR**
- Genere une creance sur le Tresor

## Interpretation des resultats

| Champ | Signification |
|-------|---------------|
| RF brut | Resultat fiscal avant imputation des deficits |
| RF net | Base imposable apres deficits (= base IS) |
| IS total | Impot du |
| Regime | PME taux reduit ou Normal |
| Acompte | Versement trimestriel = IS / 4 |
| Details | Decomposition des reintegrations et deductions |

## Erreurs courantes

1. **Oubli de la reintegration de l'IS comptabilise (WI)** : L'IS passe en charges dans les comptes mais doit toujours etre reintegre
2. **Mauvaise appreciation du seuil PME** : Le seuil de 10 M EUR s'applique au CA HT, pas au total des produits
3. **Capital PP mal evalue** : Les SARL de famille ou SAS avec holding intermediaire peuvent ne pas remplir la condition des 75%

---

## Voir aussi

- [Liasse 2058-A](liasse-2058a.md) — Reintegrations et deductions en detail
- [API : Endpoint /calc-is](../developpeurs/endpoints/calculs.md) — Utilisation via l'API
