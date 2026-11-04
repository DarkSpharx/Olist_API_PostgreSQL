# 🚀 FastAPI — Mettre à disposition les indicateurs Olist par une API

**Formation Data Analyst 2026-2027 · Fil Olist · 2 jours · Niveau 2 · Adapter**
Suite des briefs pandas (lundi) et Power Query (Olist).

> **Compétences visées**
> - **Référentiel WCS** (niveau dominant **2 · Adapter**)
>   - **C1.6** Interface standard de partage automatique (API REST) — niveau 2
>   - **C2.4** Bonnes pratiques de programmation : code organisé et réutilisable — niveau 2
>   - **C2.1** Effectuer et documenter des choix méthodologiques d'automatisation — niveau 2
>   - **C2.5** Tableaux de données : DataFrames avec Python et pandas — niveau 2 *(J1)*
> - **Référentiel Simplon** (niveau 6)
>   - **C6** Extraire des données depuis une source structurée de manière sécurisée — *travaillée partiellement* : connexion programmatique à PostgreSQL avec un compte en lecture seule, secrets hors du code, initialisation des connexions, gestion des erreurs et des exceptions.
>   - **C7** Extraire des données… en construisant des requêtes HTTP vers un service web REST — *travaillée partiellement* : côté client uniquement (script `client.py`).
>
> **Niveau 2 · Adapter** : tu appliques des méthodes **fournies** à un nouveau contexte. Chaque mission te donne la méthode, un modèle à suivre et du code à trous.

---

<a id="sommaire"></a>
## 📑 Sommaire

