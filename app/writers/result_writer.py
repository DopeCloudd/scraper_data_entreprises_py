import pandas as pd


class ResultWriter:
    """
    Écrit les résultats dans un fichier Excel, avec les colonnes choisies.
    """
    def __init__(self, output_path: str, columns: list[str]):
        self.output_path = output_path
        self.columns = columns

    def write(self, records: list[dict]):
        df = pd.DataFrame(records)

        # Garder uniquement les colonnes spécifiées
        df = df.reindex(columns=self.columns)

        df.to_excel(self.output_path, index=False)
