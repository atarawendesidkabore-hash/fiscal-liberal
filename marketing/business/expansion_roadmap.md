# Feuille de Route d'Expansion — FiscIA Pro

> Version 1.0 | Mars 2026
> Document strategique interne — Ne pas diffuser

---

## 1. Vision a 3 ans

FiscIA Pro devient **la reference IA fiscale du monde francophone**, en commencant par l'IS francais puis en etendant geographiquement et fonctionnellement.

### Trajectoire cible

| | Y1 (2026-27) | Y2 (2027-28) | Y3 (2028-29) |
|--|-------------|-------------|-------------|
| **Marches** | France | + Belgique, Luxembourg | + Suisse FR, Quebec, Afrique OHADA |
| **Produit** | IS + 2058-A + IA locale | + TVA + liasse complete | + CVAE/CFE + integration fiscale |
| **Clients** | 920 | 2 800 | 5 500 |
| **ARR** | 745K EUR | 2,1M EUR | 4,5M EUR |
| **Equipe** | 6 | 15 | 30 |
| **Levee** | Pre-seed / bootstrap | Seed (1-2M EUR) | Serie A (5-8M EUR) |

---

## 2. Phase 1 — France : Penetration du marche (Y1)

### Strategie

Capturer 5% du marche accessible (SAM = 18 370 cabinets) en ciblant d'abord les independants et petits cabinets, segments les plus reactifs et les moins engages avec les editeurs historiques.

### Objectifs chiffres

| Indicateur | Cible Y1 |
|-----------|----------|
| Clients Starter (29 EUR) | 500 |
| Clients Pro (79 EUR) | 300 |
| Clients Cabinet (199 EUR) | 120 |
| **Total clients** | **920** |
| **MRR fin Y1** | **62 000 EUR** |
| **ARR** | **745 000 EUR** |
| Churn mensuel | <3% |
| NPS | >40 |

### Canaux d'acquisition prioritaires

| Canal | Budget Y1 | Leads attendus | CAC cible | Conversion |
|-------|----------|---------------|----------|-----------|
| **SEO / Blog** | 8 000 EUR | 2 500 | 3 EUR/lead | 5% |
| **LinkedIn organique** | 3 000 EUR (outils) | 1 500 | 2 EUR/lead | 4% |
| **LinkedIn Ads** | 25 000 EUR | 1 200 | 21 EUR/lead | 8% |
| **Google Ads** | 20 000 EUR | 800 | 25 EUR/lead | 10% |
| **Evenements OEC** | 29 000 EUR | 500 | 58 EUR/lead | 12% |
| **Partenaires/referral** | 15 000 EUR | 300 | 50 EUR/lead | 15% |
| **Total** | **100 000 EUR** | **6 800** | **15 EUR avg** | **~7% avg** |

### Jalons trimestriels

| Trimestre | Jalon produit | Jalon commercial | Jalon partenariat |
|-----------|--------------|-----------------|-------------------|
| **Q1** | GA stable, Xero live | 100 clients, SEO operationnel | 5 affilies actifs |
| **Q2** | QuickBooks live, API v2 | 300 clients, LinkedIn Ads | 1 CROEC signe, 10 affilies |
| **Q3** | Pennylane integration, IA v2 | 600 clients, Congres OEC | 3 CROECs, 20 certifies |
| **Q4** | TVA module (beta), exports | 920 clients, NPS >40 | 5 CROECs, 1 POC white-label |

---

## 3. Phase 2 — Belgique et Luxembourg (Y2)

### Justification

La Belgique et le Luxembourg partagent avec la France :
- La langue francaise (Wallonie + Bruxelles, tout le Luxembourg)
- Des concepts fiscaux similaires (IS/ISOC/IRC inspires du meme droit continental)
- La proximite geographique (deploiement commercial depuis Paris)
- L'absence d'alternative IA fiscale locale sur ces marches

### 3.1 Belgique

#### Marche

