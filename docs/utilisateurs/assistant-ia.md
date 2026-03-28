# Assistant IA fiscal

> Posez des questions fiscales en langage naturel et obtenez des reponses structurees avec references CGI.

**Prerequis** : Compte FiscIA Pro (formule Pro ou Cabinet)

**Temps estime** : 10 minutes de lecture

---

## Vue d'ensemble

L'assistant IA de FiscIA Pro est un modele specialise en fiscalite IS francaise. Il repond a vos questions en citant les articles CGI applicables et en fournissant des calculs detailles.

### 4 modes disponibles

| Mode | Description | Endpoint |
|------|-------------|----------|
| **general** | Questions fiscales ouvertes | `POST /v2/ai/explain` |
| **is** | Calcul IS avec detail des tranches | `POST /v2/ai/explain-is` |
| **liasse** | Analyse 2058-A ligne par ligne | `POST /v2/ai/explain-liasse` |
| **mere** | Verification Art. 145 mere-filiale | `POST /v2/ai/explain-mere` |

## Poser des questions efficaces

### Bonnes pratiques

1. **Soyez specifique** : incluez les montants, les conditions et le contexte
2. **Mentionnez le regime** : PME, normal, integration fiscale
3. **Precisez l'exercice** : les regles changent d'une annee a l'autre

### Exemples de questions efficaces

```
Mode: is
"Calcule l'IS pour une SA avec un RF de 200 000 EUR, CA de 3M EUR,
capital 100% personnes physiques. Exercice 2024."

Mode: liasse
"Analyse cette liasse : benefice 150k, IS comptabilise 18k,
amendes 5k, interets CC excedentaires 12k. CA 8M, capital PP."

Mode: mere
"SA ALPHA detient 7% de SA BETA depuis 3 ans.
Titres nominatifs, pleine propriete. BETA soumise IS, hors ETNC.
Dividendes recus : 80 000 EUR. Verifier eligibilite Art. 145."

Mode: general
"Quelles sont les differences entre le report en avant (Art. 209 I)
et le carry-back (Art. 220 quinquies) pour les deficits IS ?"
```

### Questions a eviter

- Questions trop vagues : "Comment optimiser mon IS ?" (pas assez de contexte)
- Questions hors IS : l'IA est specialisee en IS, pas en TVA ou IR
- Questions sur des regimes speciaux non couverts (ZFU, JEI, etc.)

## Comprendre les reponses

Chaque reponse de l'IA contient :

| Champ | Description |
|-------|-------------|
| `response` | Texte de la reponse avec calculs et references |
| `mode` | Mode utilise (is, liasse, mere, general) |
| `model` | Modele d'IA utilise |
| `elapsed_ms` | Temps de generation en millisecondes |
| `tokens_evaluated` | Nombre de tokens du prompt evalues |
| `tokens_generated` | Nombre de tokens generes |
| `disclaimer` | Avertissement de validation professionnelle |

### Exemple de reponse

```json
{
  "response": "CALCUL IS - Exercice 2024\nResultat Fiscal : 100 000 EUR\nRegime : PME taux reduit (Art. 219-I-b)\nTranche 15% : 42 500 x 15% = 6 375 EUR\nTranche 25% : 57 500 x 25% = 14 375 EUR\nIS TOTAL : 20 750 EUR",
  "mode": "is",
  "model": "fiscia-fiscal-is-v3",
  "elapsed_ms": 2340,
  "disclaimer": "Reponse indicative generee par IA locale. Validation professionnelle requise."
}
```

## Quand faire confiance vs verifier

### Fiable (haute confiance)

- Calculs arithmetiques (tranches, taux, acomptes)
- References d'articles CGI (numeros d'articles)
- Conditions legales enumerees (6 conditions Art. 145)

### A verifier systematiquement

- Cas particuliers (integration fiscale, ZFU, JEI)
- Interets CC : le TMP BdF change chaque trimestre
- Appreciation des conditions PME (composition du capital)
- Montants specifiques a un dossier client

### Regle d'or

> L'IA est un assistant, pas un decisionnaire. Chaque reponse porte le disclaimer :
> *"Reponse indicative. Validation professionnelle requise."*
>
> Utilisez l'IA pour gagner du temps sur la recherche et les calculs de base,
> puis validez avec votre expertise professionnelle.

## IA locale (Ollama)

La formule **Cabinet** offre la possibilite d'heberger le modele d'IA directement sur votre serveur :

- **Zero donnee transmise** : le modele s'execute integralement en local
- **Modele** : Mistral 7B fine-tune sur le referentiel fiscal IS
- **Configuration** : via le fichier `Modelfile.fiscal_IS_v3`
- **Temperature** : 0.05 (reponses deterministes)

### Verifier la disponibilite

```
GET /v2/ai/status

{
  "available": true,
  "model": "fiscia-fiscal-is-v3"
}
```

Si `available: false`, verifiez que le serveur Ollama est demarre et que le modele est charge.

---

## Voir aussi

- [API : AI endpoints](../developpeurs/endpoints/calculs.md#ai-endpoints) — Documentation technique
- [Securite](../conformite/securite.md) — IA locale et protection des donnees
