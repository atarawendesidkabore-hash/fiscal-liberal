"""Stripe plans and product limits."""

PLANS = {
    "starter": {
        "price_eur": 49,
        "cible": "Independant / petite structure",
        "stripe_price_id": "price_starter_monthly",
        "limites": {
            "requetes_ia_par_mois": 200,
            "dossiers_clients": 10,
            "liasses_2058a": 5,
            "modules": ["recherche_cgi", "veille"],
            "ollama_local": False,
            "export_pdf": True,
        },
    },
    "pro": {
        "price_eur": 149,
        "cible": "Cabinet 1-5 associes",
        "stripe_price_id": "price_pro_monthly",
        "limites": {
            "requetes_ia_par_mois": 1000,
            "dossiers_clients": 100,
            "liasses_2058a": -1,
            "modules": [
                "recherche_cgi",
                "veille",
                "liasse_2058a",
                "is_calculator",
                "mere_filiale",
                "clients",
            ],
            "ollama_local": True,
            "export_pdf": True,
            "api_access": False,
        },
    },
    "cabinet": {
        "price_eur": 399,
        "cible": "Cabinet structure 5-20 associes",
        "stripe_price_id": "price_cabinet_monthly",
        "limites": {
            "requetes_ia_par_mois": -1,
            "dossiers_clients": -1,
            "liasses_2058a": -1,
            "users_inclus": 10,
            "modules": "all",
            "ollama_local": True,
            "api_access": True,
            "support_prioritaire": True,
            "sso": True,
        },
    },
}