| Donnee | Valeur |
|--------|--------|
| Fiduciaires enregistrees | ~12 000 |
| SAM (1-10 employes, francophone) | ~4 500 |
| SOM Y2 cible (3%) | ~135 cabinets |
| Impot : ISOC | Taux : 25% (PME : 20% sur premiere tranche 100K EUR) |
| Declaration : Biztax | Formulaire electronique obligatoire |
| Autorite : ITAA | Institut des Conseillers Fiscaux et des Experts-Comptables |

#### Adaptation produit

| Element | Travail requis | Effort |
|---------|---------------|--------|
| Moteur de calcul ISOC | Adapter Art. 219 → CIR/92 belge | 3-4 semaines dev |
| Formulaire Biztax | Nouveau generateur (XML Biztax) | 2-3 semaines dev |
| IA locale | Fine-tuning sur CIR/92 + jurisprudence belge | 2 semaines data |
| Interface | Traduction NL (optionnel, Flandre) | 1 semaine |
| Conformite | RGPD identique (APD belge = CNIL) | Minimal |

#### Go-to-market Belgique

1. **Partenariat ITAA** : Convention similaire OEC (Q1 Y2)
2. **Evenement** : Forum for the Future (evenement ITAA annuel, Bruxelles)
3. **Premier client** : Cibler 5 fiduciaires pilotes bruxelloises (reseau personnel)
4. **Pricing** : Identique France (EUR, meme structure)
5. **Support** : Equipe France (meme fuseau horaire)

### 3.2 Luxembourg

#### Marche

| Donnee | Valeur |
|--------|--------|
| Fiduciaires enregistrees | ~3 000 |
| SAM | ~1 200 (francophone, <10 employes) |
| SOM Y2 cible (3%) | ~36 cabinets |
| Impot : IRC | Taux : 17% (+ 7% impot solidarite + ICC communale) |
| Declaration | Formulaire 500 electronique |
| Autorite : OEC Luxembourg | Ordre des Experts-Comptables du Grand-Duche |

#### Adaptation produit

| Element | Travail requis | Effort |
|---------|---------------|--------|
| Moteur IRC | Nouveau module (taux composite IRC+solidarite+ICC) | 2-3 semaines |
| Formulaire 500 | Generateur XML specifique | 2 semaines |
| IA locale | Fine-tuning LIR luxembourgeoise | 1 semaine data |
| Particularites | SOPARFI, SPF (vehicules holdings) | 2 semaines specialisation |

#### Go-to-market Luxembourg

1. **Approche directe** : Marche petit, contact personnel (CEO à Luxembourg)
2. **Partenariat OEC Luxembourg** : Convention tarifaire
3. **Pricing premium** : +20% vs France (marche a plus forte capacite financiere)
4. **Cible** : Fiduciaires PME (pas les Big 4 / structures holdings complexes Y2)

### Objectifs Phase 2

| Indicateur | Belgique Y2 | Luxembourg Y2 | Total Phase 2 |
|-----------|------------|---------------|---------------|
| Clients | 135 | 36 | 171 |
| ARPU | 85 EUR/mois | 105 EUR/mois | 89 EUR/mois |
| ARR additionnel | 138K EUR | 45K EUR | 183K EUR |

---

## 4. Phase 3 — Expansion francophone (Y3)

### 4.1 Suisse (cantons francophones)

| Donnee | Valeur |
|--------|--------|
| Cantons cibles | Vaud, Geneve, Neuchatel, Fribourg (partie FR), Valais (partie FR) |
| Fiduciaires SAM | ~2 000 |
| SOM Y3 (2%) | ~40 cabinets |
| Impot | Impot federal direct (IFD) 8.5% + impot cantonal (variable 12-24%) |
| Particularite | Chaque canton a son propre taux et deductions |

