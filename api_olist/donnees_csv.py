"""Accès aux données — version 1 : le fichier CSV exporté lundi (J1).

Ce module LIT et CALCULE. Il ne sait rien du web : c'est main.py qui expose les résultats.
Les zones « ... » sont à compléter (méthode dans la consigne, page 5).
"""
from pathlib import Path

import pandas as pd

from erreurs import SourceIndisponible

FICHIER = Path(__file__).parent / "data" / "ventes_olist.csv"
_ventes = None  # le fichier est lu une seule fois, au premier appel


def charger() -> pd.DataFrame:
    """Fourni — lit le CSV une seule fois et garde la table en mémoire."""
    global _ventes
    if _ventes is None:
        if not FICHIER.exists():
            raise SourceIndisponible(f"Fichier introuvable : {FICHIER}")
        _ventes = pd.read_csv(FICHIER, dtype={"mois": str, "customer_state": str},
                              parse_dates=["order_purchase_timestamp"])
    return _ventes


def source() -> str:
    """Fourni."""
    return "csv"


def compter_lignes() -> int:
    """Fourni."""
    return len(charger())


def indicateurs() -> dict:
    """Mission 2 — FOURNI : lis-le ligne à ligne, c'est le modèle des fonctions suivantes."""
    v = charger()
    nb_commandes = int(v["order_id"].nunique())
    ca_total = float(v["montant"].sum())
    return {
        "nb_lignes": len(v),
        "nb_commandes": nb_commandes,
        "ca_total": round(ca_total, 2),
        "panier_moyen": round(ca_total / nb_commandes, 2),
    }


def ventes_mensuelles(debut: str | None = None, fin: str | None = None) -> list[dict]:
    """Mission 3 — CA et nombre de commandes par mois, entre debut et fin (inclus)."""
    v = charger()

    # 1. Filtrer sur la période. debut et fin sont des textes « AAAA-MM », ou None.
    if debut is not None:
        v = v[v["mois"] >= debut]
    if fin is not None:
        v = v[...]

    # 2. Regrouper par mois : CA = somme de montant ; commandes = nombre de order_id DISTINCTS
    m = (v.groupby("mois")
          .agg(ca=("montant", ...), nb_commandes=("order_id", ...))
          .reset_index()
          .sort_values("mois"))

    # 3. Convertir en liste de dictionnaires aux types Python simples (str, float, int)
    return [{"mois": r.mois, "ca": round(float(r.ca), 2), "nb_commandes": int(...)}
            for r in m.itertuples()]


def top_categories(n: int = 10) -> list[dict]:
    """Mission 4 — les n catégories au plus fort CA, avec leur part du CA total (en %)."""
    v = charger()

    # 1. CA total, pour calculer les parts
    total = ...

    # 2. CA par catégorie, trié du plus grand au plus petit, puis les n premiers
    cat = v.groupby("categorie")["montant"].sum().sort_values(ascending=...).head(...)

    # 3. Une liste de dictionnaires : categorie, ca (arrondi à 2), part_ca (en %, arrondi à 2)
    return [{"categorie": nom, "ca": ..., "part_ca": ...}
            for nom, ca in cat.items()]


def etat(code: str) -> dict | None:
    """Mission 5 — chiffres d'un État brésilien (ex. « SP ») ; None s'il n'a aucune vente."""
    v = charger()

    # 1. Garder les lignes de l'État demandé
    e = v[v["customer_state"] == ...]

    # 2. Aucune ligne → renvoyer None (main.py transformera ce None en erreur 404)
    if e.empty:
        return ...

    # 3. Calculer et renvoyer les 4 champs
    ca = float(e["montant"].sum())
    return {
        "etat": code,
        "ca": ...,
        "nb_commandes": ...,
        "part_ca": ...,  # part du CA total, en %, arrondie à 2 décimales
    }
