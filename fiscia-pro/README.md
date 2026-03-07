# FiscIA Pro

FiscIA Pro est un moteur fiscal Python orienté IS France (Art. 219 CGI), liasse 2058-A et vérification mère-filiale (Art. 145 CGI).

## 1) Créer et activer l'environnement virtuel

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

## 2) Installer les dépendances

```bash
pip install -r requirements.txt
```

## 3) Exemples CLI

Recherche CGI:

```bash
python -m fiscia.cli search "taux reduit pme"
```

Calcul IS:

```bash
python -m fiscia.cli calc-is --ca 5000000 --capital-pp
```

Traitement liasse:

```bash
python -m fiscia.cli liasse \
  --siren 123456789 \
  --exercice-clos 2024-12-31 \
  --benefice-comptable 120000 \
  --perte-comptable 0 \
  --wi-is-comptabilise 10000 \
  --wg-amendes-penalites 2000 \
  --wm-interets-excedentaires 8000 \
  --wn-reintegrations-diverses 0 \
  --wv-regime-mere-filiale 30000 \
  --l8-qp-12pct 5000 \
  --ca 6500000 \
  --capital-pp
```

Vérification mère-filiale:

```bash
python -m fiscia.cli mere \
  --pct-capital 7 \
  --annees-detention 3 \
  --nominatifs \
  --pleine-propriete \
  --filiale-is \
  --dividende 50000 \
  --credit-impot 0
```

## Alias System (Backward Compatibility)

Le modèle accepte à la fois les noms canoniques et les anciens noms pour ne pas casser les clients existants:

- `wi_is_comptabilise` (alias legacy: `wi_is_commodite`)
- `wn_reintegrations_diverses` (alias legacy: `wn_gain_change_qp5`)
- `nominatifs` (alias legacy: `nominatif`)
- `dividende` (alias legacy: `dividende_brut`)

Recommandation: utilisez toujours les noms canoniques dans tout nouveau script, et gardez les alias uniquement pour la transition.

## 4) Lancer FastAPI

```bash
uvicorn fiscia.app:app --reload --host 0.0.0.0 --port 8000
```

## 5) Lancer Docker Compose

```bash
docker compose up -d
```

## 6) Lancer les tests

```bash
pytest -q
```

## 7) CI GitHub Actions

Le workflow `.github/workflows/ci.yml` s'exécute sur push/PR vers `main`:
- setup Python 3.11,
- installation des dépendances + outils dev (`pytest`, `pytest-cov`, `ruff`),
- exécution des tests avec couverture,
- lint Ruff.

⚖️ Disclaimer : la présente réponse est fournie à titre indicatif sur la base des informations communiquées.
Elle ne constitue pas un avis fiscal engageant la responsabilité du cabinet.
Toute décision doit faire l’objet d’une analyse personnalisée d’un professionnel qualifié.

Migration note – Depuis la version X.Y, le modèle accepte les anciens noms de champs (wi_is_commodite, wn_gain_change_qp5, nominatif, dividende_brut) grâce aux alias. Nous vous recommandons toutefois d’utiliser les noms canoniques (wi_is_comptabilise, wn_reintegrations_diverses, nominatifs, dividende) dans vos nouveaux scripts.
