import json
from typing import Iterable


class JSONResultWriter:
    """
    Écrit les résultats dans un fichier JSON tout en filtrant les colonnes souhaitées.
    """

    def __init__(self, output_path: str, columns: list[str] | None = None):
        self.output_path = output_path
        self.columns = columns

    def write(self, records: Iterable[dict]):
        if self.columns:
            payload = [{column: record.get(column, "") for column in self.columns} for record in records]
        else:
            payload = list(records)

        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
