"""Génération d'une réponse HTTP CSV (téléchargement navigateur).

Fonction utilitaire appelée UNIQUEMENT par les vues : elle ne contient
aucune logique métier, elle transforme des lignes en fichier CSV.
"""
import csv
import io

from flask import make_response


def exporter_csv(nom_fichier: str, entetes: list, lignes: list):
    """Construit une réponse HTTP contenant un fichier CSV téléchargeable.

    :param nom_fichier: nom proposé au navigateur (ex. "talibes.csv").
    :param entetes: liste des noms de colonnes (1re ligne du fichier).
    :param lignes: liste de listes — une liste de valeurs par enregistrement.
    """
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(entetes)
    for ligne in lignes:
        writer.writerow(ligne)

    response = make_response(output.getvalue())
    # Content-Disposition: attachment => le navigateur télécharge le fichier.
    response.headers["Content-Disposition"] = f"attachment; filename={nom_fichier}"
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    return response
