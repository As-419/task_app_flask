"""Hiérarchie d'exceptions métier de la Daara.

Toutes héritent de `DaaraException` (qui étend RuntimeError).
Règle du sujet : elles sont levées ET capturées dans la couche views,
puis affichées à l'utilisateur via flash().
"""


class DaaraException(RuntimeError):
    """Ancêtre commun de toutes les exceptions métier de l'application."""


# --- Maitre -----------------------------------------------------------------
class MaitreIntrouvableException(DaaraException):
    def __init__(self, matricule: str):
        super().__init__(f"Aucun maître pour le matricule : {matricule}")


class MaitreDejaExistantException(DaaraException):
    def __init__(self, matricule: str):
        super().__init__(f"Un maître existe déjà avec le matricule : {matricule}")


# --- Classe -----------------------------------------------------------------
class ClasseIntrouvableException(DaaraException):
    def __init__(self, code: str):
        super().__init__(f"Aucune classe pour le code : {code}")


class ClasseDejaExistanteException(DaaraException):
    def __init__(self, code: str):
        super().__init__(f"Une classe existe déjà avec le code : {code}")


# --- Talibe -----------------------------------------------------------------
class TalibeIntrouvableException(DaaraException):
    def __init__(self, matricule: str):
        super().__init__(f"Aucun talibé pour le matricule : {matricule}")


class TalibeDejaExistantException(DaaraException):
    def __init__(self, matricule: str):
        super().__init__(f"Un talibé existe déjà avec le matricule : {matricule}")


# --- Progression ------------------------------------------------------------
class ProgressionIntrouvableException(DaaraException):
    def __init__(self, progression_id: int):
        super().__init__(f"Aucune progression pour l'identifiant : {progression_id}")


class ProgressionInvalideException(DaaraException):
    """Progression incohérente : versets négatifs, sourate vide, talibé absent."""

    def __init__(self, message: str):
        super().__init__(message)


# --- Suppression ------------------------------------------------------------
class SuppressionImpossibleException(DaaraException):
    """Suppression interdite car une relation existe encore
    (maître ayant des classes, classe ayant des talibés)."""

    def __init__(self, message: str):
        super().__init__(message)
