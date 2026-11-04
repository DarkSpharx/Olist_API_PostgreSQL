"""Fourni — compare donnees_csv.py et donnees_pg.py fonction par fonction (J2, mission 9).

Lancement :  py verifier_sources.py   (macOS/Linux : python3 verifier_sources.py)
Chaque ligne doit afficher ✅. Les deux sources doivent donner EXACTEMENT les mêmes chiffres.
"""
import json

import donnees_csv
import donnees_pg


def normaliser(valeur):
    """Convertit les Decimal de PostgreSQL en float pour pouvoir comparer."""
    return json.loads(json.dumps(valeur, default=float))


ESSAIS = [
    ("indicateurs()", lambda d: d.indicateurs()),
    ("ventes_mensuelles()", lambda d: d.ventes_mensuelles()),
    ("ventes_mensuelles('2017-01', '2017-12')", lambda d: d.ventes_mensuelles("2017-01", "2017-12")),
    ("top_categories(10)", lambda d: d.top_categories(10)),
    ("top_categories(50)", lambda d: d.top_categories(50)),
    ("etat('SP')", lambda d: d.etat("SP")),
    ("etat('RR')", lambda d: d.etat("RR")),
    ("etat('XX')", lambda d: d.etat("XX")),
]

reussis = 0
for intitule, appel in ESSAIS:
    try:
        identique = normaliser(appel(donnees_csv)) == normaliser(appel(donnees_pg))
        print(("✅ " if identique else "❌ ") + intitule + ("" if identique else "  → résultats différents"))
    except Exception as erreur:
        identique = False
        print(f"❌ {intitule}  → erreur : {type(erreur).__name__} : {erreur}")
    reussis += identique

print(f"\nBilan : {reussis}/{len(ESSAIS)} fonctions identiques")
