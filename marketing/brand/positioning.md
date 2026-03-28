# Positionnement Concurrentiel — FiscIA Pro

> Document interne. Dernière mise à jour : mars 2026.

---

## 1. Paysage concurrentiel

Le marché de l'outillage fiscal français se divise en 5 catégories. Aucun acteur ne couvre les trois dimensions de FiscIA Pro (logique IS profonde + IA + souveraineté).

### Catégorie A : Excel et outils manuels

**Acteurs** : Microsoft Excel, Google Sheets, tableurs internes.

| Forces | Faiblesses |
|---|---|
| Universel, maîtrisé par tous | Zéro référence CGI automatique |
| Flexible, personnalisable | Risque d'erreur formule élevé |
| Coût marginal nul | Aucun audit trail |
| | Pas de vérification Art. 145 |
| | Maintenance des modèles chronophage |

**Part de marché estimée** : ~70 % des cabinets de < 10 associés utilisent principalement Excel pour l'IS.

---

### Catégorie B : Bases juridiques en ligne

**Acteurs** : Legifrance, BOFiP, Dalloz, LexisNexis, Revue Fiduciaire.

| Forces | Faiblesses |
|---|---|
| Sources officielles et exhaustives | Recherche lente et non contextuelle |
| Jurisprudence complète | Aucun calcul intégré |
| Mises à jour législatives en temps réel | Navigation complexe |
| | Pas d'automatisation liasse |

**Relation avec FiscIA Pro** : complémentaire, pas concurrent direct. FiscIA Pro indexe le CGI et facilite l'accès, mais ne remplace pas Legifrance comme source officielle.

---

### Catégorie C : ERP et logiciels comptables

**Acteurs** : Sage (Sage 100, Sage FRP), Cegid, ACD, Quadratus, Coala.

| Forces | Faiblesses |
|---|---|
| Suite complète (compta + paie + fiscal) | Module IS basique (saisie manuelle) |
| Base installée massive | Pas d'IA ni d'automatisation intelligente |
| Intégration cabinet-client existante | Liasse 2058-A = formulaire à remplir, pas calculé |
| Support et formation établis | Coût élevé (500-2 000 EUR/mois) |
| | Pas de vérification Art. 145 |

**Relation avec FiscIA Pro** : FiscIA Pro se positionne en complément, pas en remplacement. Intégrations futures prévues (QuickBooks, Xero déjà planifiés ; Sage/Cegid à étudier).

---

### Catégorie D : IA générique

**Acteurs** : ChatGPT (OpenAI), Claude (Anthropic), Gemini (Google), Mistral.

| Forces | Faiblesses |
|---|---|
| Capacité de raisonnement puissante | Aucune garantie de précision fiscale |
| Interface conversationnelle naturelle | Hallucinations sur les articles CGI |
| Coût faible (20-30 EUR/mois) | Zéro audit trail |
| | Données envoyées aux USA (RGPD ?) |
| | Pas de calcul IS structuré |
| | Pas de disclaimer professionnel |
| | Pas de liasse 2058-A |

**Menace** : élevée à moyen terme. Les LLMs s'améliorent rapidement. Mais le fossé sur la précision CGI, l'audit trail et la souveraineté des données reste profond.

---

### Catégorie E : Outils internes Big4 / grands cabinets

**Acteurs** : Deloitte Tax Analytics, PwC Halo, EY Diligent, KPMG Clara.

| Forces | Faiblesses |
|---|---|
| Budget R&D massif | Réservés aux clients/employés du réseau |
| Données propriétaires riches | Prix inaccessible pour cabinets indépendants |
| Intégration audit + fiscal | Non disponibles en SaaS |
| | Pas adaptés au marché PME français |

**Relation avec FiscIA Pro** : pas de concurrence directe. Les Big4 servent les ETI/grands groupes. FiscIA Pro cible les cabinets indépendants et les PME.

---

## 2. Matrice de différenciation

| Dimension | FiscIA Pro | Excel | Legifrance | Sage/Cegid | ChatGPT |
|---|---|---|---|---|---|
| **Calcul IS automatisé** | Taux normal + PME, acomptes, déficits | Manuel, formules custom | Non | Saisie manuelle | Approximatif, non fiable |
| **Liasse 2058-A** | Ligne par ligne, réf. CGI | Manuel | Non | Formulaire vide | Non structuré |
| **Art. 145 mère-filiale** | 6 conditions vérifiées auto | Non | Texte brut | Non | Peut halluciner |
| **Recherche CGI** | < 2 secondes, fuzzy + exacte | Non | Lente, non contextuelle | Non | Peut halluciner les articles |
| **Audit trail** | Complet (user, IP, timestamp) | Non | Non | Basique | Non |
| **Conformité RGPD** | Complète (export, suppression) | N/A | N/A | Variable | Données US |
| **IA locale** | Oui (Ollama, formule Cabinet) | N/A | N/A | Non | Non |
| **Prix** | 29-199 EUR/mois | ~0 EUR | Gratuit | 500-2 000 EUR/mois | 20-30 EUR/mois |

