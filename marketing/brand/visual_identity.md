# Identité Visuelle — FiscIA Pro

> Document interne. Dernière mise à jour : mars 2026.

---

## 1. Palette de couleurs

### Couleur principale — Bleu FiscIA

Le bleu est la couleur de la confiance, de la rigueur et de l'institutionnel en France. C'est la couleur de la DGFIP, des banques et des logiciels comptables. FiscIA Pro utilise une échelle de 10 nuances de bleu comme couleur primaire.

| Token | Hex | Usage |
|---|---|---|
| `primary-50` | `#eff6ff` | Arrière-plans hero, survol léger |
| `primary-100` | `#dbeafe` | Badges, initiales d'équipe, hover cards |
| `primary-200` | `#bfdbfe` | Bordures actives, timeline |
| `primary-300` | `#93c5fd` | États intermédiaires |
| `primary-400` | `#60a5fa` | Icônes sur fond sombre (nav slate-900) |
| `primary-500` | `#3b82f6` | Liens, accents secondaires |
| `primary-600` | **`#2563eb`** | **Couleur héroïque.** Boutons CTA, logo, titres marqués, sélection de texte. |
| `primary-700` | `#1d4ed8` | Hover sur CTA, boutons pressés |
| `primary-800` | `#1e40af` | Texte sur fond clair haute importance |
| `primary-900` | `#1e3a8a` | Texte haute densité |
| `primary-950` | `#172554` | Arrière-plans très sombres |

