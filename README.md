# FiscIA Pro — Moteur Fiscal IS Francais

Moteur de calcul d'Impot sur les Societes conforme au CGI (Art. 219, Art. 145, liasse 2058-A).

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate   # Linux/Mac
# .venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

## CLI

```bash
# Recherche CGI
python -m fiscia.cli search "taux reduit pme"

# Calcul IS (RF fictif 100k)
python -m fiscia.cli calc-is --ca 5000000 --capital-pp

# Liasse 2058-A complete
python -m fiscia.cli liasse \
  --siren 123456789 --exercice 2024-12-31 \
  --benefice 120000 --wi 10000 --wg 2000 --wm 8000 \
  --wv 30000 --l8 5000 --ca 6500000 --capital-pp

# Verification mere-filiale Art. 145
python -m fiscia.cli mere \
  --pct-capital 7 --annees 3 --nominatif --pleine-propriete \
  --filiale-is --dividende 50000
```

## API (FastAPI)

```bash
uvicorn fiscia.app:app --reload --port 8000
# Docs: http://localhost:8000/docs
```

Exemples curl:

```bash
curl http://localhost:8000/health

curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "taux reduit pme"}'

curl -X POST http://localhost:8000/calc-is \
  -H "Content-Type: application/json" \
  -d '{"ca": 5000000, "capital_pp": true}'

curl -X POST http://localhost:8000/mere \
  -H "Content-Type: application/json" \
  -d '{"pct_capital": 7, "annees_detention": 3, "nominatifs": true, "pleine_propriete": true, "filiale_is": true, "paradis_fiscal": false, "dividende": 50000, "credit_impot": 0}'
```

## Docker

```bash
docker compose up -d
# Backend: http://localhost:8000
# Ollama stays local — never expose port 11434 externally
```

## Tests

```bash
pytest -q
```

## CI

GitHub Actions runs on push/PR to main: pytest + ruff lint.

## Ollama (local model)

```bash
ollama create fiscia-fiscal-is-v3 -f Modelfile.fiscal_IS_v3
```

Data stays on-premise. Never expose the Ollama port to the internet.
