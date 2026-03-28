# FiscIA Pro - Strategie de Pricing

> Document strategique interne - Ne pas diffuser

---

## Philosophie de tarification

### Principes directeurs

1. **Ancrage concurrentiel** : le prix doit etre immediatement comparable a WK (10x moins cher)
2. **Simplicite** : 3 plans maximum, pas de compteur cache, pas de surprise
3. **Progression naturelle** : chaque plan repond a une etape de croissance du cabinet
4. **Sans engagement** : mensuel par defaut, annuel en option (-16%)

### Methode de calcul

Le pricing est base sur la **valeur percue** et non sur le cout :

| Facteur | Valeur |
|---------|--------|
| Cout marginal par utilisateur | ~0.50 EUR/mois (infrastructure) |
| Valeur du temps economise | 45 min x 30 EUR/h = 22.50 EUR par liasse |
| Willingness-to-pay (enquete) | 30-100 EUR/mois pour les independants |
| Reference concurrentielle | WK 300-500 EUR, Cegid 200-400 EUR |
| Prix psychologique optimal | 29 / 79 / 199 EUR (terminaisons en 9) |

---

## Grille tarifaire

### Plans mensuels

| | **Starter** | **Pro** | **Cabinet** |
|--|------------|---------|-------------|
| **Prix** | **29 EUR/mois** | **79 EUR/mois** | **199 EUR/mois** |
| Prix annuel | 290 EUR/an (-16%) | 790 EUR/an (-16%) | 1 990 EUR/an (-16%) |
| Calculs IS | 50/mois | Illimites | Illimites |
| Liasse 2058-A | Oui | Oui | Oui |
| Art. 145 mere-filiale | Oui | Oui | Oui |
| Utilisateurs | 1 | 1 | 10 |
| Assistant IA fiscal | Non | Oui | Oui |
| API access | Non | Non | Oui |
| Support | Email (48h) | Email prioritaire (4h) | Telephone (1h) |
| RGPD (export/suppression) | Oui | Oui | Oui |
| Onboarding personnalise | Non | Non | 1 session (1h) |

### Justification psychologique de chaque prix

#### Starter a 29 EUR — "Le prix d'un livre de fiscalite"

- **Ancrage** : un BOFiP imprime coute 35 EUR, un abonnement Revue Fiduciaire ~50 EUR
- **Terminaison en 9** : prix psychologique percu comme "dans les 20 EUR"
- **Barriere basse** : decide en 30 secondes, pas besoin de validation hierarchique
- **Valeur percue** : economise 2h/mois minimum → valeur de 60 EUR (2x le prix)

#### Pro a 79 EUR — "Le prix d'un dejeuner client par mois"

- **Ancrage** : un repas d'affaires a Paris coute 60-100 EUR
- **Saut de valeur** : l'IA fiscale justifie le x2.7 (feature hero du plan)
- **No-brainer** : pour un cabinet qui fait 30+ liasses/an, le ROI est de 30:1
- **Ecart psychologique** : 79 EUR est assez loin de 29 EUR pour paraitre "premium" mais assez bas pour rester accessible

#### Cabinet a 199 EUR — "Moins cher qu'un seul poste WK"

- **Ancrage** : un poste WK coute 300-500 EUR/mois → 199 EUR pour 10 postes est un choc
- **Valeur par siege** : 199 / 10 = 19.90 EUR/utilisateur/mois
- **Effet de nombre** : "10 utilisateurs" cree une perception de generosite
- **Seuil** : sous la barre des 200 EUR, evite le processus d'achat complexe

---

## Pricing annuel

### Mecanique de la remise annuelle

| Plan | Mensuel | Annuel | Economie | Mois offerts |
|------|---------|--------|----------|-------------|
| Starter | 29 x 12 = 348 EUR | 290 EUR | 58 EUR | ~2 mois |
| Pro | 79 x 12 = 948 EUR | 790 EUR | 158 EUR | ~2 mois |
| Cabinet | 199 x 12 = 2 388 EUR | 1 990 EUR | 398 EUR | ~2 mois |

