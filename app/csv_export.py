"""Génération de fichiers CSV (encodage UTF-8).

Équivalent du `CsvExporter` du projet Java : on construit une réponse HTTP
téléchargeable à partir d'un en-tête et de lignes de valeurs.
"""
import csv
import io

from flask import Response


def reponse_csv(nom_fichier: str, entetes: list[str], lignes: list[list]) -> Response:
    """Construit une réponse HTTP CSV téléchargeable.

    :param nom_fichier: nom du fichier proposé au téléchargement (ex : "maitres.csv")
    :param entetes: noms des colonnes (ligne d'en-tête)
    :param lignes: une liste par enregistrement (les valeurs sont converties en str)
    """
    tampon = io.StringIO()
    writer = csv.writer(tampon)
    writer.writerow(entetes)
    for ligne in lignes:
        writer.writerow(["" if v is None else str(v) for v in ligne])

    # ﻿ (BOM) : aide Excel à reconnaître l'UTF-8.
    contenu = "﻿" + tampon.getvalue()
    return Response(
        contenu,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={nom_fichier}"},
    )
