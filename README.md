# API des indicateurs de ventes Olist

## Objet

Cette API est écrite en Python avec FastAPI, une bibliothèque Python qui sert à créer des API web. Elle permet de retourner les chiffres clés des ventes Olist enregistrées dans PostgreSQL : les ventes mensuelles, les meilleures catégories et les chiffres par État. Elle se connecte avec le compte `lecteur_olist`, qui peut seulement lire les données (`SELECT`).

## Prérequis

- Python 3.10 ou plus récent.
- PostgreSQL en cours d'exécution.
- DBeaver pour préparer la base `olist`.
- Git Bash sous Windows.

## Installation

1. Dans Git Bash, depuis la racine du projet, se placer dans le dossier `api_olist` :

```bash
cd api_olist
```

2. Créer et activer l'environnement virtuel, puis installer les bibliothèques nécessaires :

```bash
py -m venv .venv
source .venv/Scripts/activate
py -m pip install -r requirements.txt
```

## Configuration

1. Copier `.env.exemple` sous le nom `.env` dans le dossier `api_olist` :
   ```bash
   cp .env.exemple .env
   ```
2. Dans DBeaver, se connecter à PostgreSQL avec le compte `postgres`.
3. Créer la base `olist` si elle n'existe pas.
4. Dans le navigateur de bases, faire un clic droit sur la base `olist` elle-même, puis choisir **Outils > Exécuter le script**.
5. Dans la fenêtre **Script PostgreSQL**, cliquer sur l'icône de dossier à côté de **Input**.
6. Sélectionner `api_olist/olist_ventes.sql`, puis cliquer sur **Ouvrir**.
7. Cliquer sur **Démarrage** pour lancer le script.
8. Vérifier que le résultat final affiche `110197` lignes, `96478` commandes et `15424463.65` de chiffre d'affaires.
9. Dans DBeaver, configurer une connexion PostgreSQL avec `localhost`, le port `5432`, la base `olist` et l'utilisateur `lecteur_olist`. Laisser **Show all databases** décoché, saisir le mot de passe de ce compte, puis tester la connexion.
10. Dans `.env`, indiquer `SOURCE_DONNEES=postgresql` et renseigner `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER` et `PGPASSWORD` avec ces mêmes paramètres.
11. Ne pas partager `.env` : il contient des identifiants et est ignoré par Git.

Le script supprime puis recrée le schéma `analytique` dans la base sélectionnée. Il crée le compte `lecteur_olist` s'il n'existe pas et lui accorde les droits de lecture sur `olist`.

Le fichier `.env.exemple` donne les noms des variables à renseigner. `PGPASSWORD` correspond au mot de passe du compte de lecture défini lors de la création initiale du compte. Si ce compte existe déjà, conserver son mot de passe actuel.

## Lancement

Dans le dossier `api_olist`, avec l’environnement virtuel activé :

```bash
py -m uvicorn main:app --reload
```

- Ouvrir <http://127.0.0.1:8000/docs> pour afficher l'interface Swagger.
- Choisir une route, puis cliquer sur **Try it out** et **Execute** pour la tester.
- Pour voir une réponse directement, ouvrir par exemple <http://127.0.0.1:8000/sante>.

## Routes

**`GET /sante`**
- Rôle : vérifie que l'API répond et indique la source de données.
- Paramètres : aucun.
- Exemple de réponse :
  ```json
  {"statut":"ok","source":"postgresql","nb_lignes":110197}
  ```

**`GET /indicateurs`**
- Rôle : renvoie les chiffres clés de toute la période.
- Paramètres : aucun.
- Exemple de réponse :
  ```json
  {"nb_lignes":110197,"nb_commandes":96478,"ca_total":15424463.65,"panier_moyen":159.88}
  ```

**`GET /ventes/mensuelles`**
- Rôle : renvoie le chiffre d'affaires et le nombre de commandes, mois par mois.
- Paramètres : `debut` et `fin` sont facultatifs, au format `AAAA-MM`. Les bornes sont incluses.
- Exemple d'appel : <http://127.0.0.1:8000/ventes/mensuelles?debut=2017-11&fin=2017-11>
- Exemple de réponse : `[{"mois":"2017-11","ca":1154559.53,"nb_commandes":7289}]`

**`GET /categories/top`**
- Rôle : renvoie les catégories classées par chiffre d'affaires décroissant.
- Paramètres : `n`, nombre de catégories entre 1 et 50 ; valeur par défaut : 10.
- Exemple d'appel : <http://127.0.0.1:8000/categories/top?n=3>

**`GET /etats/{code_etat}`**
- Rôle : renvoie les chiffres de vente d'un État brésilien.
- Paramètres : `code_etat`, code de l'État sur deux lettres, par exemple `SP`.
- Exemple d'appel : <http://127.0.0.1:8000/etats/SP>
- Exemple de réponse : `{"etat":"SP","ca":5771713.93,"nb_commandes":40501,"part_ca":37.42}`

## Codes de réponse

- `200` : requête réussie.
- `400` : période incohérente ; `debut` est après `fin`.
- `404` : aucune vente pour l'État demandé.
- `422` : paramètre invalide, par exemple `n=0` ou un mois mal écrit.
- `503` : source de données indisponible.

## Sécurité

- Les identifiants PostgreSQL sont stockés dans `.env`, jamais dans le code. Ce fichier ne doit pas être partagé.
- L'API se connecte avec `lecteur_olist`, qui a uniquement le droit `SELECT`.
- Les valeurs des requêtes SQL sont transmises avec des paramètres psycopg (`%(nom)s`) pour éviter l'injection SQL.

## Données

Olist, *Brazilian E-Commerce Public Dataset* (Kaggle), licence CC BY-NC-SA 4.0. Données des commandes livrées entre septembre 2016 et août 2018. Utilisation sous licence.