**Pourquoi -16% et pas -20% :**
- 16% = exactement 2 mois gratuits sur 12 (message simple et credible)
- 20% serait trop agressif et eroderait la marge
- "2 mois gratuits" est plus parlant que "-16%"

### Affichage sur la page tarification

```
Toggle : [Mensuel] / [Annuel — 2 mois offerts]

Starter : 29 EUR/mois → [barre] 24.17 EUR/mois (facture 290 EUR/an)
Pro :     79 EUR/mois → [barre] 65.83 EUR/mois (facture 790 EUR/an)
Cabinet : 199 EUR/mois → [barre] 165.83 EUR/mois (facture 1 990 EUR/an)
```

---

## Offres promotionnelles

### Lancement (M1-M3)

| Offre | Mecanique | Duree | Code |
|-------|-----------|-------|------|
| Early Adopter | -30% a vie sur le plan annuel | 3 premiers mois | FISCIA30 |
| Essai etendu | 30 jours gratuits (au lieu de 14) | 3 premiers mois | AUTO |
| Bundle OEC | -20% pour les membres OEC | Permanent | OEC20 |

**Calcul de l'offre Early Adopter :**

| Plan | Prix normal annuel | Prix Early Adopter | Economie |
|------|-------------------|-------------------|----------|
| Starter | 290 EUR | 203 EUR | 87 EUR/an |
| Pro | 790 EUR | 553 EUR | 237 EUR/an |
| Cabinet | 1 990 EUR | 1 393 EUR | 597 EUR/an |

> L'offre "a vie" cree de l'urgence et recompense les premiers adopteurs. Le cout est acceptable car ces clients sont les plus susceptibles de devenir des ambassadeurs.

### Saisonniere

| Periode | Offre | Justification |
|---------|-------|---------------|
| Janvier | "Campagne IS : essai 30 jours" | Debut de saison, maximiser les essais |
| Septembre | "Switch WK : 3 mois a -50%" | Capter les renouvellements WK |
| Novembre | "Black Friday : annuel a -25%" | Traditionnelle, forte attente |

### Referral

| Action | Recompense |
|--------|-----------|
| Parrainage → essai | Rien (trop tot) |
| Parrainage → souscription | 1 mois gratuit (parrain + filleul) |
| 3 parrainages convertis | 1 mois upgrade offert |
| 10 parrainages convertis | 3 mois Cabinet gratuits |

---

## Tier Enterprise (futur, a partir de M12)

### Positionnement

Pour les cabinets de 10+ associes et les reseaux (AGC, groupements).

| Critere | Enterprise |
|---------|-----------|
| Prix | Sur devis (estimatif : 500-2 000 EUR/mois) |
| Utilisateurs | Illimites |
| Calculs | Illimites |
| SLA | 99.9% garanti |
| Support | Responsable de compte dedie |
| Integration | API + connecteurs Sage/Cegid/ACD |
| Deploiement | On-premise optionnel (IA locale) |
| Formation | Programme de formation sur site |
| Conformite | SOC 2 Type II + audit CNIL sur demande |
| Facturation | Annuelle, bon de commande, virement |

### Criteres de qualification Enterprise

- Cabinet de 10+ associes OU reseau/groupement
- Budget outils fiscaux > 5 000 EUR/mois
- Besoin d'integration avec logiciel de production existant
- Exigence SLA contractuel
- Facturation par bon de commande (pas de CB)

### Processus de vente Enterprise

```
Demande de contact → Qualification (15 min call)
→ Demo personnalisee (45 min) → POC 30 jours
→ Proposition commerciale → Negociation
→ Signature contrat → Onboarding (2-4 semaines)
```

**Cycle de vente estime :** 2-4 mois
**Panier moyen estime :** 12 000 EUR/an

---

## Analyse de sensibilite

### Elasticite-prix estimee

