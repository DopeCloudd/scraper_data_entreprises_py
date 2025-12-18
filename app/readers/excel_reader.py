import os

import pandas as pd


def read(file_path: str | None = None) -> list[dict]:
    """
    Lit le fichier Excel (./data/input.xlsx par défaut) et filtre les lignes :
    - denominationUniteLegale != '[ND]'
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    path = file_path or os.path.join(base_dir, "data", "input.xlsx")

    df = pd.read_excel(path)

    # Filtrer
    df = df[df["denominationUniteLegale"].str.strip() != "[ND]"]

    return df.to_dict(orient="records")
