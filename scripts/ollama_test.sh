#!/bin/bash
# FiscIA Pro — Ollama Test Prompts
# Usage: bash scripts/ollama_test.sh
# Requires: ollama running with a cloud model (deepseek-v3.1:671b-cloud, qwen3-coder:480b-cloud, etc.)

MODEL="${OLLAMA_MODEL:-deepseek-v3.1:671b-cloud}"

echo "=============================================="
echo "FiscIA Pro — Test Ollama ($MODEL)"
echo "=============================================="

# --- TEST 1: IS PME Calculation ---
echo ""
echo ">>> TEST 1: Calcul IS PME"
echo "-------------------------------------------"
ollama run "$MODEL" "$(cat <<'PROMPT'
Tu es FiscIA Local IS, le moteur fiscal embarque de FiscIA Pro.
Contexte: Art. 219 CGI, LFI 2024. Taux normal 25%. Taux reduit PME 15% sur premiers 42 500 EUR si CA HT < 10M EUR et capital >= 75% PP.

Cas: SA DUPONT, CA = 5 M EUR, capital 100% personnes physiques.
Benefice fiscal 2024 : 80 000 EUR.

Calcule l'IS du avec le detail des tranches.

Format obligatoire:
-----------------------------------------------
CALCUL IS - Exercice 2024
Resultat Fiscal (ligne XN) : [montant]
Regime applicable : [PME taux reduit / Normal]
-----------------------------------------------
Tranche 15% (PME) : [montant] x 15% = [resultat]
Tranche 25%       : [montant] x 25% = [resultat]
IS TOTAL DU        :              [montant]
-----------------------------------------------
Acomptes estimes : [IS/4] x 4 versements
Dates : 15/03, 15/06, 15/09, 15/12
-----------------------------------------------
Reponse indicative. Validation professionnelle requise.
PROMPT
)"

# --- TEST 2: Reintegrations 2058-A ---
echo ""
echo ">>> TEST 2: Reintegrations liasse 2058-A"
echo "-------------------------------------------"
ollama run "$MODEL" "$(cat <<'PROMPT'
Tu es FiscIA Liasse, l'assistant de determination du resultat fiscal IS.
Reference: formulaire DGFiP 2058-A, LFI 2024.

Cas: La SARL MARTIN (IS de plein droit) a comptabilise en charges :
- IS de l'exercice = 22 000 EUR (compte 695)
- Amendes DGFiP (majorations) = 3 500 EUR
- Interets CC associe au-dela du TMP BdF = 8 000 EUR
- TVS = 4 200 EUR

Pour chaque charge, indique:
1. Le code ligne 2058-A exact
2. Le sens (REINTEGRATION ou DEDUCTION)
3. L'article CGI applicable
4. Le montant a reintegrer
5. L'impact sur le RF

Format par charge:
-----------------------------------------------
TRAITEMENT 2058-A
Ligne : [CODE]  |  Sens : [+ REINTEGRATION]
Montant : [X EUR]  |  Art. CGI : [numero]
Impact RF : RF augmente de [X EUR]
-----------------------------------------------

Puis donne le total des reintegrations.
Reponse indicative. Validation professionnelle requise.
PROMPT
)"

# --- TEST 3: Regime Mere-Filiale Art. 145 ---
echo ""
echo ">>> TEST 3: Regime mere-filiale Art. 145 CGI"
echo "-------------------------------------------"
ollama run "$MODEL" "$(cat <<'PROMPT'
Tu es FiscIA Art145, le verificateur du regime mere-filiale.
Reference: Art. 145 et 216 CGI, LFI 2024.

Cas: SA ALPHA detient 7% du capital de SA BETA (filiale soumise IS de plein droit) depuis 3 ans. Titres nominatifs en pleine propriete. BETA est etablie en France (hors ETNC).
Dividendes recus de BETA : 50 000 EUR. Pas de credit d'impot.

Verifie les 6 conditions cumulatives Art. 145 CGI une par une.
Si eligible, calcule:
- La deduction WV (dividende brut)
- La reintegration WN (quote-part 5% de frais et charges)
- L'impact RF net

Format:
-----------------------------------------------
VERIFICATION ART. 145 CGI - REGIME MERE-FILIALE (LFI 2024)
-----------------------------------------------
Condition 1 (>= 5% capital)      : [OUI/NON]
Condition 2 (>= 2 ans detention)  : [OUI/NON]
Condition 3 (titres nominatifs)   : [OUI/NON]
Condition 4 (pleine propriete)    : [OUI/NON]
Condition 5 (filiale IS)          : [OUI/NON]
Condition 6 (hors ETNC)           : [OUI/NON]
-----------------------------------------------
RESULTAT : [ELIGIBLE / NON ELIGIBLE]
Deduction WV    : [montant]
Reintegration WN (QP 5%) : [montant]
Impact RF net   : [montant]
-----------------------------------------------
Reponse indicative. Validation professionnelle requise.
PROMPT
)"

echo ""
echo "=============================================="
echo "Tests termines."
echo "=============================================="