**Defi technique** : Moteur multi-cantonal (5 modules cantonaux + federal).
**Approche** : Commencer par Vaud + Geneve (60% du SAM romand), ajouter cantons progressivement.
**Partenariat** : Fiduciaire Suisse (association professionnelle), collaboration avec une fiduciaire locale.
**Pricing** : CHF, +40% vs France (cout de la vie suisse).

### 4.2 Quebec

| Donnee | Valeur |
|--------|--------|
| CPA Quebec (comptables agrees) | ~40 000 |
| SAM (cabinets <10) | ~5 000 |
| SOM Y3 (1%) | ~50 cabinets |
| Impot | IS federal (CRA) 15% + IS provincial (Revenu Quebec) 11.5% |
| Particularite | Double declaration (T2 federal + CO-17 provincial) |

**Defi technique** : Systeme fiscal tres different (CRA + Revenu Quebec). Effort dev significatif (8-12 semaines).
**Approche** : Partenariat avec un editeur local ou une firme CPA pour co-developpement.
**Pricing** : CAD, aligne sur le marche local (~49-199 CAD/mois).
**Timeline** : Y3 Q3 lancement beta, Y3 Q4 GA.

### 4.3 Afrique francophone (OHADA)

| Donnee | Valeur |
|--------|--------|
| Pays OHADA francophones cibles | Senegal, Cote d'Ivoire, Cameroun, Burkina Faso |
| Cabinets comptables estimes | ~8 000 (total zone) |
| SOM Y3 (0.5%) | ~40 cabinets |
| Impot | IS variable (25-30% selon pays), inspire du CGI francais |
| Particularite | Plan comptable OHADA (SYSCOHADA), liasses specifiques |

**Avantage strategique** : Passerelle avec le reseau WASI (West African Shipping Intelligence) deja developpe.
**Approche** : Partenariat avec ONECCA (Senegal), OECFB (Burkina Faso) — ordres professionnels locaux.
**Pricing** : Adapte au pouvoir d'achat (10-49 EUR/mois).
**Modele** : SaaS cloud (pas de deploiement local — infrastructure limitee).

### Objectifs Phase 3

| Marche | Clients Y3 | ARPU | ARR additionnel |
|--------|-----------|------|----------------|
| Suisse romande | 40 | 140 EUR | 67K EUR |
| Quebec | 50 | 120 CAD (~82 EUR) | 49K EUR |
| Afrique OHADA | 40 | 30 EUR | 14K EUR |
| **Total Phase 3** | **130** | - | **130K EUR** |

---

## 5. Extensions de gamme

### Roadmap produit

| Module | Timeline | Effort dev | Impact ARR | Justification |
|--------|----------|-----------|-----------|---------------|
| **TVA/Declaration CA3** | Y1 Q4 (beta) → Y2 Q1 (GA) | 6 semaines | +15% ARPU | Demande #1 des clients existants |
| **Liasse fiscale complete** (2050-2059) | Y2 Q1-Q2 | 10 semaines | +25% ARPU | Passage de "outil IS" a "suite fiscale" |
| **Module audit trail** | Y2 Q2 | 3 semaines | Inclus Cabinet | Exigence grands cabinets / white-label |
| **CVAE + CFE** | Y3 Q1 | 4 semaines | +5% ARPU | Completude offre fiscale entreprise |
| **Integration fiscale Art. 223 A** | Y3 Q2 | 8 semaines | Plan Enterprise (399 EUR) | Groupes de societes, ticket eleve |
| **Credit d'impot recherche (CIR)** | Y3 Q3 | 6 semaines | Module premium 49 EUR/mois | Forte demande PME innovantes |

### Evolution des plans tarifaires

| Plan | Y1 | Y2 (apres extensions) | Y3 |
|------|----|-----------------------|-----|
| **Starter** | 29 EUR (IS + 2058-A) | 39 EUR (+TVA) | 39 EUR |
| **Pro** | 79 EUR (+IA) | 99 EUR (+liasse complete) | 109 EUR (+CVAE/CFE) |
| **Cabinet** | 199 EUR (+API, 20 users) | 249 EUR (+audit trail) | 249 EUR |
| **Enterprise** (new Y3) | - | - | 399 EUR (+Art. 223 A, 50 users, SLA) |

