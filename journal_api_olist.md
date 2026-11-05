# Journal de l'API Olist — FastAPI

**Nom :** Frédéric Arnould
**Dates :** J1 05/11/2026 · J2 06/11/2026
**Fichier rendu :** api_olist_Frederic_ARNOULD.zip

> Compétences : WCS C1.6 · C2.4 · C2.1 · C2.5 (niveau 2 · Adapter) — Simplon C6 · C7 (partiel)
> Remplis les parties **dans l'ordre**. Remplace chaque « … ». Une phrase suffit sauf mention contraire.

**Chiffres de référence (export de lundi)**
- Lignes : 110 197 · Commandes livrées : 96 478
- CA total : 15 424 463,65 R$ · Panier moyen : 159,88 R$
- Novembre 2017 : 1 154 559,53 R$ et 7 289 commandes
- SP : 5 771 713,93 R$, 40 501 commandes, 37,42 % du CA

---

# J1 — L'API sur le fichier CSV

<a id="j-m1"></a>
## M1 — Lancer l'API et la tester

- Version de Python : Python 3.14.7
- Commande de lancement que j'ai utilisée : py -m uvicorn main:app --reload
- Code et `nb_lignes` renvoyés par `/sante` : code 200, {"statut":"ok","source":"csv","nb_lignes":110197}
- Différence entre `/docs` et `/sante` ouverts dans le navigateur : /docs est une interface graphique (Swagger) générée automatiquement par FastAPI pour tester les routes. /sante est une route API qui renvoie un JSON confirmant que l'API tourne.
- Problème rencontré et solution (ou « aucun ») : comprendre les consignes et ou/quand répondre aux questions

<a id="j-m2"></a>
## M2 — Lire une route complète

### Le trajet d'une requête `GET /indicateurs`, en 4 étapes

1. Le navigateur envoie une requête `GET` à l'adresse http://127.0.0.1:8000/indicateurs
2. FastAPI exécute la fonction indicateurs() du fichier main.py, qui appelle  `indicateurs()` de `donnees_csv.py`
3. Cette fonction lit `data/ventes_olist.csv` et renvoie un dictionnaire `{"nb_lignes": len(v),"nb_commandes": nb_commandes,"ca_total": round(ca_total, 2),"panier_moyen": round(ca_total / nb_commandes, 2),}`
4. Le modèle `class Indicateurs(BaseModel)` vérifie les champs et leurs types puis FastAPI renvoie un `JSON` avec le code `200`

### L'expérience du contrat

- Quand j'ai mis `panier_moyen` en commentaire dans le modèle, la réponse ne contient plus le champ `panier_moyen`.
- Conclusion : le modèle décide de ce qui sort, même si la fonction de données renvoie plus.

### Pourquoi deux fichiers (`main.py` et `donnees_csv.py`) ?

- `donnees_csv.py` **calcule** et ne sait rien du web. `main.py` **expose** et ne sait rien du calcul. Demain, tu remplaceras `donnees_csv.py` par `donnees_pg.py`, et `main.py` ne changera presque pas. C'est ce qu'on appelle un code **organisé**

### Comparaison avec lundi

- `nb_commandes` : 96478 (lundi : 96 478)
- `ca_total` : 15424463.65 (lundi : 15 424 463,65)

<a id="j-m3"></a>
## M3 — Ventes mensuelles

### Tests

- Sans paramètre : `23` mois, du `2016-09` au `2018-08`
- `debut=2017-01` et `fin=2017-12` : 12 mois ; novembre 2017 = `1154559.53` R$ et `7289` commandes
- `debut=2018-02` et `fin=2017-01` : code `400` , message `{"detail":"« debut » doit être antérieur ou égal à « fin »."}`
- `debut=2017-13` : code `422`

### Questions

1. Différence entre un paramètre de chemin et un paramètre de requête, avec un exemple de cette API : **Un paramètre de chemin fait partie de l’URL, par exemple `SP` dans `/etats/SP`. Un paramètre de requête suit le `?` et précise la demande, par exemple `debut=2017-01` dans `/ventes/mensuelles?debut=2017-01`.**
2. Qui renvoie le code 400 (toi ou FastAPI) ? Et le code 422 ? Pourquoi cette différence ? **Le code 400 est renvoyé par notre code quand la période est incohérente, par exemple si `debut` est après `fin`. Le code 422 est renvoyé automatiquement par FastAPI si un paramètre ne respecte pas le format déclaré, comme `debut=2017-13`.**

<a id="j-m4"></a>
## M4 — Top catégories

### Tests

- Sans paramètre : `10` catégories ; la première est `health_beauty` avec `9.16 %`
- Somme des 10 parts : `62.32 %`
- `n=3` : `25.3 %`
- `n=0` : code `422` · `n=51` : code `422`

### Question

- Que reçoit Rafael s'il n'envoie pas `n` ? Où est-ce décidé dans le code ? S'il n'envoie pas de valeur pour `n`, il reçoit les 10 catégories au plus fort chiffre d'affaires. La valeur par défaut `10` est définie dans `main.py`, dans le paramètre `Query(10, ...)` de la route `/categories/top`.

```python
def top_categories(n: int = Query(10, ge=1, le=50, description="Nombre de catégories (1 à 50)")):
    """Les n catégories au plus fort chiffre d'affaires."""
    return donnees.top_categories(n)`
```
<a id="j-m5"></a>
## M5 — Chiffres d'un État

### Mon modèle `Etat` (copie le code)

- Dans `main.py`
```python
class Etat(BaseModel):
    etat: str
    ca: float
    nb_commandes: int
    part_ca: float

