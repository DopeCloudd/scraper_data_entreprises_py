import json
import os
from typing import Iterable


class JSONResultWriter:
    """
    Écrit les résultats dans un fichier JSON tout en filtrant les colonnes souhaitées.
    """

    def __init__(self, output_path: str, columns: list[str] | None = None):
        self.output_path = output_path
        self.columns = columns

    def _filter_records(self, records: Iterable[dict]) -> list[dict]:
        if self.columns:
            return [{column: record.get(column, "") for column in self.columns} for record in records]
        return list(records)

    def write(self, records: Iterable[dict]):
        payload = self._filter_records(records)

        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    def append_batch(self, records: Iterable[dict]) -> None:
        payload = self._filter_records(records)
        if not payload:
            return

        serialized = [json.dumps(record, ensure_ascii=False) for record in payload]
        if not os.path.exists(self.output_path) or os.path.getsize(self.output_path) == 0:
            with open(self.output_path, "w", encoding="utf-8") as f:
                f.write("[\n")
                for idx, item in enumerate(serialized):
                    if idx:
                        f.write(",\n")
                    f.write(f"  {item}")
                f.write("\n]\n")
            return

        with open(self.output_path, "r+", encoding="utf-8") as f:
            f.seek(0, os.SEEK_END)
            pos = f.tell() - 1
            while pos >= 0:
                f.seek(pos)
                char = f.read(1)
                if not char.isspace():
                    break
                pos -= 1

            if pos < 0 or char != "]":
                raise ValueError("Le fichier JSON de sortie est invalide ou incomplet.")

            pos2 = pos - 1
            while pos2 >= 0:
                f.seek(pos2)
                char2 = f.read(1)
                if not char2.isspace():
                    break
                pos2 -= 1

            has_records = pos2 >= 0 and char2 != "["
            f.truncate(pos)
            f.seek(pos)

            if has_records:
                f.write(",\n")
            else:
                f.write("\n")

            for idx, item in enumerate(serialized):
                if idx:
                    f.write(",\n")
                f.write(f"  {item}")
            f.write("\n]\n")