### Impact sur l'ARPU

| Annee | ARPU moyen | Variation |
|-------|-----------|----------|
| Y1 | 68 EUR/mois | Base |
| Y2 | 89 EUR/mois | +31% (TVA + liasse + nouveaux marches premium) |
| Y3 | 105 EUR/mois | +18% (extensions + plan Enterprise) |

---

## 6. Approche Enterprise

### Cibles prioritaires

| Groupe | Taille | Decision | Timeline approche |
|--------|--------|----------|-------------------|
| **Fiducial** | 900 bureaux, 7 500 pers. | Direction Innovation, Paris | Y1 Q4 (POC) |
| **In Extenso** (Deloitte) | 250 bureaux, 5 000 pers. | Equipe Outils internes | Y2 Q1 |
| **Baker Tilly France** | 60 bureaux, 1 500 pers. | Associe national IT | Y2 Q1 |
| **Groupe Y Nexia** | 100+ bureaux | Direction digitale | Y2 Q2 |
| **Grant Thornton France** | 40 bureaux | Responsable Innovation | Y2 Q3 |

### Offre Enterprise

| Element | Detail |
|---------|--------|
| **Deploiement** | Cloud dedie (OVHcloud) ou on-premise (Docker) |
| **Branding** | White-label complet (cf. channel_partners.md) |
| **IA** | Instance Ollama dediee, fine-tuning sur donnees client (optionnel) |
| **SLA** | 99.9% uptime, support L3 <4h, restauration <2h |
| **Securite** | ISO 27001, pentest annuel, rapport SOC 2 |
| **Integration** | API complete + connecteurs ERP specifiques (SAP, Oracle) |
| **Formation** | Programme certifiant pour les equipes internes |

### Processus de vente Enterprise

| Etape | Duree | Acteur |
|-------|-------|--------|
| Identification + qualification | 2 semaines | Head of Sales |
| Premier rendez-vous (demo executive) | 1h | CEO + CTO |
| POC 10 utilisateurs | 4 semaines | Solutions Engineer |
| Retour POC + proposition commerciale | 2 semaines | Head of Sales |
| Negociation juridique (DSI + achats) | 4-6 semaines | CEO + juridique |
| Deploiement + formation | 6-8 semaines | Solutions Engineer |
| **Cycle total** | **4-6 mois** | |

### Recrutement cle

| Poste | Timeline | Mission |
|-------|----------|---------|
| Head of Sales / BD | Y2 Q1 | Pipeline enterprise, partenariats strategiques |
| Solutions Engineer | Y2 Q2 | POC, deploiement, integration |
| Customer Success Manager | Y2 Q3 | Onboarding, retention, upsell |

---

## 7. Partenariats internationaux

### Big 4 — Bureaux locaux

**Strategie** : Ne pas viser les Big 4 en frontal (cycle de vente 12-18 mois, procurement complexe). Viser leurs **departments PME/mid-market** ou leurs **spin-offs locales**.

| Cabinet | Cible | Approche |
|---------|-------|----------|
| Deloitte (via In Extenso) | Reseau PME France | White-label (cf. section 6) |
| PwC (via Landwell) | Departement fiscal PME | POC sur calcul IS automatise |
| KPMG (via KPMG Pulse) | Offre digitale PME | Partenariat technologique |
| EY (via EY Riverview) | Practice tax technology | Integration dans leur stack |

### Reseaux internationaux de cabinets

| Reseau | Presence | Approche |
|--------|----------|----------|
| **Kreston Global** | 120 pays, 25K pros | Contact bureau France → pilote |
| **Moore Global** | 110 pays, 30K pros | Partenariat regional Europe francophone |
| **Nexia International** | 120 pays, 36K pros | Via Groupe Y (membre francais) |
| **HLB International** | 150 pays, 40K pros | Contact direct bureau France |

