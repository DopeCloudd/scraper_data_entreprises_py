import os

import pandas as pd


def read() -> list[dict]:
    """
    Lit le fichier Excel situé dans ./data/input.xlsx
    et retourne les lignes filtrées :
    - denominationUniteLegale non vide
    - denominationUniteLegale != '[ND]'
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    file_path = os.path.join(base_dir, "data", "input.xlsx")

    df = pd.read_excel(file_path)

    # Filtrer
    df = df[df["denominationUniteLegale"].str.strip() != "[ND]"]

    return df.to_dict(orient="records")
