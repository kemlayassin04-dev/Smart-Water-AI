from pathlib import Path
import pandas as pd
import csv

print("=== SMART WATER AI : DATA INSPECTION ===")

dossier = Path("data/raw")
fichiers = list(dossier.glob("*.csv"))

print("Nombre de fichiers :", len(fichiers))

for fichier in fichiers:

    print("\n" + "=" * 70)
    print("FICHIER :", fichier.name)

    with open(fichier, "r", encoding="utf-8-sig", errors="replace") as f:
        premiere_ligne = f.readline()

    try:
        dialecte = csv.Sniffer().sniff(
            premiere_ligne,
            delimiters=";,\t"
        )
        separateur = dialecte.delimiter
    except csv.Error:
        separateur = ";"

    df = pd.read_csv(
        fichier,
        sep=separateur,
        encoding="utf-8-sig"
    )

    print("SEPARATEUR :", repr(separateur))
    print("COLONNES :", df.columns.tolist())
    print("\n5 PREMIERES LIGNES :")
    print(df.head().to_string(index=False))
    print("\nDIMENSIONS :", df.shape)
    print("TYPES :", df.dtypes.to_dict())
    print("VALEURS MANQUANTES :", df.isnull().sum().to_dict())
print("\n=== INSPECTION TERMINEE ===")
