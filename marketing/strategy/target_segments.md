# FiscIA Pro - Segmentation & Personas

> Document strategique interne - Ne pas diffuser

---

## Marche cible : la profession comptable francaise

### Taille du marche (TAM / SAM / SOM)

| Niveau | Taille | Description |
|--------|--------|-------------|
| **TAM** | 21 611 cabinets | Tous les cabinets d'expertise comptable inscrits a l'OEC (2024) |
| **SAM** | 18 370 cabinets | Cabinets de 1-10 collaborateurs (85% du marche) |
| **SOM** | 920 cabinets | Objectif Annee 1 : 5% du SAM |

### Revenus potentiels

| Segment | Cabinets | ARPU/mois | ARR potentiel |
|---------|----------|-----------|---------------|
| Independants (Starter) | 500 | 29 EUR | 174 000 EUR |
| Petits cabinets (Pro) | 300 | 79 EUR | 284 400 EUR |
| Cabinets moyens (Cabinet) | 120 | 199 EUR | 286 560 EUR |
| **Total SOM** | **920** | **68 EUR moy.** | **744 960 EUR** |

---

## Segment primaire : cabinets 1-5 associes (80% du pipeline)

### Sous-segment A : l'expert-comptable independant

**Profil demographique :**
- Age : 35-55 ans
- Formation : DSCG + DEC, parcours en Big 4 ou cabinet
- Localisation : 60% province, 40% Ile-de-France
- CA cabinet : 100 000 - 500 000 EUR
- Collaborateurs : 0-2 (secretaire + stagiaire)

**Stack technologique actuel :**
- Logiciel de production : Sage Expert, ACD, Quadratus
- Calcul IS : Excel + baremes PDF imprimes
- IA : aucune ou ChatGPT (avec inquietude RGPD)
- Budget outils fiscaux : 50-200 EUR/mois

**Douleurs principales (par ordre de priorite) :**

