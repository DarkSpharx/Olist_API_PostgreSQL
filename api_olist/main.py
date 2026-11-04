"""API des indicateurs de ventes Olist.

Lancement, depuis le dossier api_olist :
    Windows      : py -m uvicorn main:app --reload
    macOS/Linux  : python3 -m uvicorn main:app --reload
Puis ouvre http://127.0.0.1:8000/docs
"""
from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel

import donnees_csv as donnees   # J2, mission 10 : cette ligne sera remplacée

app = FastAPI(
    title="API des indicateurs de ventes Olist",
    description="Indicateurs en lecture seule, calculés sur les articles des commandes livrées (sept. 2016 – août 2018).",
    version="1.0.0",
)


# ---------- Modèles de réponse (ce que l'API promet de renvoyer) ----------
class Sante(BaseModel):
    statut: str
    source: str
    nb_lignes: int


class Indicateurs(BaseModel):
    nb_lignes: int
    nb_commandes: int
    ca_total: float
    panier_moyen: float


# ---------- Routes ----------
@app.get("/sante", response_model=Sante, tags=["Service"])
def sante():
    """Vérifie que l'API répond et indique la source utilisée."""
    return {"statut": "ok", "source": donnees.source(), "nb_lignes": donnees.compter_lignes()}


@app.get("/indicateurs", response_model=Indicateurs, tags=["Indicateurs"])
def indicateurs():
    """Chiffres clés de toute la période."""
    return donnees.indicateurs()


# =====================================================================
# MISSION 3 — Décommente ce bloc (sélectionne-le, puis Ctrl + /) et complète les « ... »
# =====================================================================
# class VenteMensuelle(BaseModel):
#     mois: str
#     ca: float
#     nb_commandes: int
#
#
# @app.get("/ventes/mensuelles", response_model=list[VenteMensuelle], tags=["Indicateurs"])
# def ventes_mensuelles(
#     debut: str | None = Query(None, pattern=r"^\d{4}-(0[1-9]|1[0-2])$",
#                               description="Premier mois inclus, format AAAA-MM", examples=["2017-01"]),
#     fin: str | None = Query(None, pattern=..., description=..., examples=["2017-12"]),
# ):
#     """Chiffre d'affaires et nombre de commandes, mois par mois."""
#     if debut is not None and fin is not None and debut > fin:
#         raise HTTPException(status_code=..., detail="« debut » doit être antérieur ou égal à « fin ».")
#     return donnees.ventes_mensuelles(debut, fin)


# =====================================================================
# MISSION 4 — Décommente ce bloc et complète les « ... »
# =====================================================================
# class Categorie(BaseModel):
#     categorie: str
#     ca: ...
#     part_ca: ...
#
#
# @app.get("/categories/top", response_model=list[Categorie], tags=["Indicateurs"])
# def top_categories(n: int = Query(10, ge=..., le=..., description="Nombre de catégories (1 à 50)")):
#     """Les n catégories au plus fort chiffre d'affaires."""
#     return donnees.top_categories(...)


# =====================================================================
# MISSION 5 — Écris toi-même le modèle Etat et la route /etats/{code_etat}
# en suivant les deux missions précédentes (méthode dans la consigne).
# =====================================================================
