"""Tests de la recherche CGI."""
from fiscia.cgi_search import search


def test_search_mere_filiale():
    """Requete mere-filiale doit retourner Art. 145 CGI."""
    results = search("quote-part 5% mere-filiale")
    articles = [r["article"] for r in results]
    assert "Art. 145 CGI" in articles


def test_search_taux_reduit_pme():
    """Requete taux reduit PME doit retourner Art. 219 I-b CGI."""
    results = search("taux reduit pme")
    articles = [r["article"] for r in results]
    assert "Art. 219 I-b CGI" in articles


def test_search_returns_scores():
    """Chaque resultat doit avoir un score entre 0 et 1."""
    results = search("impot societes")
    for r in results:
        assert 0 <= r["score"] <= 1
        assert "version" in r