| Variation de prix | Impact sur les inscriptions | Impact sur le revenu |
|-------------------|-----------------------------|---------------------|
| -30% (20/55/139 EUR) | +40% inscriptions | -5% revenu (volume compense) |
| -15% (25/67/169 EUR) | +15% inscriptions | +2% revenu |
| Prix actuel (29/79/199 EUR) | Baseline | Baseline |
| +15% (33/91/229 EUR) | -20% inscriptions | -8% revenu |
| +30% (38/103/259 EUR) | -35% inscriptions | -15% revenu |

**Conclusion :** le prix actuel est au point optimal. Une baisse de 15% pourrait etre testee si la conversion essai → paye est < 20%.

### Scenarios de revenus (Annee 1)

| Scenario | Clients M12 | ARPU | MRR M12 | ARR |
|----------|-------------|------|---------|-----|
| Pessimiste | 100 | 55 EUR | 5 500 EUR | 66 000 EUR |
| Base | 250 | 68 EUR | 17 000 EUR | 204 000 EUR |
| Optimiste | 500 | 75 EUR | 37 500 EUR | 450 000 EUR |

---

## Metriques de pricing a surveiller

### KPIs mensuels

| Indicateur | Cible | Alerte |
|-----------|-------|--------|
| Conversion essai → paye | > 25% | < 15% |
| Upgrade rate (Starter → Pro) | > 8%/mois | < 3%/mois |
| Downgrade rate (Pro → Starter) | < 2%/mois | > 5%/mois |
| Churn rate | < 5%/mois | > 8%/mois |
| LTV/CAC ratio | > 5x | < 3x |
| Expansion revenue (% MRR) | > 10% | < 5% |
| ARPU | > 60 EUR | < 45 EUR |

### Signaux de repricing

| Signal | Action |
|--------|--------|
| Conversion essai > 40% | Le prix est peut-etre trop bas → tester +10% |
| Churn > 8% et raison = "trop cher" | Tester un tier intermediaire |
| 50%+ des clients sur Starter | Le jump Starter→Pro est trop grand → creer un plan a 49 EUR |
| Enterprise requests > 10/mois | Lancer le tier Enterprise |
| Concurrence baisse ses prix | Ne pas reagir (notre structure de couts est superieure) |

---

## Compliance marketing des prix

### Mentions obligatoires

Tout affichage de prix doit inclure :

- Prix HT clairement indique ("29 EUR HT/mois")
- TVA applicable (20% pour les services numeriques en France)
- Mention "sans engagement" si engagement minimum = 0
- Conditions de l'essai gratuit (duree, pas de CB requise pour l'essai)
- Lien vers les CGV

### Comparaisons de prix

Toute comparaison avec WK ou Cegid doit :

- Citer la source du prix concurrent (grille tarifaire publique ou estimation basee sur enquete)
- Preciser "prix releves en [mois/annee], susceptibles de varier"
- Comparer des offres de niveau comparable (memes fonctionnalites)
- Ne pas utiliser de termes absolus ("le moins cher du marche") sans preuve

### Prix barre

L'affichage du prix barre (mensuel → annuel) doit respecter :

- Le prix de reference doit avoir ete effectivement pratique
- La reduction doit etre calculee correctement
- La duree de l'offre doit etre indiquee si c'est une promotion temporaire

---

## Roadmap pricing

| Trimestre | Action | Objectif |
|-----------|--------|---------|
| T1 | Lancement 3 plans + offre Early Adopter | 100 clients payants |
| T2 | A/B test annuel vs mensuel (toggle page pricing) | Optimiser mix annuel (cible : 40%) |
| T3 | Lancement offre "Switch WK" (-50% 3 mois) | Capter les renouvellements septembre |
| T4 | Analyse churn par plan → ajuster si necessaire | Churn < 5% |
| T5 (Y2) | Lancement tier Enterprise | 5 contrats Enterprise |
| T6 (Y2) | Facturation a l'usage optionnelle (pay-per-calc) | Segment TPE ultra-sensible au prix |

---

*Document interne - Mise a jour : Mars 2026*
