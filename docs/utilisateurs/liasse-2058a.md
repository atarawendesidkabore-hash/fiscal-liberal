# Liasse 2058-A — Guide ligne par ligne

> Remplissage automatise du tableau de determination du resultat fiscal (formulaire DGFiP 2058-A).

**Reference** : Formulaire DGFiP 2058-A, LFI 2024

**Temps estime** : 15 minutes de lecture

---

## Vue d'ensemble

Le formulaire 2058-A determine le passage du **resultat comptable** au **resultat fiscal**. FiscIA Pro automatise ce calcul en traitant chaque ligne avec les references CGI exactes.

```
Benefice comptable (XN)
  + Reintegrations extracomptables (WI, WG, WM, WN, WD...)
  - Deductions extracomptables (WV, L8...)
  = Resultat fiscal brut
  - Deficits anterieurs (XI)
  = Resultat fiscal net → base IS
```

## Lignes traitees par FiscIA Pro

### Reintegrations (augmentent le RF)

| Code | Libelle | Art. CGI | Traitement |
|------|---------|----------|------------|
| **WI** | IS comptabilise en charges | Art. 213 | **Toujours reintegre**. L'IS n'est pas une charge deductible. |
| **WG** | Amendes et penalites | Art. 39-2 | **Toujours reintegre**. Amendes fiscales, majorations, penalites de retard DGFiP. |
| **WM** | Interets excedentaires CC | Art. 39-1-3 + 212 | Reintegre si le taux d'interet depasse le TMP BdF ou si le capital n'est pas entierement libere. |
| **WN** | Reintegrations diverses | Divers | Inclut la quote-part 5% de frais et charges sur dividendes mere-filiale (Art. 216). |
| **WD** | Amortissements excedentaires | Art. 39-4 | Reintegration de l'excedent d'amortissement (vehicules de tourisme, etc.). |

### Deductions (diminuent le RF)

| Code | Libelle | Art. CGI | Traitement |
|------|---------|----------|------------|
| **WV** | Regime mere-filiale | Art. 145 + 216 | Deduction des dividendes recus si les 6 conditions Art. 145 sont remplies. |
| **L8** | QP 12% PV LT titres participation | Art. 219-I-a quater | Quote-part de 12% reintegree sur les plus-values LT de cession de titres de participation. |

### Deficits

| Code | Libelle | Art. CGI | Traitement |
|------|---------|----------|------------|
| **XI** | Deficits anterieurs | Art. 209 I | Report illimite, plafonne a 1 M EUR + 50% au-dela. |
| **ZL** | Carry-back | Art. 220 quinquies | Report en arriere, plafonne a 1 M EUR. |

## Workflow pas a pas

### 1. Saisir les donnees de base

Renseignez les champs obligatoires :

- **SIREN** : identifiant a 9 chiffres de l'entreprise
- **Exercice clos** : date de cloture (YYYY-MM-DD)
- **Benefice comptable** : montant en EUR (ligne XN du compte de resultat)
- **Perte comptable** : si applicable (benefice et perte sont mutuellement exclusifs)

### 2. Renseigner les reintegrations

Pour chaque ligne, saisissez le montant en EUR :

```
Exemple : SARL MARTIN
  Benefice comptable :  120 000 EUR
  WI (IS comptabilise) : 10 000 EUR
  WG (amendes DGFiP)   :  2 000 EUR
  WM (interets CC)      :  3 000 EUR
```

### 3. Renseigner les deductions

```
  WV (mere-filiale) : 0 EUR  (pas de dividendes mere-filiale)
```

### 4. Lancer le calcul

FiscIA Pro effectue automatiquement :

1. Addition des reintegrations au benefice comptable
2. Soustraction des deductions
3. Determination du RF brut
4. Application des deficits anterieurs (si renseignes)
5. Determination du regime applicable (PME ou Normal)
6. Calcul de l'IS par tranches
7. Calcul des acomptes trimestriels

### 5. Verifier les resultats

```
Resultat pour SARL MARTIN :
  RF brut = 120 000 + 10 000 + 2 000 + 3 000 = 135 000 EUR
  RF net  = 135 000 EUR (pas de deficits anterieurs)
  Regime  = PME taux reduit (CA < 10M, capital PP)
  IS      = 42 500 x 15% + 92 500 x 25% = 6 375 + 23 125 = 29 500 EUR
```

## Prevention des erreurs courantes

### Erreur 1 : Oubli de WI

L'IS comptabilise (compte 695) **doit toujours etre reintegre**. C'est l'erreur la plus frequente. FiscIA Pro l'applique automatiquement.

### Erreur 2 : Confusion WN / WV

- **WN** (reintegration) : quote-part 5% de frais et charges sur dividendes mere-filiale
- **WV** (deduction) : montant total des dividendes exoneres

Ces deux lignes fonctionnent ensemble : si vous deduisez 50 000 EUR en WV, vous devez reintegrer 2 500 EUR (5%) en WN.

### Erreur 3 : Interets CC sans verification

La ligne WM ne concerne que l'**excedent** d'interets. Il faut comparer le taux applique au TMP de la Banque de France et verifier que le capital est entierement libere.

### Erreur 4 : Regime mere-filiale sans verification des 6 conditions

Avant de renseigner la ligne WV, verifiez les 6 conditions cumulatives de l'Art. 145 CGI. Utilisez l'endpoint `/mere` ou la page de verification Art. 145 dans l'application.

## Guardrails automatiques

FiscIA Pro applique 5 guardrails sur chaque calcul :

| Code | Regle | Action |
|------|-------|--------|
| G001 | Disclaimer present dans la sortie | Bloque si absent |
| G002 | PME verifie avant taux 15% | Bloque si conditions non remplies |
| G003 | Donnees confidentielles non exposees | Bloque si SIREN visible en clair dans les logs |
| G004 | Version legislative citee (LFI 2024) | Bloque si reference absente |
| G005 | Art. 145 verifie si mere-filiale present | Bloque si WV > 0 sans verification |

---

## Voir aussi

- [Calcul IS](calcul-is.md) — Taux et regimes en detail
- [API : Endpoint /liasse](../developpeurs/endpoints/liasse.md) — Utilisation via l'API
