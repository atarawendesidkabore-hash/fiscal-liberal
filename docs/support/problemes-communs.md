# Problemes courants

> FAQ, codes d'erreur et contact support.

---

## Questions frequentes

### Compte et connexion

**Je n'arrive pas a me connecter.**

1. Verifiez que votre adresse email est correcte (sensible a la casse)
2. Utilisez la fonction "Mot de passe oublie" si necessaire
3. Apres 5 tentatives echouees, votre compte est bloque temporairement (15 minutes)
4. Si le probleme persiste, contactez le support

**Mon token JWT a expire.**

Les tokens d'acces expirent apres 30 minutes. Utilisez le refresh token pour en obtenir un nouveau :

```bash
POST /auth/refresh
Authorization: Bearer <refresh_token>
```

Le refresh token est valide 7 jours. Passe ce delai, reconnectez-vous.

**Je ne peux pas acceder a certaines fonctionnalites.**

Verifiez votre role :
- **Client** : calcul IS uniquement
- **Fiscaliste** : calcul IS + liasse 2058-A + assistant IA
- **Admin** : toutes les fonctionnalites + gestion d'equipe

Demandez a votre administrateur de modifier votre role si necessaire.

### Calculs IS

**Mon calcul IS donne un resultat inattendu.**

1. Verifiez les parametres d'entree (CA, charges, duree d'exercice)
2. Verifiez si le taux PME (15%) s'applique :
   - Capital entierement libere par des personnes physiques
   - CA < 10 M EUR
   - Benefice < 42 500 EUR pour le taux reduit
3. Verifiez la duree de l'exercice (prorata si != 12 mois)
4. Consultez le detail du calcul dans la reponse API (`detail` ou `breakdown`)

**Le taux PME ne s'applique pas alors que mon client y est eligible.**

Assurez-vous de passer `capital_personnes_physiques: true` dans la requete :

```json
{
  "chiffre_affaires": 500000,
  "charges_exploitation": 400000,
  "capital_personnes_physiques": true
}
```

### Liasse 2058-A

**Certaines lignes de la liasse sont a zero alors qu'elles ne devraient pas l'etre.**

La liasse 2058-A ne calcule que les lignes pour lesquelles des donnees d'entree sont fournies. Verifiez que tous les champs pertinents sont remplis dans `Liasse2058AInput`.

**Je ne retrouve pas une liasse sauvegardee.**

Les liasses sont associees a votre compte utilisateur. Verifiez :
1. Que vous etes connecte avec le bon compte
2. Que la liasse n'a pas ete supprimee
3. Que la periode de retention (3 ans) n'est pas depassee

### Assistant IA

**L'assistant IA ne repond pas.**

L'assistant IA utilise Ollama en local. Verifiez :

```bash
GET /v2/ai/status
```

Si `available: false`, le serveur Ollama n'est pas accessible. Causes possibles :
- Ollama n'est pas demarre
- Le modele n'est pas telecharge (`ollama pull mistral`)
- Le port 11434 est bloque par un pare-feu

**Les reponses de l'IA sont lentes.**

Le temps de reponse depend du modele et du materiel :
- **Mistral 7B** : 5-15 secondes (GPU recommande)
- **Llama 3** : 10-30 secondes
- Timeout par defaut : 120 secondes

---

## Codes d'erreur

### Erreurs HTTP standard

| Code | Signification | Cause frequente |
|------|--------------|----------------|
| 400 | Bad Request | Donnees d'entree invalides |
| 401 | Unauthorized | Token manquant ou expire |
| 403 | Forbidden | Role insuffisant pour cette action |
| 404 | Not Found | Ressource inexistante |
| 409 | Conflict | Doublon (email deja utilise, etc.) |
| 422 | Unprocessable Entity | Validation Pydantic echouee |
| 429 | Too Many Requests | Rate limit depasse |
| 500 | Internal Server Error | Erreur serveur (contactez le support) |
| 503 | Service Unavailable | Ollama non disponible |
| 504 | Gateway Timeout | Ollama timeout (requete trop longue) |

### Erreurs metier

| Code erreur | Message | Solution |
|-------------|---------|----------|
| `AUTH_INVALID_CREDENTIALS` | Email ou mot de passe incorrect | Verifiez vos identifiants |
| `AUTH_ACCOUNT_LOCKED` | Compte bloque temporairement | Attendez 15 minutes |
| `AUTH_TOKEN_EXPIRED` | Token expire | Utilisez le refresh token |
| `ROLE_INSUFFICIENT` | Role insuffisant | Contactez votre admin |
| `FIRM_NOT_FOUND` | Cabinet non trouve | Verifiez l'ID du cabinet |
| `LIASSE_NOT_FOUND` | Liasse non trouvee | Verifiez l'ID de la liasse |
| `CONSENT_INVALID_TYPE` | Type de consentement invalide | Utilisez : data_processing, marketing, analytics |
| `RATE_LIMIT_EXCEEDED` | Trop de requetes | Attendez avant de reessayer |
| `OLLAMA_UNAVAILABLE` | Service IA indisponible | Verifiez le statut Ollama |

### Format des erreurs

Toutes les erreurs suivent le meme format JSON :

```json
{
  "detail": "Description lisible de l'erreur"
}
```

Pour les erreurs de validation (422), le format inclut les champs concernes :

```json
{
  "detail": [
    {
      "loc": ["body", "chiffre_affaires"],
      "msg": "Input should be greater than or equal to 0",
      "type": "greater_than_equal"
    }
  ]
}
```

---

## Depannage avance

### Verifier la sante de l'API

```bash
GET /health
```

Reponse attendue :

```json
{
  "status": "healthy",
  "version": "3.0.0"
}
```

### Verifier votre profil

```bash
GET /auth/me
Authorization: Bearer <token>
```

Cela confirme que votre token est valide et affiche votre role et cabinet.

### Logs de diagnostic

Si vous rencontrez une erreur 500, notez :
1. L'heure exacte de l'erreur
2. L'endpoint appele
3. Les parametres envoyes
4. Le message d'erreur complet

Ces informations aideront le support a diagnostiquer le probleme.

---

## Contact support

### Canaux de support

| Formule | Canal | Delai de reponse |
|---------|-------|-----------------|
| Starter | Email | 48 heures ouvrables |
| Pro | Email prioritaire | 4 heures ouvrables |
| Cabinet | Telephone + email | 1 heure ouvrables |

### Email

- **Support technique** : support@fiscia.pro
- **Securite** : security@fiscia.pro
- **DPO (RGPD)** : dpo@fiscia.pro

### Informations a fournir

Pour un traitement rapide de votre demande, incluez :

1. Votre **adresse email** de connexion
2. Le **nom de votre cabinet** (si applicable)
3. Une **description detaillee** du probleme
4. Les **etapes pour reproduire** le probleme
5. Les **captures d'ecran** ou messages d'erreur
6. Le **navigateur** et systeme d'exploitation utilises

---

## Voir aussi

- [Performance](performance.md) — Optimisation et compatibilite
- [Documentation API](../developpeurs/introduction.md) — Reference technique
- [RGPD](../conformite/gdpr.md) — Vos droits sur vos donnees
