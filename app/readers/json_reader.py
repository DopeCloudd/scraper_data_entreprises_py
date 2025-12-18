import json
import os


def read(file_path: str | None = None) -> list[dict]:
    """
    Lit le fichier JSON contenant une liste d'établissements et
    retourne des enregistrements prêts à être enrichis.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    path = file_path or os.path.join(base_dir, "data", "etablissements-20251215.json")

    with open(path, "r", encoding="utf-8") as f:
        etablissements = json.load(f)

    rows: list[dict] = []
    for etablissement in etablissements:
        unite = etablissement.get("uniteLegale") or {}
        denomination = str(unite.get("denominationUniteLegale") or "").strip()

        if not denomination or denomination == "[ND]":
            continue

        row = {
            "siret": str(etablissement.get("siret", "")).strip(),
            "denominationUniteLegale": denomination,
            "adresse": _format_adresse(etablissement.get("adresseEtablissement") or {}),
            "nom": str(unite.get("nomUniteLegale") or "").strip(),
            "prenom": str(unite.get("prenomUsuelUniteLegale") or "").strip(),
            "linkedin_url": "",
        }
        rows.append(row)

    return rows


def _format_adresse(adresse: dict) -> str:
    voie = " ".join(
        part
        for part in [
            str(adresse.get("numeroVoieEtablissement") or "").strip(),
            str(adresse.get("typeVoieEtablissement") or "").strip(),
            str(adresse.get("libelleVoieEtablissement") or "").strip(),
        ]
        if part
    )

    ville = " ".join(
        part
        for part in [
            str(adresse.get("codePostalEtablissement") or "").strip(),
            str(adresse.get("libelleCommuneEtablissement") or "").strip(),
        ]
        if part
    )

    components = [component for component in (voie, ville) if component]
    return ", ".join(components)
