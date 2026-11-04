"""Accès aux données — version 2 : la base PostgreSQL « olist » (J2).

Mêmes fonctions, mêmes noms, mêmes résultats que donnees_csv.py :
main.py n'a pas besoin de savoir d'où viennent les données.
Les zones « ... » sont à compléter (méthode dans la consigne, page 7).
"""
import os

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

from erreurs import SourceIndisponible

load_dotenv()  # lit le fichier .env (jamais versionné)


def _lire(requete: str, parametres: dict | None = None) -> list[dict]:
    """Fourni — ouvre une connexion, exécute UNE requête paramétrée, renvoie les lignes.

    Chaque ligne est un dictionnaire : ligne["ca"], ligne["mois"]...
    """
    try:
        with psycopg.connect(
            host=os.getenv("PGHOST", "localhost"),
            port=int(os.getenv("PGPORT", "5432")),
            dbname=os.getenv("PGDATABASE", "olist"),
            user=os.getenv("PGUSER"),
            password=os.getenv("PGPASSWORD"),
            connect_timeout=5,
            row_factory=dict_row,
        ) as conn:
            return conn.execute(requete, parametres).fetchall()
    except psycopg.OperationalError as erreur:
        raise SourceIndisponible("Base PostgreSQL injoignable") from erreur


def source() -> str:
    """Fourni."""
    return "postgresql"


def compter_lignes() -> int:
    """Fourni."""
    return _lire("SELECT count(*) AS n FROM analytique.ventes")[0]["n"]


def indicateurs() -> dict:
    """Mission 9.1 — FOURNI : le modèle des fonctions suivantes."""
    ligne = _lire("""
        SELECT count(*)                                          AS nb_lignes,
               count(DISTINCT order_id)                          AS nb_commandes,
               round(sum(montant), 2)                            AS ca_total,
               round(sum(montant) / count(DISTINCT order_id), 2) AS panier_moyen
        FROM analytique.ventes
    """)[0]
    return ligne


def ventes_mensuelles(debut: str | None = None, fin: str | None = None) -> list[dict]:
    """Mission 9.2 — même résultat que donnees_csv.ventes_mensuelles."""
    return _lire("""
        SELECT mois,
               round(sum(montant), 2)   AS ca,
               count(DISTINCT order_id) AS nb_commandes
        FROM analytique.ventes
        WHERE (%(debut)s::text IS NULL OR mois >= %(debut)s)
          AND (...)
        GROUP BY ...
        ORDER BY ...
    """, {"debut": debut, "fin": fin})


def top_categories(n: int = 10) -> list[dict]:
    """Mission 9.3 — même résultat que donnees_csv.top_categories."""
    return _lire("""
        SELECT categorie,
               round(sum(montant), 2) AS ca,
               round(100 * sum(montant) / (SELECT sum(montant) FROM analytique.ventes), 2) AS part_ca
        FROM analytique.ventes
        GROUP BY ...
        ORDER BY ...
        LIMIT ...
    """, {"n": n})


def etat(code: str) -> dict | None:
    """Mission 9.4 — même résultat que donnees_csv.etat."""
    ligne = _lire("""
        SELECT %(code)s::text            AS etat,
               round(sum(montant), 2)    AS ca,
               count(DISTINCT order_id)  AS nb_commandes,
               ...                       AS part_ca
        FROM analytique.ventes
        WHERE ...
    """, {"code": code})[0]
    # Sans aucune vente, la requête renvoie quand même UNE ligne, avec nb_commandes = 0
    if ligne["nb_commandes"] == 0:
        return ...
    return ligne