1. [Page 1 — Contexte et objectifs](#page-1)
2. [Page 2 — Comprendre une API (15 min)](#page-2)
3. [Page 3 — Préparer ton poste (J1, 20 min)](#page-3)
4. [Page 4 — Plan d'action des 2 jours](#page-4)
5. [Page 5 — J1 · Missions 1 à 6 : l'API sur le fichier CSV](#page-5)
6. [Page 6 — J2 · Missions 7 et 8 : la base et les secrets](#page-6)
7. [Page 7 — J2 · Missions 9 à 12 : PostgreSQL, bascule, client, README](#page-7)
8. [Page 8 — Auto-évaluation, rendu et ressources](#page-8)

---

<a id="page-1"></a>
## Page 1 — Contexte et objectifs

### 📨 Le message de Mariana

> « Bonjour,
> Les chiffres sont enfin justes dans Power BI, merci.
> Nouvelle demande : Rafael, le développeur du **portail vendeurs**, veut afficher nos indicateurs (chiffre d'affaires mensuel, meilleures catégories, chiffres par État) directement dans le portail. Il ne veut pas de fichier Excel envoyé chaque mois : il veut **interroger nos chiffres automatiquement**, quand il en a besoin.
> Peux-tu lui préparer une **API en lecture seule** ? Demain, elle devra lire la base PostgreSQL, pas un fichier.
> Mariana »

### 🎯 À la fin des 2 jours, tu sais…

1. Expliquer ce qu'est une API REST : route, paramètre, réponse JSON, code de statut.
2. Exposer des indicateurs calculés en pandas, puis en SQL, avec **FastAPI**.
3. Valider les paramètres reçus et renvoyer des erreurs claires (400, 404, 422, 503).
4. Te connecter à PostgreSQL de façon sécurisée : compte en lecture seule, mot de passe hors du code, requêtes paramétrées.
5. Interroger une API depuis un script Python et vérifier ses réponses.

### 🤔 Pourquoi construire une API quand on est data analyst ?

En certification, tu **interrogeras** des API (C7). Construire la tienne te montre l'autre côté : ce qu'est une route, pourquoi une API renvoie 404 ou 422, à quoi sert sa documentation. Tu sauras ensuite lire n'importe quelle documentation d'API.

### 📦 Ce que tu rends à la fin du J2

1. `api_olist_NOM.zip` : ton dossier `api_olist`, **sans** le sous-dossier `data/` et **sans** le fichier `.env`.
2. `journal_api_olist.md` : ton journal complété.

[↑ Sommaire](#sommaire)

---

<a id="page-2"></a>
## Page 2 — Comprendre une API *(15 min)*

### L'image du restaurant

- Le **client** (le portail de Rafael, ton navigateur, un script) passe une **commande** : c'est la **requête**.
- La **cuisine** (ton API) prépare le plat à partir des ingrédients (les données).
- Le **plat** revient au client : c'est la **réponse**, au format **JSON**.
- La **carte** dit ce qu'on peut commander et comment : c'est la **documentation**. FastAPI la génère toute seule, à l'adresse `/docs`.

Le client ne voit jamais la cuisine. Il ne sait pas si les chiffres viennent d'un CSV ou de PostgreSQL. C'est ce qui te permettra de changer de source au J2 **sans que Rafael change une ligne de son code**.

### Le vocabulaire

- **Route** (ou *endpoint*) : une adresse de l'API, par exemple `/indicateurs`.
- **Méthode GET** : « donne-moi ». Toute ton API est en GET, car elle est en lecture seule.
- **Paramètre de chemin** : une valeur **dans** l'adresse. `/etats/SP` → `code_etat = "SP"`.
- **Paramètre de requête** : une option **après le `?`**. `/categories/top?n=5` → `n = 5`. Plusieurs options sont séparées par `&`.
- **JSON** : du texte qui ressemble aux dictionnaires et listes Python : `{"mois": "2017-11", "ca": 1154559.53}`.
- **Modèle de réponse** : une classe Python (Pydantic) qui décrit exactement les champs renvoyés. C'est le **contrat** passé avec Rafael.

### Les codes de statut à connaître

- **200** : tout va bien.
- **400** : la demande est mal formulée (ex. date de début après la date de fin). C'est **toi** qui décides de l'envoyer.
- **404** : la ressource demandée n'existe pas (ex. un État sans vente).
- **422** : un paramètre ne respecte pas les règles déclarées (ex. `n=0` alors que le minimum est 1). **FastAPI** l'envoie tout seul.
- **500** : l'API a planté. Une API bien faite n'en renvoie jamais volontairement.
- **503** : la source de données ne répond pas (ex. PostgreSQL arrêté).

### Les 5 routes que tu vas construire

1. `GET /sante` : l'API répond-elle ? Quelle source utilise-t-elle ? *(fournie)*
2. `GET /indicateurs` : chiffres clés de toute la période. *(fournie)*
3. `GET /ventes/mensuelles?debut=2017-01&fin=2017-12` : CA et commandes par mois.
4. `GET /categories/top?n=10` : les meilleures catégories.
5. `GET /etats/SP` : les chiffres d'un État.

[↑ Sommaire](#sommaire)

---

<a id="page-3"></a>
## Page 3 — Préparer ton poste *(J1, 20 min)*

Fais les étapes **dans l'ordre**. Coche chaque case.

### Étape 3.1 — Vérifier Python *(2 min)*

Dans un terminal :
```
Windows      : py --version
macOS/Linux  : python3 --version
```
- [ ] La version est **3.10 ou plus récente**. Sinon, appelle le formateur avant d'aller plus loin.

### Étape 3.2 — Récupérer le projet *(3 min)*

1. Télécharge `api_olist_depart.zip` (ressources du brief) et décompresse-le, par exemple dans `C:\formation\`.
2. Tu obtiens un dossier `api_olist` et un fichier `olist_ventes.sql` (pour le J2).
3. Ouvre le **dossier** `api_olist` dans VS Code : **Fichier › Ouvrir le dossier**.

- [ ] Je vois dans VS Code : `main.py`, `donnees_csv.py`, `donnees_pg.py`, `erreurs.py`, `client.py`, `verifier_sources.py`, `requirements.txt`, `.env.exemple`, `.gitignore`, `README.md` et le dossier `data/`.

💡 Le fichier `data/ventes_olist.csv` est l'export de lundi (mission 6), identique pour tout le groupe. Tous les chiffres de référence de ce brief viennent de lui.

### Étape 3.3 — Installer les bibliothèques *(10 min)*

1. Dans VS Code : **Terminal › Nouveau terminal**. Le terminal s'ouvre **dans le dossier** `api_olist`.
2. Tape :
```
Windows      : py -m pip install -r requirements.txt
macOS/Linux  : python3 -m pip install -r requirements.txt
```
- [ ] La dernière ligne commence par `Successfully installed` ou indique `Requirement already satisfied`.

📘 `requirements.txt` liste les bibliothèques du projet. Toute personne qui récupère ton projet les installe avec cette **seule** commande.

[↑ Sommaire](#sommaire)

---

<a id="page-4"></a>
## Page 4 — Plan d'action des 2 jours

### J1 — L'API sur le fichier CSV

| Horaire | Mission | Fichier à ouvrir | Ce que tu remplis |
|---|---|---|---|
| 9 h 00 | Pages 1 à 3 | — | — |
| 9 h 45 | [M1 — Lancer l'API et la tester](#m1) | terminal, navigateur | [Journal › M1](journal_api_olist.md#j-m1) |
| 10 h 30 | [M2 — Lire une route complète](#m2) | `main.py`, `donnees_csv.py` | [Journal › M2](journal_api_olist.md#j-m2) |
| 11 h 15 | [M3 — Ventes mensuelles](#m3) | `main.py`, `donnees_csv.py` | [Journal › M3](journal_api_olist.md#j-m3) |
| 13 h 30 | [M4 — Top catégories](#m4) | `main.py`, `donnees_csv.py` | [Journal › M4](journal_api_olist.md#j-m4) |
| 14 h 30 | [M5 — Chiffres d'un État](#m5) | `main.py`, `donnees_csv.py` | [Journal › M5](journal_api_olist.md#j-m5) |
| 15 h 45 | [M6 — Recette complète dans /docs](#m6) | navigateur | [Journal › M6](journal_api_olist.md#j-m6) |

### J2 — L'API sur PostgreSQL

| Horaire | Mission | Fichier à ouvrir | Ce que tu remplis |
|---|---|---|---|
| 9 h 00 | [M7 — Charger les ventes dans PostgreSQL](#m7) | DBeaver, `olist_ventes.sql` | [Journal › M7](journal_api_olist.md#j-m7) |
| 9 h 30 | [M8 — Mettre les secrets dans `.env`](#m8) | `.env` | [Journal › M8](journal_api_olist.md#j-m8) |
| 10 h 00 | [M9 — Réécrire les fonctions en SQL](#m9) | `donnees_pg.py` | [Journal › M9](journal_api_olist.md#j-m9) |
| 13 h 30 | [M10 — Basculer l'API sur PostgreSQL](#m10) | `main.py`, `.env` | [Journal › M10](journal_api_olist.md#j-m10) |
| 14 h 15 | [M11 — Écrire le client de Rafael](#m11) | `client.py` | [Journal › M11](journal_api_olist.md#j-m11) |
| 15 h 15 | [M12 — README et rendu](#m12) | `README.md` | [Journal › M12](journal_api_olist.md#j-m12) |
| 16 h 15 | [Auto-évaluation et dépôt](#page-8) | Simplonline | — |

**Règle des 2 jours** : chaque mission utilise la précédente. En retard le J1 ? Termine **M1 à M3** : M4 et M5 suivent le même modèle. En retard le J2 ? Termine **M7 à M10** : ce sont elles qui branchent PostgreSQL.

**Règle du terminal** : l'API tourne dans **un** terminal (laisse-le ouvert). Pour lancer d'autres commandes, ouvre un **deuxième** terminal (bouton **+** du panneau Terminal).

**Règle macOS/Linux** : dans toutes les commandes de ce brief, remplace `py` par `python3`.

[↑ Sommaire](#sommaire)

---

<a id="page-5"></a>
## Page 5 — J1 · Missions 1 à 6

<a id="m1"></a>
### Mission 1 — Lancer l'API et la tester *(45 min)*

**Méthode**
1. Dans le terminal (dossier `api_olist`) :
   ```
   Windows      : py -m uvicorn main:app --reload
   macOS/Linux  : python3 -m uvicorn main:app --reload
   ```
   Attends la ligne `Application startup complete`.
2. Ouvre ton navigateur à l'adresse **http://127.0.0.1:8000/docs**.
3. Clique sur **GET /sante** › **Try it out** › **Execute**.
4. Lis la zone *Responses* : le **Request URL**, le **Code** et le **Response body**.
5. Ouvre maintenant **http://127.0.0.1:8000/sante** directement dans un nouvel onglet. Tu vois la même réponse, sans la page de documentation.

📘 `main:app` veut dire « dans le fichier `main.py`, l'objet nommé `app` ». `--reload` relance l'API à chaque fois que tu enregistres un fichier `.py`.

✅ **Je vérifie**
- [ ] `/sante` renvoie le code **200** et `"nb_lignes": 110197`.
- [ ] `/docs` affiche 2 routes : `/sante` et `/indicateurs`.

**Ça bloque ?**
- *`No module named uvicorn`* : l'étape 3.3 n'a pas été faite, ou a été faite avec une autre commande Python.
- *`Error loading ASGI app. Could not import module "main"`* : le terminal n'est pas dans le dossier `api_olist`. Tape `cd` suivi du chemin du dossier.
- *`address already in use`* : une autre API tourne déjà. Ferme l'autre terminal, ou arrête-la avec **Ctrl + C**.

➡️ [Journal › M1](journal_api_olist.md#j-m1)

---

<a id="m2"></a>
### Mission 2 — Lire une route complète *(45 min)*

**Objectif** : comprendre le trajet d'une requête, du navigateur jusqu'aux données, et retour. Ce trajet est le **modèle** de toutes les missions suivantes.

**Méthode**
1. Dans `main.py`, lis la route `/indicateurs` (la fonction sous `@app.get("/indicateurs", ...)`).
2. Dans `donnees_csv.py`, lis la fonction `indicateurs()`.
3. Lis le schéma ci-dessous et vérifie chaque flèche dans le code.
4. Fais l'expérience du contrat (ci-dessous).
5. Compare les chiffres de `/indicateurs` à ceux de lundi.

📘 **Le trajet d'une requête**
```
Navigateur ──GET /indicateurs──▶ main.py : indicateurs()
                                      │ appelle
                                      ▼
                              donnees_csv.py : indicateurs()  ── lit ──▶ data/ventes_olist.csv
                                      │ renvoie un dictionnaire Python
                                      ▼
                              main.py : modèle Indicateurs  (vérifie les champs et leurs types)
                                      │
Navigateur ◀──JSON + code 200─────────┘
```

📘 **Pourquoi deux fichiers ?** `donnees_csv.py` **calcule** et ne sait rien du web. `main.py` **expose** et ne sait rien du calcul. Demain, tu remplaceras `donnees_csv.py` par `donnees_pg.py`, et `main.py` ne changera presque pas. C'est ce qu'on appelle un code **organisé** (C2.4).

🧪 **L'expérience du contrat** *(10 min)*
1. Dans `main.py`, classe `Indicateurs` : ajoute `# ` au début de la ligne `panier_moyen: float`. Enregistre (**Ctrl + S**).
2. Relance **Execute** sur `/indicateurs` dans `/docs`. Que devient `panier_moyen` ?
3. Retire le `# `, enregistre. `panier_moyen` revient.

Conclusion à écrire dans le journal : **le modèle décide de ce qui sort**, même si la fonction de données renvoie plus.

✅ **Je vérifie**
- [ ] `/indicateurs` renvoie **96478** commandes et un `ca_total` de **15424463.65**.
- [ ] J'ai rempli le trajet de la requête dans le journal.

➡️ [Journal › M2](journal_api_olist.md#j-m2)

---

<a id="m3"></a>
### Mission 3 — Ventes mensuelles *(75 min)*

**Objectif** : `GET /ventes/mensuelles?debut=2017-01&fin=2017-12` renvoie une ligne par mois avec le CA et le nombre de commandes.

**Méthode** (l'ordre est imposé)
1. **Les données d'abord.** Dans `donnees_csv.py`, complète `ventes_mensuelles()` (3 zones `...`).
   - Le filtre `fin` est le symétrique du filtre `debut`.
   - Le CA est une **somme** (`"sum"`), les commandes sont des `order_id` **distincts** (`"nunique"`).
2. **Teste la fonction seule**, sans l'API, dans un **deuxième** terminal :
   ```
   py -c "import donnees_csv as d; print(d.ventes_mensuelles('2017-11', '2017-11'))"
   ```
   Attendu : `[{'mois': '2017-11', 'ca': 1154559.53, 'nb_commandes': 7289}]`
3. **La route ensuite.** Dans `main.py`, sélectionne tout le bloc **MISSION 3** (de `# class VenteMensuelle` à `# return donnees...`) et décommente-le : **Ctrl + /** (macOS : **Cmd + /**).
4. Complète les `...` du paramètre `fin` en copiant ceux de `debut` (même `pattern`, description adaptée).
5. Complète le code d'erreur quand `debut` est après `fin` : c'est une demande mal formulée (voir [page 2](#page-2)).
6. Enregistre. Dans `/docs`, recharge la page (**F5**) : la route apparaît.

📘 **Le `pattern`, une règle d'écriture.** `^\d{4}-(0[1-9]|1[0-2])$` signifie « 4 chiffres, un tiret, puis un mois de 01 à 12 ». Si Rafael envoie `2017-13` ou `nov 2017`, FastAPI refuse **avant même** d'appeler ta fonction, avec un code 422. Tu as déjà vu les expressions régulières en Python.

📘 **Pourquoi comparer des textes marche ici.** Le format `AAAA-MM` se trie comme une date : `"2017-02" < "2017-11"` est vrai. Ce ne serait pas le cas avec `MM-AAAA`.

✅ **Je vérifie** (dans `/docs`, *Try it out*)
- [ ] Sans paramètre : **23** mois, de `2016-09` à `2018-08`.
- [ ] `debut=2017-01`, `fin=2017-12` : **12** mois ; novembre 2017 = **1154559.53** et **7289** commandes.
- [ ] `debut=2018-02`, `fin=2017-01` : code **400**.
- [ ] `debut=2017-13` : code **422**.

➡️ [Journal › M3](journal_api_olist.md#j-m3)

---

<a id="m4"></a>
### Mission 4 — Top catégories *(60 min)*

**Objectif** : `GET /categories/top?n=10` renvoie les `n` catégories au plus fort CA, avec leur part du CA total en %.

**Méthode** (même ordre qu'en mission 3)
1. Dans `donnees_csv.py`, complète `top_categories()`.
   - `total` : la somme de toute la colonne `montant`.
   - Tri **décroissant** (`ascending=False`), puis les `n` premiers.
   - `ca` arrondi à 2 décimales ; `part_ca` = `ca / total * 100`, arrondi à 2. Pense à `round(float(...), 2)`, comme dans `indicateurs()`.
2. Teste la fonction seule :
   ```
   py -c "import donnees_csv as d; print(d.top_categories(2))"
   ```
3. Dans `main.py`, décommente le bloc **MISSION 4** et complète :
   - les types des champs `ca` et `part_ca` dans le modèle `Categorie` ;
   - les bornes de `n` : **1** au minimum, **50** au maximum ;
   - l'appel à la fonction de données.

📘 **`ge` et `le`**, c'est-à-dire *greater or equal* (≥) et *less or equal* (≤). Le `10` en premier argument de `Query` est la **valeur par défaut** : si Rafael n'envoie pas `n`, il reçoit 10 catégories.

✅ **Je vérifie**
- [ ] Sans paramètre : **10** catégories, `health_beauty` en tête (**9.16** %).
- [ ] Les 10 parts additionnées font environ **62,4** % (lundi : les 10 premières font 62 % du CA).
- [ ] `n=0` et `n=51` : code **422**.

➡️ [Journal › M4](journal_api_olist.md#j-m4)

---

<a id="m5"></a>
### Mission 5 — Chiffres d'un État *(75 min, pause comprise)*

**Objectif** : `GET /etats/SP` renvoie le CA, le nombre de commandes et la part du CA de l'État. Un État sans vente renvoie **404**.

Cette fois, **tu écris toi-même** le modèle et la route, en suivant les missions 3 et 4.

**Méthode**
1. Dans `donnees_csv.py`, complète `etat()`. Si l'État n'a aucune ligne, la fonction renvoie `None`.
2. Teste-la : `py -c "import donnees_csv as d; print(d.etat('SP')); print(d.etat('XX'))"`
3. Dans `main.py`, sous le commentaire **MISSION 5**, écris le modèle `Etat` avec 4 champs : `etat` (texte), `ca` (décimal), `nb_commandes` (entier), `part_ca` (décimal).
4. Écris la route en t'appuyant sur ce squelette :
   ```python
   @app.get("/etats/{code_etat}", response_model=..., tags=["Indicateurs"])
   def etat(code_etat: str = Path(pattern=r"^[A-Za-z]{2}$", description="Code de l'État sur 2 lettres, ex. SP")):
       """Chiffres d'un État brésilien."""
       code = code_etat.upper()          # « sp » et « SP » donnent le même résultat
       resultat = donnees.etat(...)
       if resultat is None:
           raise HTTPException(status_code=..., detail=f"Aucune vente pour l'État « {code} ».")
       return resultat
   ```

📘 **Pourquoi `{code_etat}` entre accolades ?** C'est un **paramètre de chemin** : FastAPI prend ce qui est écrit à cet endroit de l'adresse et le passe à la fonction sous le nom `code_etat`.

📘 **Pourquoi `.upper()` ?** Dans les données, les États sont en majuscules. Rafael ne doit pas avoir à le savoir.

✅ **Je vérifie**
- [ ] `/etats/SP` : CA **5771713.93**, **40501** commandes, **37.42** %.
- [ ] `/etats/sp` donne exactement la même réponse.
- [ ] `/etats/XX` : code **404** avec un message lisible.
- [ ] `/etats/SPX` : code **422**.

➡️ [Journal › M5](journal_api_olist.md#j-m5)

---

<a id="m6"></a>
### Mission 6 — Recette complète dans /docs *(45 min)*

**Objectif** : vérifier toute l'API comme le ferait Rafael, et garder la preuve.

**Méthode**
1. Arrête l'API (**Ctrl + C**), relance-la, recharge `/docs`.
2. Déroule les **12 tests** de la Partie M6 du journal, dans l'ordre. Pour chacun, note le code obtenu et une valeur lue dans la réponse.
3. En bas de `/docs`, ouvre la section **Schemas**. Retrouve tes 5 modèles.
4. Ouvre **http://127.0.0.1:8000/openapi.json**. C'est la même documentation, en JSON, lisible par une machine. Rafael peut s'en servir pour générer son code.

✅ **Je vérifie**
- [ ] Les 12 tests donnent le code attendu.
- [ ] J'ai répondu aux 2 questions de bilan du J1.
- [ ] **Ctrl + S** sur tous les fichiers.

🚀 **Pour aller plus loin** : ajoute une route `GET /categories/{categorie}/mensuel` qui renvoie le CA mensuel d'une seule catégorie (404 si elle n'existe pas). Ajoute la fonction correspondante dans `donnees_csv.py`.

➡️ [Journal › M6](journal_api_olist.md#j-m6)

[↑ Sommaire](#sommaire)

---

<a id="page-6"></a>
## Page 6 — J2 · Missions 7 et 8

<a id="m7"></a>
### Mission 7 — Charger les ventes dans PostgreSQL *(30 min)*

**Objectif** : la table des ventes existe dans la base `olist`, et le compte `lecteur_olist` peut la lire.

**Méthode**
1. Ouvre **DBeaver** et connecte-toi avec le compte `postgres`.
2. Vérifie que la base **`olist`** existe (tu l'as créée pour le brief Power Query). Sinon : clic droit sur **Bases de données** › **Créer une nouvelle base de données** › nom `olist`.
3. Sélectionne la base `olist`, puis **Fichier › Ouvrir un fichier** › `olist_ventes.sql`.
4. Vérifie en haut de l'éditeur que la base active est `olist`.
5. Exécute **tout le script** : **Alt + X**. Compte 30 secondes à 2 minutes.
6. Le dernier résultat doit afficher **110197**, **96478** et **15424463.65**.

📘 Le script crée le schéma `analytique` et sa table `ventes` : les mêmes 110 197 lignes que `ventes_olist.csv`. Il donne au compte `lecteur_olist` le droit de **lire** (`SELECT`), rien d'autre. Si le compte n'existe pas encore, le script le crée, avec le mot de passe `olist2026`.

✅ **Je vérifie**
- [ ] J'ai lu 110197, 96478 et 15424463.65.

➡️ [Journal › M7](journal_api_olist.md#j-m7)

---

<a id="m8"></a>
### Mission 8 — Mettre les secrets dans `.env` *(30 min)*

**Objectif** : l'API connaît le mot de passe de la base, sans qu'il apparaisse jamais dans le code.

**Méthode**
1. Dans VS Code, clic droit sur `.env.exemple` › **Copier**, puis clic droit dans le dossier › **Coller**. Renomme la copie en **`.env`** (exactement, avec le point au début, sans extension).
2. Dans `.env`, remplace `a_remplacer` par le mot de passe de `lecteur_olist`. Laisse `SOURCE_DONNEES=csv` pour l'instant.
3. Ouvre `.gitignore` et repère la ligne `.env`.
4. Teste la lecture du fichier, dans le deuxième terminal :
   ```
   py -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('PGUSER'))"
   ```
   Attendu : `lecteur_olist`.

📘 **Trois règles pour les secrets** (comme en S42 avec `lecteur_data`)
1. Un mot de passe n'est **jamais** écrit dans un fichier `.py`. Le code se partage ; le secret, non.
2. `.env` reste **sur ton poste**. `.gitignore` empêche Git de l'envoyer sur un dépôt. Tu ne le déposes pas non plus sur Simplonline.
3. `.env.exemple` est partagé : il montre **quelles** variables remplir, avec de fausses valeurs.

✅ **Je vérifie**
- [ ] La commande de test affiche `lecteur_olist`.
- [ ] Aucun fichier `.py` ne contient `olist2026`. Pour le vérifier : **Ctrl + Maj + F** dans VS Code, puis cherche `olist2026`.

➡️ [Journal › M8](journal_api_olist.md#j-m8)

[↑ Sommaire](#sommaire)

---

<a id="page-7"></a>
## Page 7 — J2 · Missions 9 à 12

<a id="m9"></a>
### Mission 9 — Réécrire les fonctions en SQL *(2 h 30, pause comprise)*

**Objectif** : `donnees_pg.py` a les **mêmes fonctions** que `donnees_csv.py` et donne **exactement les mêmes chiffres**, mais en interrogeant PostgreSQL.

**Méthode**
1. **9.1 — Lire le modèle** *(20 min)*. Dans `donnees_pg.py`, lis `_lire()` puis `indicateurs()`.
   - `_lire()` ouvre une connexion avec les valeurs de `.env`, exécute **une** requête et renvoie une liste de dictionnaires.
   - Si PostgreSQL ne répond pas, `_lire()` lève `SourceIndisponible` : tu t'en serviras en mission 10.
2. **9.2 — `ventes_mensuelles()`** *(40 min)*. Complète le `WHERE`, le `GROUP BY` et le `ORDER BY`. La condition sur `fin` est le symétrique de celle sur `debut`.
3. **9.3 — `top_categories()`** *(30 min)*. Complète `GROUP BY`, `ORDER BY` (décroissant) et `LIMIT` avec le paramètre `%(n)s`.
4. **9.4 — `etat()`** *(30 min)*. Complète `part_ca` (même formule qu'en 9.3) et le `WHERE` avec le paramètre `%(code)s`, puis le `return` quand il n'y a aucune commande.
5. **Après chaque fonction**, lance dans le deuxième terminal :
   ```
   py verifier_sources.py
   ```
   Le script appelle chaque fonction **dans les deux fichiers** et compare les résultats.

📘 **Les paramètres `%(nom)s` : la règle de sécurité n° 1.**
Ne construis **jamais** une requête en collant une valeur reçue dans le texte SQL :
```python
# ❌ INTERDIT : si code vaut  SP' OR '1'='1 , la requête renvoie tout (injection SQL)
_lire(f"SELECT ... WHERE customer_state = '{code}'")

# ✅ OBLIGATOIRE : psycopg envoie la valeur séparément, elle ne peut pas modifier la requête
_lire("SELECT ... WHERE customer_state = %(code)s", {"code": code})
```

📘 **Pourquoi `%(debut)s::text IS NULL OR ...` ?** Quand Rafael n'envoie pas `debut`, la valeur vaut `None`, transmise à PostgreSQL comme `NULL`. La condition devient alors vraie pour toutes les lignes, et **le filtre est ignoré**. `::text` indique à PostgreSQL le type de cette valeur vide.

📘 **Laisse la base calculer.** On ne rapatrie pas 110 197 lignes dans Python pour les additionner : PostgreSQL renvoie directement 12 lignes ou 1 ligne. C'est le principe vu en S42.

✅ **Je vérifie**
- [ ] `py verifier_sources.py` affiche **8/8 fonctions identiques**.
- [ ] Aucune requête de `donnees_pg.py` ne contient de `f"` ni de `+` pour insérer une valeur.

**Ça bloque ?**
- *`SourceIndisponible: Base PostgreSQL injoignable`* : PostgreSQL est arrêté, ou une valeur de `.env` est fausse.
- *`password authentication failed`* : le mot de passe de `.env` est faux.
- *`permission denied for schema analytique`* : la mission 7 n'a pas été faite dans la base `olist`.
- *`syntax error at or near "..."`* : il reste un `...` dans ta requête.

➡️ [Journal › M9](journal_api_olist.md#j-m9)

---

<a id="m10"></a>
### Mission 10 — Basculer l'API sur PostgreSQL *(45 min)*

**Objectif** : l'API lit PostgreSQL, et répond **503** au lieu de planter si la base est indisponible.

**Méthode**
1. Dans `main.py`, remplace **tout** le début du fichier, des lignes `from fastapi import ...` jusqu'à `import donnees_csv as donnees ...` incluse, par ce bloc :
   ```python
   import os

   from dotenv import load_dotenv
   from fastapi import FastAPI, HTTPException, Path, Query, Request
   from fastapi.responses import JSONResponse
   from pydantic import BaseModel

   from erreurs import SourceIndisponible

   load_dotenv()
   if os.getenv("SOURCE_DONNEES", "csv") == "postgresql":
       import donnees_pg as donnees
   else:
       import donnees_csv as donnees
   ```
2. Juste **avant** la ligne `# ---------- Routes ----------`, ajoute :
   ```python
   # ---------- Erreur de source : 503 au lieu d'une erreur 500 illisible ----------
   @app.exception_handler(SourceIndisponible)
   def source_indisponible(request: Request, erreur: SourceIndisponible):
       return JSONResponse(status_code=503, content={"detail": str(erreur)})
   ```
3. Dans `.env`, remplace `SOURCE_DONNEES=csv` par `SOURCE_DONNEES=postgresql`.
4. **Arrête et relance l'API** (**Ctrl + C**, puis la commande uvicorn). `--reload` surveille les fichiers `.py`, pas le fichier `.env`.
5. Dans `/docs`, lance `/sante` : la source doit être `postgresql`. Relance quelques tests de la mission 6.
6. **Test de panne** : dans `.env`, mets `PGPORT=5999` (un port où rien n'écoute). Relance l'API, puis appelle `/indicateurs`. Note le code et le message. Remets `PGPORT=5432` et relance.

📘 **Ce que Rafael n'a pas eu à changer** : ni les adresses, ni les paramètres, ni le format des réponses. Seule la **cuisine** a changé.

✅ **Je vérifie**
- [ ] `/sante` affiche `"source": "postgresql"` et `110197` lignes.
- [ ] Avec `PGPORT=5999`, `/indicateurs` renvoie **503** avec `Base PostgreSQL injoignable`.
- [ ] `PGPORT` est revenu à `5432`.

➡️ [Journal › M10](journal_api_olist.md#j-m10)

---

<a id="m11"></a>
### Mission 11 — Écrire le client de Rafael *(60 min)*

**Objectif** : un script Python qui interroge l'API comme le fera le portail, vérifie les réponses et enregistre un fichier.

**Méthode**
1. L'API tourne dans le premier terminal. Ne l'arrête pas.
2. Ouvre `client.py`. Lis les fonctions fournies `appeler()` et `verifier()`, puis les blocs 1 et 2.
3. Complète les blocs 3 à 6 en suivant les blocs 1 et 2.
4. Lance-le dans le deuxième terminal : `py client.py`.

📘 **Ce que fait `requests.get()`** : exactement ce que fait ton navigateur. `params={"n": 3}` fabrique `?n=3` à ta place. `timeout=10` évite que le script attende sans fin. `.status_code` donne le code, `.json()` transforme la réponse en dictionnaire ou en liste Python.

📘 **Pour les blocs 4 et 5**, inspire-toi du bloc 3 : `appeler("/categories/top", {"n": 3}).json()`.

✅ **Je vérifie**
- [ ] Le script affiche **Bilan : 10/10 contrôles réussis**.
- [ ] Le fichier `ca_mensuel_2017.csv` est créé et contient 12 mois, plus la ligne d'en-tête.

➡️ [Journal › M11](journal_api_olist.md#j-m11)

---

<a id="m12"></a>
### Mission 12 — README et rendu *(60 min)*

**Objectif** : Rafael installe et lance ton API sans te poser une seule question.

**Méthode**
1. Complète `README.md` en remplaçant chaque `…`. Reprends les commandes **exactes** que tu as tapées depuis hier.
2. Pour chaque route, copie un exemple de réponse réel depuis `/docs`.
3. Relis `requirements.txt` : chaque bibliothèque importée dans un fichier `.py` y figure-t-elle ?
4. **Test de remise à zéro** : arrête l'API, supprime le dossier `__pycache__`, relance l'API en suivant **uniquement** ton README.
5. Prépare le rendu :
   - copie le dossier `api_olist` ;
   - dans la copie, supprime le sous-dossier `data/`, le fichier `.env` et le dossier `__pycache__` ;
   - compresse la copie en `api_olist_NOM.zip`.

✅ **Je vérifie**
- [ ] Le README ne contient plus de `…`.
- [ ] Le zip ne contient **ni** `.env`, **ni** `data/`.

➡️ [Journal › M12](journal_api_olist.md#j-m12)

[↑ Sommaire](#sommaire)

---

<a id="page-8"></a>
## Page 8 — Auto-évaluation, rendu et ressources

### ✅ Auto-évaluation (tout doit être coché)

**L'API**
- [ ] Elle démarre sans erreur avec la commande du README.
- [ ] Les 5 routes répondent avec les chiffres de référence, sur PostgreSQL.
- [ ] Les erreurs renvoient le bon code : 400, 404, 422, 503. Aucun test ne renvoie 500.
- [ ] `/docs` montre les 5 routes et leurs 5 modèles.

**La sécurité**
- [ ] La connexion utilise `lecteur_olist`, jamais `postgres`.
- [ ] Le mot de passe n'apparaît dans aucun fichier `.py` et n'est pas dans le zip.
- [ ] Toutes les requêtes SQL utilisent des paramètres `%(nom)s`.

**Le code et sa documentation**
- [ ] `verifier_sources.py` affiche 8/8 et `client.py` affiche 10/10.
- [ ] Le README permet d'installer, configurer et lancer l'API.
- [ ] Le journal est complet, sans « … » restant.

### 📤 Rendu sur Simplonline

Dépose **2 fichiers** :
1. `api_olist_NOM.zip` (sans `data/` ni `.env`)
2. `journal_api_olist.md` complété

### 📚 Ressources

- **Projet de départ** : `api_olist_depart.zip` (dossier `api_olist` et script `olist_ventes.sql`).
- **Documentation FastAPI**, en français pour l'essentiel : fastapi.tiangolo.com/fr — sections *Premiers pas*, *Paramètres de chemin*, *Paramètres de requête*, *Modèle de réponse*, *Gérer les erreurs*.
- **psycopg 3**, passage de paramètres : psycopg.org/psycopg3/docs/basic/params.html
- **requests** : requests.readthedocs.io — *Quickstart*.
- **Tes ressources** : le brief S42 (Python et PostgreSQL, compte en lecture seule), ton notebook pandas Olist de lundi.
- **Données** : Olist, *Brazilian E-Commerce Public Dataset* (Kaggle), licence CC BY-NC-SA 4.0.

### 🗺️ Les fichiers du projet, en une phrase chacun

- `main.py` : expose les routes (le **menu** et le **service**).
- `donnees_csv.py` / `donnees_pg.py` : calculent les indicateurs (la **cuisine**), à partir du CSV ou de PostgreSQL.
- `erreurs.py` : l'erreur `SourceIndisponible`, partagée par les fichiers ci-dessus.
- `client.py` : interroge l'API comme le portail de Rafael.
- `verifier_sources.py` : prouve que les deux cuisines donnent les mêmes plats.
- `.env` (privé) et `.env.exemple` (partagé) : la configuration et les secrets.
- `requirements.txt` : les bibliothèques à installer. `README.md` : le mode d'emploi.

---

*Données : Olist, « Brazilian E-Commerce Public Dataset », publiées sur Kaggle sous licence CC BY-NC-SA 4.0.*