**Modele** : Licence par pays membre, adaptation locale par le bureau national, support central FiscIA Pro.

---

## 8. Risques et mitigations

| Risque | Probabilite | Impact | Mitigation |
|--------|------------|--------|-----------|
| WK baisse ses prix de 50% | Faible | Eleve | Notre structure de cout est 50x plus legere ; impossible pour WK de descendre a 29 EUR |
| Reforme majeure IS (taux unique, suppression PME) | Moyenne | Moyen | Architecture modulaire, mise a jour en <48h ; renforce le besoin d'IA explicative |
| CNIL durcit les regles IA | Moyenne | Faible | Notre modele local est le plus conforme ; risque = avantage competitif |
| Echec integration Pennylane/Sage | Moyenne | Moyen | Diversifier les integrations ; API ouverte pour connecteurs tiers |
| Churn eleve Y1 (>5%/mois) | Moyenne | Eleve | Investir dans onboarding, CSM, communaute des le Q1 |
| Retard expansion Belgique/Luxembourg | Faible | Faible | Phase 2 non critique pour le P&L Y1 ; report sans impact strategique |
| Difficulte recrutement dev fiscal | Elevee | Moyen | Remote-first, salaires competitifs, formation interne sur le CGI |

---

## 9. Synthese financiere

### Projection de revenus par source

| Source | Y1 | Y2 | Y3 |
|--------|-----|-----|-----|
| France — Direct | 632K | 1 200K | 1 800K |
| France — Partenaires | 113K | 400K | 700K |
| Belgique + Luxembourg | - | 183K | 350K |
| Suisse + Quebec + Afrique | - | - | 130K |
| Enterprise / White-label | - | 317K | 1 520K |
| **Total ARR** | **745K** | **2 100K** | **4 500K** |

### Investissements cles par phase

| Poste | Y1 | Y2 | Y3 |
|-------|-----|-----|-----|
| Equipe (salaires) | 300K | 750K | 1 500K |
| Marketing + evenements | 100K | 180K | 250K |
| Partenariats + certifications | 110K | 150K | 200K |
| Infrastructure (cloud + securite) | 30K | 80K | 150K |
| **Total depenses** | **540K** | **1 160K** | **2 100K** |
| **Resultat net** | **+205K** | **+940K** | **+2 400K** |

### Besoins en financement

| Phase | Besoin | Source | Utilisation |
|-------|--------|--------|-------------|
| Y1 | 0 (bootstrap) | CA + tresorerie fondateurs | Produit + premiers clients |
| Y2 Q1 | 1-2M EUR | Seed (VC tech francais : Kima, Elaia, Breega) | Recrutement + expansion BeNeLux |
| Y3 Q1 | 5-8M EUR | Serie A (VC europeen : Index, Balderton, Partech) | Enterprise + international |

---

## 10. Indicateurs de decision (Go/No-Go)

### Gate Phase 1 → Phase 2 (fin Y1)

| Critere | Seuil Go | Seuil No-Go |
|---------|----------|-------------|
| Clients actifs | >700 | <400 |
| Churn mensuel | <4% | >6% |
| NPS | >35 | <20 |
| ARR | >500K EUR | <300K EUR |
| Unit economics (LTV/CAC) | >3x | <2x |

### Gate Phase 2 → Phase 3 (fin Y2)

| Critere | Seuil Go | Seuil No-Go |
|---------|----------|-------------|
| Clients France | >2 000 | <1 200 |
| Clients BeNeLux | >100 | <30 |
| ARR total | >1,5M EUR | <800K EUR |
| Equipe | >12 | <8 |
| Seed leve | Oui | Non (reporter Phase 3) |

---

*Prochaine revision : Septembre 2026 (Gate Phase 1)*
*Responsable : CEO + Board consultatif*
