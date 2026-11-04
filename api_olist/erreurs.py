"""Erreurs propres à l'API, partagées par main.py et les modules de données."""


class SourceIndisponible(Exception):
    """La source de données (fichier ou base) ne répond pas."""
