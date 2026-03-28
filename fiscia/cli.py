#!/usr/bin/env python
"""
FiscIA Pro CLI - Interface en ligne de commande pour le moteur fiscal IS.
"""
from decimal import Decimal

import click

from fiscia.cgi_search import search as cgi_search
from fiscia.guardrails import enforce_guardrails
from fiscia.is_calculator import DISCLAIMER, ISCalculator
from fiscia.mere_fi_check import verifier_mere_filiale
from fiscia.models import Liasse2058AInput


@click.group()
def cli():
    """FiscIA Pro - Moteur fiscal IS francais."""
    pass


@cli.command()
@click.argument("query")
@click.option("--top", default=5, help="Nombre de resultats")
def search(query: str, top: int):
    """Recherche dans le catalogue CGI."""
    results = cgi_search(query, top_n=top)
    if not results:
        click.echo("Aucun resultat.")
        return
    for i, r in enumerate(results, 1):
        click.echo(f"\n--- Resultat {i} (score: {r['score']}) ---")
        click.echo(f"Article : {r['article']}")
        click.echo(f"Titre   : {r['title']}")
        click.echo(f"Version : {r['version']}")
        click.echo(f"Extrait : {r['excerpt']}")
    click.echo(f"\nDisclaimer: {DISCLAIMER}")


@cli.command("calc-is")
@click.option("--ca", type=float, required=True, help="CA HT en EUR")
@click.option("--capital-pp", is_flag=True, help="Capital >= 75% personnes physiques")
def calc_is(ca: float, capital_pp: bool):
    """Calcul IS sur un RF fictif de 100 000 EUR."""
    calc = ISCalculator()
    rf = Decimal("100000")
    is_total, regime, t15, t25 = calc.calcul_is(rf, Decimal(str(ca)), capital_pp)

    click.echo(f"\n{'='*50}")
    click.echo("CALCUL IS - Art. 219 CGI (LFI 2024)")
    click.echo(f"{'='*50}")
    click.echo(f"Resultat fiscal       : {rf:>12} EUR")
    click.echo(f"Regime                : {regime}")
    click.echo(f"Tranche 15% (PME)     : {t15:>12} EUR")
    click.echo(f"Tranche 25%           : {t25:>12} EUR")
    click.echo(f"IS TOTAL DU           : {is_total:>12} EUR")
    acompte = (is_total / 4).quantize(Decimal("0.01"))
    click.echo(f"Acompte trimestriel   : {acompte:>12} EUR")
    click.echo("Dates acomptes : 15/03, 15/06, 15/09, 15/12")
    click.echo(f"\nDisclaimer: {DISCLAIMER}")