@app.get("/etats/{code_etat}", response_model=Etat, tags=["Indicateurs"])
def etat(code_etat: str = Path(pattern=r"^[A-Za-z]{2}$", description="Code de l'État sur 2 lettres, ex. SP")):
    """Chiffres d'un État brésilien."""
    code = code_etat.upper()          # « sp » et « SP » donnent le même résultat
    resultat = donnees.etat(code)
    if resultat is None:
        raise HTTPException(status_code=404, detail=f"Aucune vente pour l'État « {code} ».")
    return resultat
```
- Dans `donnees_csv.py`
```python
def etat(code: str) -> dict | None:
    """Mission 5 — chiffres d'un État brésilien (ex. « SP ») ; None s'il n'a aucune vente."""
    v = charger()

    # 1. Garder les lignes de l'État demandé
    e = v[v["customer_state"] == code]

    # 2. Aucune ligne → renvoyer None (main.py transformera ce None en erreur 404)
    if e.empty:
        return None

    # 3. Calculer et renvoyer les 4 champs
    ca = float(e["montant"].sum())
    part_ca = ca / float(v["montant"].sum()) * 100  # part du CA total, en %, arrondie à 2 décimales
    return {
        "etat": code,
        "ca": round(ca, 2),
        "nb_commandes": e["order_id"].nunique(),
        "part_ca": round(part_ca, 2),  # part du CA total, en %, arrondie à 2 décimales
    }
```

### Tests

- `/etats/SP` : CA `5771713.93` , commandes `40501` , part `37.42` %
- `/etats/sp` : identique (oui / non) : oui
- `/etats/XX` : code `404` , message `"Aucune vente pour l'État « XX »."`
- `/etats/SPX` : code `422`

### Question

- Pourquoi un État sans vente renvoie 404 et pas une réponse vide avec le code 200 ? **Parce qu’un État sans vente est considéré comme une ressource inexistante. Le code 404 l’indique clairement, alors qu’un 200 avec une réponse vide signifierait que la requête a réussi.**

<a id="j-m6"></a>
## M6 — Recette complète dans /docs

Pour chaque test : le code obtenu, puis une valeur lue dans la réponse.

1. `GET /sante` (attendu 200) : …
2. `GET /indicateurs` (attendu 200) : …
3. `GET /ventes/mensuelles` sans paramètre (attendu 200, 23 mois) : …
4. `GET /ventes/mensuelles?debut=2018-01` (attendu 200) : nombre de mois …
5. `GET /ventes/mensuelles?debut=2018-02&fin=2017-01` (attendu 400) : …
6. `GET /ventes/mensuelles?fin=nov` (attendu 422) : …
7. `GET /categories/top` (attendu 200, 10 catégories) : …
8. `GET /categories/top?n=50` (attendu 200) : dernière catégorie de la liste …
9. `GET /categories/top?n=0` (attendu 422) : …
10. `GET /etats/RJ` (attendu 200) : part du CA …
11. `GET /etats/XX` (attendu 404) : …
12. `GET /etats/SPX` (attendu 422) : …

### Bilan du J1

1. Ce qui fonctionne : …
2. Ce qui me reste à comprendre ou à terminer : …

---

# J2 — L'API sur PostgreSQL

<a id="j-m7"></a>
## M7 — Charger les ventes dans PostgreSQL

- Base utilisée : …
- Résultat du contrôle final du script : … lignes, … commandes, … de CA
- Droit donné à `lecteur_olist` sur la table, et pourquoi seulement celui-là : …

<a id="j-m8"></a>
## M8 — Mettre les secrets dans `.env`

- Résultat de la commande de test : …
- Rôle de `.env` : …
- Rôle de `.env.exemple` : …
- Rôle de la ligne `.env` dans `.gitignore` : …
- J'ai vérifié qu'aucun `.py` ne contient le mot de passe (oui / non) : …

<a id="j-m9"></a>
## M9 — Réécrire les fonctions en SQL

### Résultat de `verifier_sources.py`

- Bilan affiché : … / 8
- Fonction qui m'a demandé le plus de corrections, et pourquoi : …

### Ma requête de `top_categories()` (copie-la)

```sql
…
```

### Sécurité

- Pourquoi `%(code)s` plutôt qu'une f-string ? Donne l'exemple d'une valeur dangereuse. …
- Pourquoi faire calculer PostgreSQL plutôt que Python ? …

<a id="j-m10"></a>
## M10 — Basculer l'API sur PostgreSQL

- `/sante` après la bascule : source … , lignes …
- Pourquoi il faut relancer l'API après avoir modifié `.env` : …
- Test de panne (`PGPORT=5999`) : code … , message …
- Ce qu'aurait vu Rafael sans le gestionnaire d'erreur `SourceIndisponible` : …
- Ce que Rafael a dû changer dans son code pour la bascule : …

<a id="j-m11"></a>
## M11 — Écrire le client de Rafael

- Bilan affiché par `client.py` : … / 10
- Nombre de lignes de `ca_mensuel_2017.csv`, en-tête compris : …
- Différence entre `.status_code` et `.json()` : …
- Utilité du paramètre `timeout` : …

<a id="j-m12"></a>
## M12 — README et rendu

- Le test de remise à zéro a fonctionné en suivant seulement le README (oui / non) : …
- Ce que j'ai dû corriger dans le README après ce test : …
- Contenu de mon zip, fichier par fichier : …

### Mes choix techniques (3 à 5 lignes)

- Source de données retenue et pourquoi : …
- Compte de connexion et pourquoi : …
- Gestion des erreurs : …
- Ce que j'ajouterais pour mettre l'API en production : …

### Message à Mariana (3 lignes, sans jargon)

- Ce que Rafael peut faire maintenant : …
- D'où viennent les chiffres : …
- Le chiffre qui prouve que c'est juste : …
