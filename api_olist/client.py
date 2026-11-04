"""Client de l'API Olist : interroge chaque route et vérifie les réponses (J2, mission 11).

Lancement (l'API doit tourner dans un AUTRE terminal) :
    Windows      : py client.py
    macOS/Linux  : python3 client.py
Les zones « ... » sont à compléter.
"""
import csv

import requests

URL_API = "http://127.0.0.1:8000"
DELAI = 10  # secondes avant d'abandonner une requête


def appeler(route: str, parametres: dict | None = None) -> requests.Response:
    """Fourni — envoie une requête GET à l'API et renvoie la réponse complète."""
    return requests.get(f"{URL_API}{route}", params=parametres, timeout=DELAI)


def verifier(intitule: str, condition: bool) -> bool:
    """Fourni — affiche ✅ ou ❌ et renvoie le résultat du contrôle."""
    print(("✅ " if condition else "❌ ") + intitule)
    return condition


def main() -> None:
    try:
        reponse = appeler("/sante")
    except requests.ConnectionError:
        print("❌ L'API ne répond pas : lance-la d'abord avec  py -m uvicorn main:app --reload")
        return
    if reponse.status_code != 200:
        print(f"❌ L'API répond {reponse.status_code} : {reponse.json().get('detail')}")
        return

    resultats = []

    # 1. Santé — FOURNI
    sante = appeler("/sante").json()
    print(f"Source utilisée par l'API : {sante['source']}")
    resultats.append(verifier("/sante renvoie 110197 lignes", sante["nb_lignes"] == 110197))

    # 2. Indicateurs — FOURNI
    ind = appeler("/indicateurs").json()
    resultats.append(verifier("96478 commandes livrées", ind["nb_commandes"] == 96478))
    resultats.append(verifier("CA total = 15424463.65", abs(ind["ca_total"] - 15424463.65) < 0.01))

    # 3. Ventes mensuelles 2017 + sauvegarde CSV
    reponse = appeler("/ventes/mensuelles", {"debut": ..., "fin": ...})
    mois = reponse.json()
    resultats.append(verifier("12 mois en 2017", len(mois) == ...))
    record = max(mois, key=lambda m: m["ca"])
    resultats.append(verifier(f"Record 2017 en novembre ({record['mois']}, {record['ca']} R$)",
                              record["mois"] == ...))
    with open("ca_mensuel_2017.csv", "w", newline="", encoding="utf-8") as f:
        ecrivain = csv.DictWriter(f, fieldnames=["mois", "ca", "nb_commandes"])
        ecrivain.writeheader()
        ecrivain.writerows(...)
    print("   → ca_mensuel_2017.csv enregistré")

    # 4. Top catégories : demande 3 catégories, vérifie qu'il y en a 3 et que health_beauty est en tête
    top = ...
    resultats.append(verifier("3 catégories, health_beauty en tête", ...))

    # 5. État : SP pèse environ 37 % du CA
    sp = ...
    resultats.append(verifier("SP pèse environ 37 % du CA", ...))

    # 6. Les erreurs sont bien signalées (compare .status_code au code attendu)
    resultats.append(verifier("État inconnu → 404", appeler("/etats/XX").status_code == 404))
    resultats.append(verifier("n = 0 → 422", ...))
    resultats.append(verifier("debut après fin → 400", ...))

    print(f"\nBilan : {sum(resultats)}/{len(resultats)} contrôles réussis")


if __name__ == "__main__":
    main()