**Lecture** : FiscIA Pro est le seul outil qui combine calcul IS précis + références CGI + IA + souveraineté des données + prix accessible.

---

## 3. Création de catégorie — « IA fiscale »

### Constat

Le terme « IA fiscale » n'est pas encore une catégorie logicielle reconnue dans le marché français. Les experts-comptables ne cherchent pas « IA fiscale » — ils cherchent « calcul IS », « liasse 2058-A » ou « recherche CGI ».

### Stratégie

FiscIA Pro doit simultanément **éduquer le marché** sur la catégorie et **l'occuper en premier**.

### Plan d'action

| Action | Canal | Fréquence | Objectif |
|---|---|---|---|
| Articles de fond « IA fiscale » | Blog FiscIA Pro | 2/mois | SEO + thought leadership |
| Tribune « L'IA fiscale : opportunité ou menace ? » | Revue Fiduciaire, Les Échos | 1/trimestre | Légitimité médiatique |
| Webinaires « IA fiscale en pratique » | YouTube + LinkedIn | 1/mois | Démonstration + leads |
| Stand « IA fiscale » | Congrès de l'Ordre, Journées IFEC | 2/an | Présence physique + crédibilité |
| Livre blanc « État de l'IA fiscale en France » | Site FiscIA Pro (gated) | 1/an | Lead generation premium |
| Partenariats formation | CNOEC, universités | Continu | Intégration dans les cursus |

### Mots-clés SEO cibles

- « IA fiscale » (à créer)
- « assistant fiscal IA »
- « calcul IS automatique »
- « liasse 2058-A automatisée »
- « logiciel fiscal expert-comptable »
- « Art. 219 CGI calcul »
- « régime mère-filiale vérification »

### Indicateur de succès

La catégorie « IA fiscale » est créée quand :
1. Le terme apparaît dans les articles de la Revue Fiduciaire sans guillemets.
2. Les prospects disent « je cherche une IA fiscale » en premier contact.
3. Des concurrents se positionnent comme « IA fiscale » — validant la catégorie.

---

## 4. Analyse d'espace blanc

### Le triptyque défensible

FiscIA Pro occupe l'intersection de trois dimensions. Aucun concurrent ne couvre les trois simultanément.

```
                    Logique IS profonde
                    (Art. 219, 145, 2058-A)
                          /\
                         /  \
                        /    \
                       / FISC \
                      /  IA    \
                     /  PRO     \
                    /____________\
     IA intégrée                   Souveraineté
     (calcul, search,              (France, RGPD,
      NLP fiscal)                   IA locale)
```

| Dimension | Ce que ça signifie | Qui ne l'a pas |
|---|---|---|
| **Logique IS profonde** | Calcul IS multi-régime, liasse 2058-A ligne par ligne, 6 conditions Art. 145 | ChatGPT, Excel |
| **IA intégrée** | Recherche fuzzy CGI, assistant NLP, guardrails automatiques | Sage, Cegid, Legifrance |
| **Souveraineté** | Hébergement France, RGPD complet, IA locale zéro donnée transmise | ChatGPT, tous les outils US |

### Opportunités d'espace blanc non encore exploitées

| Opportunité | Description | Priorité |
|---|---|---|
| **TVA** | Étendre le moteur à la TVA (Art. 256 et suivants) — un volume de calculs bien supérieur à l'IS | Haute |
| **Intégration Sage/Cegid** | Connecteur bidirectionnel avec les ERP dominants en France | Haute |
| **Multi-juridiction UEMOA** | Calcul IS pour les pays de la zone UEMOA (même base juridique francophone) | Moyenne |
| **Formation / Certification** | Module e-learning « IA fiscale » certifié par le CNOEC | Moyenne |
| **Audit fiscal automatisé** | Revue de cohérence entre liasses N et N-1 avec détection d'anomalies | Basse (v2) |

---

## 5. Positionnement en thought leadership

### Double crédibilité

FiscIA Pro est fondé par un tandem rare :

- **Thomas Lefebvre** — Ex-Deloitte, 12 ans en IS, HEC Paris → crédibilité fiscale
- **Sarah Nguyen** — Ex-Google DeepMind, experte NLP juridique → crédibilité technologique

Cette double légitimité est un atout concurrentiel majeur. Aucun concurrent ne peut revendiquer simultanément Big4 + FAANG.

### Calendrier éditorial cible

