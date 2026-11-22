
from pathlib import Path
from decimal import Decimal
import pandas as pd

from app import create_app
from extensions import db

from models.national_distribution import NationalDistribution
from models.zone_distribution import ZoneDistribution
from models.monthly_peak import MonthlyPeak
from models.pole_production import PoleProduction


# =====================================================
# CONFIGURATION
# =====================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "raw"

app = create_app()

MOIS = {
    "janvier": 1,
    "fevrier": 2,
    "février": 2,
    "mars": 3,
    "avril": 4,
    "mai": 5,
    "juin": 6,
    "juillet": 7,
    "aout": 8,
    "août": 8,
    "septembre": 9,
    "octobre": 10,
    "novembre": 11,
    "decembre": 12,
    "décembre": 12
}


# =====================================================
# OUTILS DE NETTOYAGE
# =====================================================

def convertir_decimal(valeur):
    """
    Convertit les nombres CSV :
    1 553       -> 1553
    25110,041   -> 25110.041
    """

    valeur = str(valeur).strip()

    valeur = (
        valeur.replace("\u00a0", "")
        .replace(" ", "")
        .replace(",", ".")
    )

    return Decimal(valeur)


def trouver_fichier(motif):
    fichiers = list(DATA_DIR.glob(motif))

    if len(fichiers) != 1:
        raise FileNotFoundError(
            f"Fichier introuvable ou ambigu : {motif}"
        )

    return fichiers[0]


def lire_csv(fichier):
    return pd.read_csv(
        fichier,
        sep=";",
        encoding="utf-8-sig",
        dtype=str,
        keep_default_na=False
    )


def sauvegarder(model, cles, valeurs):
    """
    Insère une nouvelle ligne ou actualise
    une ligne déjà existante.
    """

    objet = model.query.filter_by(**cles).first()

    if objet is None:
        objet = model(**cles, **valeurs)
        db.session.add(objet)
    else:
        for colonne, valeur in valeurs.items():
            setattr(objet, colonne, valeur)


# =====================================================
# 1. DISTRIBUTION NATIONALE
# =====================================================

def importer_distribution_nationale():

    fichier = trouver_fichier(
        "*ensemble*tunisie*.csv"
    )

    df = lire_csv(fichier)

    df = df.dropna(axis=1, how="all")

    colonne_volume = (
        "Volume_d'eau_distribué_par_SONEDE_1000m3"
    )

    for _, ligne in df.iterrows():

        annee = int(ligne["ANNEE"])

        mois = MOIS[ligne["Mois"].strip().lower()]

        volume = convertir_decimal(
            ligne[colonne_volume]
        )

        sauvegarder(
            NationalDistribution,
            {
                "year": annee,
                "month": mois
            },
            {
                "volume_1000m3": volume
            }
        )

    print("Distribution nationale : import terminé")


# =====================================================
# 2. DISTRIBUTION PAR ZONE
# =====================================================

def importer_distribution_zones():

    fichier = trouver_fichier(
        "*gouvernorat*.csv"
    )

    df = lire_csv(fichier)

    colonnes_mois = [
        "Janvier", "Fevrier", "Mars", "Avril",
        "Mai", "Juin", "Juillet", "Aout",
        "Septembre", "Octobre", "Novembre", "Decembre"
    ]

    for _, ligne in df.iterrows():

        annee = int(ligne["Annee"])

        nom_zone = ligne["Gouvernorat"].strip()

        est_coefficient = (
            nom_zone.casefold() == "coefficient de pointe mensuelle"
        )

        for nom_mois in colonnes_mois:

            mois = MOIS[nom_mois.lower()]

            valeur = convertir_decimal(
                ligne[nom_mois]
            )

            if est_coefficient:

                sauvegarder(
                    MonthlyPeak,
                    {
                        "year": annee,
                        "month": mois
                    },
                    {
                        "coefficient": valeur
                    }
                )

            else:

                sauvegarder(
                    ZoneDistribution,
                    {
                        "year": annee,
                        "month": mois,
                        "zone_name": nom_zone
                    },
                    {
                        "volume_1000m3": valeur
                    }
                )

    print("Distribution par zone : import terminé")


# =====================================================
# 3. PRODUCTION PAR POLE
# =====================================================

def importer_production():

    fichier = trouver_fichier(
        "*production*pole*.csv"
    )

    df = lire_csv(fichier)

    colonne_pole = "Pôles de production"

    colonne_production = (
        "Production_eau_potable_par_pôle_m3"
    )

    for _, ligne in df.iterrows():

        annee = int(ligne["Annee"])

        nom_pole = ligne[colonne_pole].strip()

        # Ignorer les lignes TOTAL
        if nom_pole.upper() == "TOTAL":
            continue

        production = convertir_decimal(
            ligne[colonne_production]
        )

        sauvegarder(
            PoleProduction,
            {
                "year": annee,
                "pole_name": nom_pole
            },
            {
                "production_mm3": production
            }
        )

    print("Production par pôle : import terminé")


# =====================================================
# EXECUTION
# =====================================================

if __name__ == "__main__":

    with app.app_context():

        db.create_all()

        print("Tables MySQL créées ou déjà existantes.")

        try:
            print("\n===== IMPORT SONEDE =====\n")

            importer_distribution_nationale()
            importer_distribution_zones()
            importer_production()

            db.session.commit()

            print("\n===== VERIFICATION =====")

            print("Distribution nationale :", NationalDistribution.query.count())
            print("Distribution par zone :", ZoneDistribution.query.count())
            print("Coefficients mensuels :", MonthlyPeak.query.count())
            print("Production par pôle :", PoleProduction.query.count())

            print("\nIMPORT TERMINE AVEC SUCCES !")

        except Exception as erreur:
            db.session.rollback()
            print("\nERREUR DURANT L'IMPORT :")
            print(erreur)
            raise