1. **Temps** : 45 min par liasse 2058-A, 15 min par calcul IS — le pic de janvier-avril est epuisant
2. **Cout** : les outils WK/Cegid sont hors budget pour un independant
3. **Risque** : peur de l'erreur de taux (PME vs normal), responsabilite civile en jeu
4. **Isolement** : pas de collegue pour valider un calcul complexe (l'IA comble ce vide)

**Comportement d'achat :**
- Decide seul, cycle de decision : 1-2 semaines
- Sensible au prix (cherche "le meilleur rapport qualite-prix")
- S'informe sur LinkedIn, blogs experts-comptables, forums OEC
- Essai gratuit indispensable avant achat
- Resilie si pas utilise dans les 30 premiers jours

**Declencheurs d'achat :**
- Saison fiscale (janvier-avril) : urgence de productivite
- Erreur couteuse recente : prise de conscience du risque
- Depart d'un collaborateur : besoin d'automatisation
- Conference OEC / webinaire : decouverte de l'outil

**Objections typiques :**
| Objection | Reponse |
|-----------|---------|
| "C'est trop bon marche pour etre serieux" | Demo en direct : montrer la precision technique |
| "Je fais deja mes calculs sur Excel" | Comparaison temps : 45 min vs 30 secondes |
| "Est-ce conforme RGPD ?" | IA locale + export Art. 20 + suppression Art. 17 |
| "Et si la loi change ?" | Mise a jour automatique a chaque LFI |

---

### Sous-segment B : le cabinet 3-5 associes

**Profil demographique :**
- Structure : SARL ou SAS, 3-5 associes, 5-15 collaborateurs
- CA cabinet : 500 000 - 2 000 000 EUR
- Localisation : villes moyennes et grandes metropoles
- Specialisation : PME, TPE, professions liberales

**Stack technologique actuel :**
- Logiciel de production : Sage Expert, Cegid, ACD
- Calcul IS : Wolters Kluwer ISAGI ou outil interne
- IA : aucune (inquietude DPO/CNIL)
- Budget outils fiscaux : 500-2 000 EUR/mois (toutes licences)

**Douleurs principales :**

1. **Licences** : 300-500 EUR/poste/mois chez WK — le budget technologique explose avec chaque embauche
2. **Formation** : les juniors mettent 6 mois a etre autonomes sur les calculs fiscaux
3. **Conformite** : le DPO du cabinet freine l'adoption d'outils IA cloud
4. **Collaboration** : pas de visibilite sur les calculs des collaborateurs

**Comportement d'achat :**
- Decision collegiale (2-3 associes), cycle : 1-3 mois
- Un associe champion porte le projet, les autres valident le prix et la conformite
- Demande de demo personnalisee + rendez-vous visio
- Testent avec 1-2 utilisateurs avant deploiement complet
- Sensibles au support (veulent un interlocuteur identifie)

**Parcours d'achat typique :**

```
Decouverte (LinkedIn/OEC) → Visite site → Demo en ligne
→ Essai 14 jours (1-2 users) → Reunion associes
→ Validation DPO/RGPD → Souscription Cabinet
→ Deploiement progressif → Adoption complete (2-3 mois)
```

---

## Segment secondaire : marches adjacents (20% du pipeline)

### Sous-segment C : l'expert-comptable freelance / auto-entrepreneur

**Profil :**
- Expert-comptable inscrit a l'OEC, exerce seul sans structure
- 20-50 dossiers clients
- Tres sensible au prix (0-50 EUR/mois max)
- Utilise des outils gratuits (Excel, LibreOffice)

**Strategie :** Plan Starter a 29 EUR/mois. Conversion par le bouche-a-oreille et la communaute.

**Valeur pour FiscIA Pro :** Volume de base utilisateurs + ambassadeurs naturels (recommandent a leurs pairs).

### Sous-segment D : le dirigeant de PME autonome

**Profil :**
- Dirigeant-gerant de SARL/SAS, CA < 10M EUR
- Fait sa compta lui-meme ou avec un comptable a temps partiel
- Veut comprendre son IS avant la campagne fiscale
- N'est PAS expert-comptable (vocabulaire simplifie necessaire)

**Strategie :** Plan Starter pour le calcul IS simple. L'IA explique les resultats en langage courant.

**Risque :** Ce segment peut generer du support disproportionne. Limiter a l'IS (pas de liasse 2058-A).

### Sous-segment E : les cabinets d'avocats fiscalistes

**Profil :**
- 2-10 avocats specialises en droit fiscal
- Clients : ETI, groupes familiaux, montages mere-filiale
- Besoin : verification rapide Art. 145, simulation IS
- Budget : sensibilite faible au prix, sensibilite forte a la precision

**Strategie :** Plan Cabinet avec API. Positionner FiscIA Pro comme outil de verification rapide, pas de remplacement de leur expertise.

---

## Personas detailles

### Persona 1 : Sophie, 42 ans — Experte-comptable independante

**Contexte :**
- Cabinet unipersonnel a Toulouse, 35 dossiers
- DSCG + 8 ans en Big 4 avant de s'installer
- Utilise Sage Expert + Excel pour l'IS
- Suit les comptes LinkedIn de la profession

**Citation :** *"Je passe mes week-ends de mars a verifier mes liasses. Il doit y avoir un meilleur moyen."*

**Journee type (saison fiscale) :**
- 8h : emails clients, relances pieces manquantes
- 9h-12h : saisie comptable sur Sage
- 14h-17h : calculs IS manuels, verification taux PME
- 17h-19h : redaction liasses, verification croisee

**Comment FiscIA Pro change sa journee :**
- 14h-14h30 : saisie liasse dans FiscIA Pro, verification automatique
- 14h30-15h : questions a l'IA sur cas complexes (mere-filiale, interets excedentaires)
- 15h : liasse validee, exportee → 2h30 economisees

**Canal d'acquisition :** LinkedIn organique + Google "calcul IS PME en ligne"

---

### Persona 2 : Philippe, 52 ans — Associe gerant, cabinet 4 associes

**Contexte :**
- Cabinet a Lyon, 12 collaborateurs, 400 dossiers
- Utilise Wolters Kluwer depuis 15 ans (contrat annuel 18 000 EUR)
- Inquiet sur la conformite IA (a lu les recommandations CNIL)
- Cherche a reduire les couts sans sacrifier la qualite

**Citation :** *"Je paye 18 000 EUR par an pour WK et mes juniors ne savent toujours pas faire une mere-filiale sans moi."*

**Point de bascule :** Le renouvellement WK en septembre est l'occasion de tester une alternative.

**Canal d'acquisition :** Salon OEC + recommandation d'un confrere + demo personnalisee

---

### Persona 3 : Camille, 28 ans — Collaboratrice junior

**Contexte :**
- 2 ans d'experience, preparer le DEC
- Fait les liasses "simples" (PME taux normal)
- Bloquee des qu'il y a une mere-filiale ou des interets excedentaires
- N'ose pas deranger les associes pour chaque question

**Citation :** *"J'aimerais un outil qui m'explique pourquoi on reintegre cette ligne, pas juste le montant."*

**Role dans l'achat :** Prescripteur interne — elle recommande l'outil a Philippe apres l'avoir decouvert sur LinkedIn.

**Canal d'acquisition :** LinkedIn + Instagram professionnel + communautes jeunes experts-comptables

---

## Matrice de priorite

| Segment | Taille | Facilite d'acquisition | ARPU | Priorite |
|---------|--------|----------------------|------|----------|
| Expert-comptable independant | Grande | Facile (decision seul) | 29-79 EUR | **P1** |
| Cabinet 3-5 associes | Moyenne | Moyen (decision collegiale) | 199 EUR | **P1** |
| Freelance / auto-entrepreneur | Grande | Tres facile | 29 EUR | **P2** |
| Dirigeant PME | Tres grande | Facile | 29 EUR | **P3** |
| Cabinet avocats fiscalistes | Petite | Difficile | 199 EUR | **P3** |

---

## Saisonnalite

Le marche comptable francais a une saisonnalite marquee :

| Periode | Intensite | Action marketing |
|---------|-----------|-----------------|
| Janvier-Avril | Pic (campagne fiscale) | Conversion maximale, pub payante |
| Mai-Juin | Moyen (clotures retardataires) | Contenus pedagogiques, webinaires |
| Juillet-Aout | Creux | Content SEO long-terme, preparation rentree |
| Septembre | Reprise + renouvellements WK | Campagne "switch" anti-WK |
| Octobre-Novembre | Moyen (acomptes IS, LFI) | Webinaires LFI, mises a jour |
| Decembre | Faible (fetes) | Offres fin d'annee, promotion annuelle |

**Fenetre critique :** Septembre (renouvellements concurrents) + Janvier (debut campagne fiscale).

---

*Document interne - Mise a jour : Mars 2026*