| Mois | Thème blog | Événement externe | Action PR |
|---|---|---|---|
| Janvier | Nouveautés LFI 20XX | — | Communiqué « Ce qui change pour l'IS » |
| Mars | Campagne IS — bonnes pratiques | — | Webinaire pré-campagne |
| Mai | Art. 145 — pièges courants | — | Infographie LinkedIn |
| Juin | Bilan de campagne IS | — | Article Revue Fiduciaire |
| Septembre | Rentrée fiscale — planification | Congrès de l'Ordre | Stand + conférence |
| Octobre | IA fiscale — état des lieux | Journées IFEC | Tribune Les Échos |
| Novembre | Acomptes IS — optimisation | — | Newsletter spéciale |
| Décembre | Rétrospective + perspectives | — | Livre blanc annuel |

### Cibles médias

| Média | Type | Public | Format |
|---|---|---|---|
| Revue Fiduciaire | Presse spécialisée | Experts-comptables | Tribunes, articles techniques |
| Les Échos | Presse économique | Décideurs, investisseurs | Tribunes, interviews |
| La Lettre de l'Expert-Comptable | Newsletter professionnelle | EC inscrits à l'Ordre | Études de cas |
| LinkedIn | Social professionnel | EC, fiscalistes, DAF | Posts, articles, vidéos courtes |
| YouTube | Vidéo | EC et collaborateurs | Démos, tutoriels, webinaires |
| BFM Business | TV/Radio | Grand public B2B | Interviews fondateurs |

---

## 6. Playbook de réponse concurrentielle

### Quand le prospect mentionne Excel

> **Repositionnement** : « Excel est un excellent outil général. FiscIA Pro est un outil spécialisé. La différence, c'est que FiscIA cite automatiquement l'Art. 219, vérifie les 6 conditions Art. 145, et produit un audit trail. Excel ne le fera jamais. Et le coût du temps perdu en Excel est de 117 000 EUR/an pour un cabinet de 5 associés. »

### Quand le prospect mentionne ChatGPT

> **Repositionnement** : « ChatGPT est impressionnant en conversation, mais il hallucine les articles du CGI. Demandez-lui l'Art. 219-I-b — il inventera parfois un texte qui n'existe pas. FiscIA Pro ne hallucine pas : chaque résultat cite la source exacte. Et vos données restent en France, pas chez OpenAI à San Francisco.
>
> En prime, FiscIA Pro offre une IA locale optionnelle : zéro donnée transmise à l'extérieur. ChatGPT ne peut pas faire ça. »

### Quand le prospect mentionne Sage ou Cegid

> **Repositionnement** : « Sage et Cegid sont de très bons ERP comptables. Mais leur module IS est un formulaire à remplir manuellement — il ne calcule pas le taux réduit PME, ne vérifie pas Art. 145 et n'a pas d'IA.
>
> FiscIA Pro ne remplace pas Sage — il le complète. Nous prévoyons d'ailleurs des intégrations directes. Vous gardez votre ERP pour la comptabilité, et vous utilisez FiscIA Pro pour l'IS et la liasse. »

### Quand le prospect mentionne Legifrance / BOFiP

> **Repositionnement** : « Legifrance est la source officielle et le restera. FiscIA Pro ne la remplace pas — il la rend accessible en 2 secondes. Au lieu de naviguer dans l'arborescence du CGI, vous tapez votre question et FiscIA trouve l'article exact avec son score de pertinence.
>
> En plus, FiscIA Pro ne fait pas que chercher : il calcule. Legifrance vous donne le texte de l'Art. 219, FiscIA Pro vous donne le montant de l'IS. »

### Quand le prospect dit « j'attends de voir le marché mûrir »

> **Repositionnement** : « Attendre est un choix respectable. Mais le marché de l'IA fiscale n'a pas besoin de mûrir — il a besoin de pionniers. Les cabinets qui adoptent aujourd'hui construisent un avantage concurrentiel : collaborateurs plus rapides, clients mieux servis, marge horaire préservée.
>
> Dans 2 ans, vos concurrents utiliseront un outil comme FiscIA Pro. La question est : voulez-vous être en avance ou en retard ?
>
> L'essai est gratuit, sans carte bancaire. Le risque est nul. Le coût de l'attente ne l'est pas. »

---

## 7. Données de marché clés

| Indicateur | Valeur | Source |
|---|---|---|
| Experts-comptables inscrits en France | 21 611 | CNOEC 2024 |
| Cabinets d'expertise comptable | ~19 000 | CNOEC 2024 |
| Taux horaire moyen EC | 150 EUR/h | Observatoire des cabinets |
| Temps moyen perdu sur recherche CGI/calcul IS | 2-4h/semaine | Enquête terrain FiscIA |
| Coût du temps perdu (cabinet 5 associés) | 117 000 EUR/an | Calcul : 5 × 150 × 3h × 48 sem × 1/5 |
| TAM (si 100 % Pro tier) | ~20,5 M EUR/an | 21 611 × 79 EUR × 12 |
| Pénétration cible Y1 | 200 cabinets | Objectif interne |
| ARR cible Y1 | ~190 K EUR | 200 × 79 × 12 |