@cli.command()
@click.option("--siren", required=True, help="SIREN (9 chiffres)")
@click.option("--exercice", required=True, help="Date cloture YYYY-MM-DD")
@click.option("--benefice", type=float, default=0, help="WA Benefice comptable")
@click.option("--perte", type=float, default=0, help="WQ Perte comptable")
@click.option("--wi", type=float, default=0, help="WI IS comptabilise en charges")
@click.option("--wg", type=float, default=0, help="WG Amendes et penalites")
@click.option("--wm", type=float, default=0, help="WM Interets excedentaires CC")
@click.option("--wn", type=float, default=0, help="WN Reintegrations diverses")
@click.option("--wv", type=float, default=0, help="WV Deduction mere-filiale")
@click.option("--l8", type=float, default=0, help="L8 QP 12% PV LT")
@click.option("--ca", type=float, required=True, help="CA HT en EUR")
@click.option("--capital-pp", is_flag=True, help="Capital >= 75% PP")
def liasse(siren, exercice, benefice, perte, wi, wg, wm, wn, wv, l8, ca, capital_pp):
    """Traitement complet d'une liasse 2058-A."""
    liasse_input = Liasse2058AInput(
        siren=siren,
        exercice_clos=exercice,
        benefice_comptable=Decimal(str(benefice)),
        perte_comptable=Decimal(str(perte)),
        wi_is_comptabilise=Decimal(str(wi)),
        wg_amendes_penalites=Decimal(str(wg)),
        wm_interets_excedentaires=Decimal(str(wm)),
        wn_reintegrations_diverses=Decimal(str(wn)),
        wv_regime_mere_filiale=Decimal(str(wv)),
        l8_qp_12pct=Decimal(str(l8)),
    )

    calc = ISCalculator()
    result = calc.process_liasse(liasse_input, Decimal(str(ca)), capital_pp)

    output = (
        f"\n{'='*50}\n"
        f"LIASSE 2058-A - RESULTAT FISCAL (LFI 2024)\n"
        f"{'='*50}\n"
        f"SIREN                 : {siren}\n"
        f"Exercice clos         : {exercice}\n"
        f"Resultat comptable    : {result.details.get('resultat_comptable', 0):>12} EUR\n"
        f"Total reintegrations  : {result.details.get('total_reintegrations', 0):>12} EUR\n"
        f"Total deductions      : {result.details.get('total_deductions', 0):>12} EUR\n"
        f"RF brut               : {result.rf_brut:>12} EUR\n"
        f"RF net                : {result.rf_net:>12} EUR\n"
        f"{'─'*50}\n"
        f"Regime                : {result.regime}\n"
        f"Tranche 15%           : {result.details.get('tranche_15pct', 0):>12} EUR\n"
        f"Tranche 25%           : {result.details.get('tranche_25pct', 0):>12} EUR\n"
        f"IS TOTAL DU           : {result.is_total:>12} EUR\n"
        f"Acompte trimestriel   : {result.acompte_trimestriel:>12} EUR\n"
        f"{'─'*50}\n"
        f"Disclaimer: {DISCLAIMER}"
    )

    # Guardrail validation
    context = {
        "pme_checked": True,
        "confidential": True,
        "module": "liasse",
        "mere_conditions_present": wv > 0,
    }
    enforce_guardrails(output, context)
    click.echo(output)


@cli.command()
@click.option("--pct-capital", type=float, required=True, help="% du capital detenu")
@click.option("--annees", type=int, required=True, help="Annees de detention")
@click.option("--nominatif", is_flag=True, help="Titres nominatifs")
@click.option("--pleine-propriete", is_flag=True, help="Pleine propriete")
@click.option("--filiale-is", is_flag=True, help="Filiale soumise IS")
@click.option("--paradis-fiscal", is_flag=True, help="Filiale dans un ETNC")
@click.option("--dividende", type=float, default=0, help="Dividende brut recu")
@click.option("--credit-impot", type=float, default=0, help="Credit d'impot associe")
def mere(pct_capital, annees, nominatif, pleine_propriete, filiale_is, paradis_fiscal, dividende, credit_impot):
    """Verification regime mere-filiale Art. 145 CGI."""
    params = {
        "pct_capital": pct_capital,
        "annees_detention": annees,
        "nominatifs": nominatif,
        "pleine_propriete": pleine_propriete,
        "filiale_is": filiale_is,
        "paradis_fiscal": paradis_fiscal,
        "dividende": dividende,
        "credit_impot": credit_impot,
    }
    result = verifier_mere_filiale(params)

    output = f"\n{'='*50}\n"
    output += "VERIFICATION ART. 145 CGI - MERE-FILIALE (LFI 2024)\n"
    output += f"{'='*50}\n"

    for cond, val in result["conditions"].items():
        status = "OUI" if val else "NON"
        output += f"  {cond:30s} : {status}\n"

    output += f"{'─'*50}\n"

    if result["eligible"]:
        output += "RESULTAT : ELIGIBLE\n"
        output += f"Deduction WV          : {result['deduction_WV']:>12.2f} EUR\n"
        output += f"Reintegration WN (QP 5%) : {result['reintegration_WN_qp5']:>9.2f} EUR\n"
        output += f"Impact RF net         : {result['impact_rf_net']:>12.2f} EUR\n"
        output += f"Base legale           : {result['base_legale']}\n"
    else:
        output += "RESULTAT : NON ELIGIBLE\n"
        output += f"Conditions echouees   : {', '.join(result['conditions_echouees'])}\n"
        output += f"Consequence           : {result['consequence']}\n"
        output += f"Alerte                : {result['alerte']}\n"

    output += f"\nDisclaimer: {DISCLAIMER}"

    context = {
        "pme_checked": True,
        "confidential": True,
        "module": "mere",
        "mere_conditions_present": result["eligible"],
    }
    enforce_guardrails(output, context)
    click.echo(output)


if __name__ == "__main__":
    cli()