**Règle** : `primary-600` (#2563eb) est la couleur d'ancrage. C'est elle qui identifie FiscIA Pro. Ne jamais la remplacer par une autre teinte dans les contextes de marque.

### Couleurs sémantiques

| Couleur | Cercle fond | Cercle icône | Usage |
|---|---|---|---|
| **Vert** | `green-100` | `green-600` | Validation, check marks, éligibilité, succès |
| **Rouge** | `red-100` | `red-600` | Alertes, coûts/pertes, conditions manquantes |
| **Ambre** | `amber-100` | `amber-600` | Sécurité, chiffrement, avertissements modérés |
| **Violet** | `purple-100` | `purple-600` | Audit trail, traçabilité, conformité |
| **Jaune** | `yellow-400` | — | Badges (« Le plus populaire »), étoiles de notation |

### Couleurs neutres — Slate

| Token | Usage |
|---|---|
| `slate-900` | Titres principaux, texte corps dark |
| `slate-700` | Texte secondaire fort |
| `slate-600` | Texte corps standard |
| `slate-500` | Texte tertiaire, descriptions courtes |
| `slate-400` | Captions, métadonnées, « Pro » dans le logotype |
| `slate-300` | Bordures désactivées, éléments exclus |
| `slate-200` | Bordures de cards, séparateurs |
| `slate-100` | Séparateurs légers dans les tableaux |
| `slate-50` | Arrière-plans de sections alternées |

### Sélection de texte

```css
::selection {
  background-color: #2563eb; /* primary-600 */
  color: white;
}
```

---

## 2. Typographie

### Police principale — Inter

- **Usage** : tout le texte hors code (titres, corps, navigation, boutons, formulaires).
- **Variable CSS** : `--font-inter`
- **Subsets** : `latin`, `latin-ext` (support complet des diacritiques français : é, è, ê, ë, à, ù, ç, ô, î, etc.)
- **Display** : `swap` (performance — texte visible immédiatement)

**Pourquoi Inter** : police géométrique sans-serif optimisée pour les écrans. Neutralité professionnelle sans froideur. Lisibilité exceptionnelle à toutes les tailles. Support complet du français via latin-ext.

### Police code — JetBrains Mono

- **Usage** : exemples API, calculs fiscaux dans les terminaux mock-up, lignes de commande.
- **Variable CSS** : `--font-jetbrains`
- **Subset** : `latin`
- **Display** : `swap`

**Pourquoi JetBrains Mono** : monospace technique de référence. Ligatures optionnelles. Signal de compétence technique — les fiscalistes voient que l'outil est construit par des ingénieurs.

### Hiérarchie typographique

| Élément | Taille | Poids | Couleur |
|---|---|---|---|
| H1 (hero) | `text-4xl` → `text-6xl` (responsive) | `font-bold` | `slate-900` |
| H2 (section) | `text-2xl` → `text-3xl` | `font-bold` | `slate-900` |
| H3 (card) | `text-lg` | `font-semibold` | `slate-900` |
| Corps | `text-base` → `text-lg` | `font-normal` | `slate-600` |
| Caption | `text-sm` | `font-normal` | `slate-500` |
| Eyebrow | `text-sm` | `font-semibold`, `uppercase`, `tracking-wider` | `primary-600` |
| Badge | `text-xs` | `font-medium` | Variable |
| Code | `text-sm` | `font-mono` | `slate-300` sur `slate-950` |

---

## 3. Logo

### Construction

Le logo FiscIA Pro est composé de deux éléments :

**La marque « F »** :
- Forme : carré aux coins arrondis (`rounded-lg`, ~8px radius)
- Fond : `primary-600` (#2563eb)
- Lettre : « F » majuscule, blanc, bold, centré
- Taille standard : 36×36px (header), 32×32px (footer)

**Le logotype** :
- « FiscIA » en `primary-600`, `font-bold`
- Espace insécable
- « Pro » en `slate-400`, `font-normal`

### Variantes

| Contexte | Marque | Logotype | Fond |
|---|---|---|---|
| Header (clair) | F blanc sur primary-600 | FiscIA primary-600 + Pro slate-400 | Blanc/transparent |
| Footer (clair) | F blanc sur primary-600 | FiscIA primary-600 + Pro slate-400 | slate-50 |
| Fond sombre | F blanc sur primary-600 | FiscIA blanc + Pro slate-400 | slate-900+ |
| Favicon | F blanc sur primary-600 | — | — |

### Règles d'utilisation

- **Espacement minimum** : la marge autour du logo doit être au moins égale à la hauteur de la lettre « F ».
- **Taille minimum** : marque seule 24×24px, logotype complet 120px de large.
- **Ne jamais** : déformer les proportions, changer les couleurs, ajouter des effets (ombre portée, dégradé sur le F), séparer la marque du logotype dans les contextes de marque.

### Action requise

> Le logo actuel est rendu en HTML/CSS. Un fichier SVG et des exports PNG (1x, 2x, 3x) doivent être créés pour les usages hors-web (présentations, documents imprimés, signatures email, réseaux sociaux).

---

## 4. Iconographie

### Style

- **Bibliothèque** : Heroicons (outline)
- **ViewBox** : 24×24
- **Stroke width** : 1.5 (features, illustrations) ou 2 (check marks, actions)
- **Rendu** : SVG inline (zéro dépendance externe)

### Couleurs par contexte

| Contexte | Couleur icône |
|---|---|
| Fonctionnalités (cards) | `text-primary-600` |
| Check marks (listes) | `text-green-500` |
| Croix (exclusions) | `text-slate-300` |
| Trust badges | Cercle coloré + icône assortie (green/blue/amber/purple) |
| Navigation (flèches, menus) | `text-slate-400` → `text-slate-600` |
| Footer (réseaux sociaux) | `text-slate-400` hover `text-slate-600` |

### Règle

Ne pas mixer les styles d'icônes. Rester exclusivement sur Heroicons outline. Si une icône spécifique n'existe pas dans Heroicons, créer un SVG custom qui respecte le même stroke width (1.5) et viewBox (24×24).

---

## 5. Patterns d'interface

### Cards

```
rounded-xl
border border-slate-200
p-8
bg-white
hover:shadow-lg transition-shadow
```

Utilisées pour : fonctionnalités, témoignages, membres de l'équipe, FAQ items.

### Terminal mock-up

```
Container : rounded-xl border border-slate-200 bg-slate-950 shadow-2xl overflow-hidden
Barre titre : bg-slate-900 border-b border-slate-800 px-4 py-3
  - 3 dots : h-3 w-3 rounded-full (bg-red-500, bg-yellow-500, bg-green-500)
  - Label : text-xs text-slate-500 font-mono
Corps : p-6 font-mono text-sm leading-relaxed
  - Prompt : text-green-400 ("$")
  - Sortie : text-slate-300 / text-slate-400
  - Valeurs : text-green-400 (montants), text-blue-400 (régimes), text-yellow-400 (totaux)
```

Signal de marque fort. Montre que FiscIA Pro est un outil technique construit par des ingénieurs, pas un template SaaS générique.

### Boutons CTA

| Niveau | Style |
|---|---|
| **Primaire** | `rounded-lg bg-primary-600 text-white hover:bg-primary-700 shadow-lg shadow-primary-600/25` |
| **Secondaire** | `rounded-lg border border-slate-300 bg-white text-slate-700 hover:bg-slate-50` |
| **Ghost** | `text-primary-600 font-semibold hover:underline` |

### Héro gradient

```
bg-gradient-to-b from-primary-50 to-white
```

Utilisé en haut de chaque page principale. Crée une transition douce du bleu très léger vers le blanc.

### Décorations de fond

```
Cercle 1 : absolute -top-1/2 -right-1/4 w-[800px] h-[800px] rounded-full bg-primary-100/50 blur-3xl
Cercle 2 : absolute -bottom-1/2 -left-1/4 w-[600px] h-[600px] rounded-full bg-blue-100/50 blur-3xl
```

Subtils, jamais dominants. Donnent de la profondeur sans distraire du contenu.

### Pricing card mise en avant

```
bg-primary-600 text-white ring-4 ring-primary-600 ring-offset-2 shadow-2xl
Badge : absolute -top-3 bg-yellow-400 text-yellow-900 rounded-full
```

---

## 6. Direction visuelle

### Approche générale

FiscIA Pro adopte une esthétique **abstraite et géométrique**. Pas de photographies de personnes. Pas d'illustrations figuratives. Les visuels sont des interfaces (terminaux, cards de données, tableaux) qui montrent le produit en action.

### Représentation de l'équipe

Les membres de l'équipe sont représentés par leurs initiales dans un cercle coloré (`bg-primary-100`, `text-primary-700`), jamais par des photos. Cela renforce le positionnement « outil » plutôt que « personnalité ».

### Quand introduire la photographie

La photographie peut être introduite pour :
- **Événements** : photos de stands aux congrès (Congrès de l'Ordre, IFEC)
- **Presse** : portraits des fondateurs pour les interviews médias
- **Études de cas** : photos de cabinets clients (avec accord écrit)

Style photographique si utilisé : lumière naturelle, environnement de bureau professionnel, tons froids (bleu/gris), jamais de poses forcées ou de stock photos génériques.

### Illustrations de fonctionnalités

Quand aucun exemple de code n'est disponible, utiliser un placeholder visuel :

```
rounded-xl bg-gradient-to-br from-primary-100 to-primary-50
border border-primary-200
Icône centrale : h-16 w-16 rounded-full bg-primary-600, icône blanche
Titre + sous-titre en primary-900 / primary-600
```

---

## 7. Grille et espacement

### Largeur maximale

```
max-w-7xl (1280px) mx-auto px-6
```

Toutes les sections de contenu sont contraintes à 1280px de large avec un padding horizontal de 24px (px-6).

### Rythme vertical

```
Sections : py-20 (80px haut + bas)
Section headers : mb-16 (64px avant le contenu)
Cards gap : gap-8 (32px)
```

### Grilles responsives

| Breakpoint | Nom Tailwind | Largeur | Usage type |
|---|---|---|---|
| Mobile | (défaut) | < 640px | 1 colonne, stack vertical |
| `sm` | 640px+ | 2 colonnes pour les cards |
| `md` | 768px+ | Navigation desktop, grilles 2-3 colonnes |
| `lg` | 1024px+ | Grilles 3-4 colonnes |

### Header sticky

```
sticky top-0 z-50
border-b border-slate-200
bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/80
```

Semi-transparent avec backdrop-blur pour un effet de profondeur moderne.

---

## 8. Trust badges

Trois badges constants apparaissent en footer :

| Badge | Fond | Texte | Ring |
|---|---|---|---|
| RGPD | `bg-green-50` | `text-green-700` | `ring-green-200` |
| Made in France | `bg-blue-50` | `text-blue-700` | `ring-blue-200` |
| SSL/TLS | `bg-amber-50` | `text-amber-700` | `ring-amber-200` |

Format : `inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium ring-1 ring-inset`.

Ces badges doivent apparaître sur toute page marketing, email transactionnel et document de vente.
