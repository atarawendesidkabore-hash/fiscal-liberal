# Performance et compatibilite

> Optimisation des performances, compatibilite navigateurs et usage mobile.

---

## Temps de reponse de l'API

### Benchmarks typiques

| Endpoint | Temps moyen | P95 |
|----------|------------|-----|
| `GET /health` | < 10 ms | 20 ms |
| `POST /auth/login` | 50-100 ms | 200 ms |
| `POST /v1/calc-is` | 15-30 ms | 50 ms |
| `POST /v2/calc-is` | 20-40 ms | 60 ms |
| `POST /v2/liasse` | 30-60 ms | 100 ms |
| `GET /gdpr/export` | 100-500 ms | 1 s |
| `POST /v2/ai/explain` | 5-30 s | 60 s |

> Les endpoints IA (Ollama) sont significativement plus lents car ils impliquent l'inference d'un modele de langage.

### Facteurs de performance

| Facteur | Impact | Recommandation |
|---------|--------|---------------|
| Taille des donnees d'entree | Faible | Pas de limite pratique pour les calculs IS |
| Nombre de liasses sauvegardees | Moyen | L'export RGPD ralentit avec beaucoup de liasses |
| Modele IA | Eleve | Mistral 7B est le meilleur compromis vitesse/qualite |
| Connexion reseau | Variable | Latence ajoutee au temps serveur |

## Optimisation cote client

### Bonnes pratiques API

**Utilisez le bon endpoint.** Les endpoints v2 (async) sont recommandes pour les nouvelles integrations :

```bash
# v1 (sync) — compatible, mais plus ancien
POST /v1/calc-is

# v2 (async) — recommande
POST /v2/calc-is
```

**Gerez les tokens efficacement.**

- Stockez le token d'acces en memoire (pas en localStorage)
- Utilisez le refresh token avant l'expiration (30 min)
- Ne demandez pas un nouveau token a chaque requete

```javascript
// Exemple : refresh automatique avant expiration
const tokenExpiresAt = decoded.exp * 1000;
const refreshMargin = 5 * 60 * 1000; // 5 minutes avant

if (Date.now() > tokenExpiresAt - refreshMargin) {
  await refreshToken();
}
```

**Implementez un retry avec backoff.**

En cas d'erreur 429 (rate limit) ou 503 (service IA indisponible) :

```javascript
async function fetchWithRetry(url, options, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    const response = await fetch(url, options);
    if (response.status === 429 || response.status === 503) {
      await new Promise(r => setTimeout(r, 1000 * Math.pow(2, i)));
      continue;
    }
    return response;
  }
  throw new Error("Max retries exceeded");
}
```

### Pagination

Pour les endpoints qui retournent des listes (audit logs, liasses), utilisez la pagination :

```bash
GET /audit-logs?skip=0&limit=50
GET /audit-logs?skip=50&limit=50
```

- `limit` maximum : 100 par requete
- Chargez les pages suivantes uniquement quand l'utilisateur scrolle

## Compatibilite navigateurs

### Navigateurs supportes

| Navigateur | Version minimale | Statut |
|-----------|-----------------|--------|
| Chrome | 90+ | Supporte |
| Firefox | 88+ | Supporte |
| Safari | 15+ | Supporte |
| Edge | 90+ | Supporte |
| Opera | 76+ | Supporte |
| Internet Explorer | — | Non supporte |

### Fonctionnalites requises

L'interface FiscIA Pro necessite :

- **JavaScript ES2020** (async/await, optional chaining)
- **CSS Grid et Flexbox**
- **Fetch API** (pas de dependance a XMLHttpRequest)
- **localStorage** (pour les preferences utilisateur)

### Navigateurs mobiles

| Navigateur | Plateforme | Statut |
|-----------|-----------|--------|
| Chrome Mobile | Android 10+ | Supporte |
| Safari Mobile | iOS 15+ | Supporte |
| Samsung Internet | Android 10+ | Supporte |
| Firefox Mobile | Android 10+ | Non teste |

## Usage mobile

### Interface responsive

L'interface FiscIA Pro est responsive et s'adapte aux ecrans mobiles :

- **Smartphone** (< 640px) : navigation hamburger, formulaires empiles, tableaux scrollables horizontalement
- **Tablette** (640-1024px) : sidebar retractable, formulaires sur 2 colonnes
- **Desktop** (> 1024px) : experience complete

### Recommandations mobiles

| Action | Recommandation |
|--------|---------------|
| Calcul IS | Fonctionnel sur mobile |
| Liasse 2058-A | Tablette ou desktop recommande (tableau complexe) |
| Assistant IA | Fonctionnel sur mobile |
| Administration | Desktop recommande |
| Export RGPD | Desktop recommande (fichier volumineux) |

### Mode hors ligne

FiscIA Pro necessite une connexion internet. Cependant :

- Les calculs IS simples pourraient etre caches localement (prevu v3.2)
- Les liasses en cours de saisie sont sauvegardees dans le navigateur (localStorage)
- En cas de perte de connexion, un message clair s'affiche

## Limites connues

### Rate limiting

| Ressource | Limite | Fenetre |
|-----------|--------|---------|
| API globale | 100 requetes | Par minute, par IP |
| Login | 5 tentatives | Par minute, par IP |
| Assistant IA | 10 requetes | Par minute, par utilisateur |
| Export RGPD | 1 requete | Par heure, par utilisateur |

En cas de depassement, l'API retourne `429 Too Many Requests` avec un header `Retry-After`.

### Taille des reponses

| Endpoint | Taille typique | Taille maximale |
|----------|---------------|----------------|
| Calcul IS | 1-2 KB | 5 KB |
| Liasse 2058-A | 3-5 KB | 10 KB |
| Export RGPD | 10 KB - 5 MB | Selon le volume de donnees |
| Reponse IA | 1-10 KB | 50 KB |

### Timeouts

| Operation | Timeout |
|-----------|---------|
| Requetes API standard | 30 secondes |
| Requetes IA (Ollama) | 120 secondes |
| Export RGPD | 60 secondes |

## Surveillance

### Endpoints de sante

Utilisez `GET /health` pour surveiller la disponibilite :

```bash
# Verification rapide
curl -s https://api.fiscia.pro/health | jq .status
# "healthy"
```

### Metriques Prometheus

FiscIA Pro expose des metriques Prometheus sur `/metrics` (acces restreint) :

- `http_requests_total` — nombre total de requetes
- `http_request_duration_seconds` — duree des requetes (histogramme)
- `http_requests_in_progress` — requetes en cours
- `ollama_requests_total` — requetes IA
- `ollama_request_duration_seconds` — duree des requetes IA

---

## Voir aussi

- [Problemes courants](problemes-communs.md) — FAQ et codes d'erreur
- [Introduction API](../developpeurs/introduction.md) — Reference technique
