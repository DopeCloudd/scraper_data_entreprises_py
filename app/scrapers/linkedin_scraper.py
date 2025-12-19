import time
import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app.driver import Driver


class LinkedInScraper:
    GOOGLE_SEARCH_URL = "https://www.google.com/search?q="

    def __init__(self, driver: Driver):
        self.driver = driver

    def enrich(self, rows: list[dict]) -> list[dict]:
        for idx, row in enumerate(rows, start=1):
            prenom = str(row.get("prenom", "")).strip()
            nom = str(row.get("nom", "")).strip()
            adresse = str(row.get("adresse", "")).strip()

            if not prenom or not nom:
                logging.warning("[LinkedIn][%s] Pas de prénom ou nom pour la recherche", idx)
                row["linkedin_url"] = ""
                continue

            # Extraire la partie après la dernière virgule
            ville_cp = adresse.split(",")[-1].strip()

            # Découper en mots
            ville_parts = ville_cp.split()

            # Enlever le CP si présent
            if len(ville_parts) >= 2:
                ville = " ".join(ville_parts[1:])
            else:
                ville = ville_cp

            # Construire la query enrichie
            parts = [f'{prenom} {nom}']
            if ville:
                parts.append(f'{ville}')
            parts.append("linkedin")

            query = " ".join(parts)

            logging.info("[LinkedIn][%s] Recherche LinkedIn pour : %s", idx, query)
            url = self.search(query, nom)
            row["linkedin_url"] = url

        return rows

    def search(self, query: str, nom: str) -> str:
        url = self.GOOGLE_SEARCH_URL + query.replace(" ", "+")
        logging.info("[LinkedIn] Ouverture : %s", url)
        self.driver.get(url)
        time.sleep(2)

        try:
            results = WebDriverWait(self.driver.driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a"))
            )
            nom_lower = nom.lower()

            for link in results:
                href = link.get_attribute("href")
                if href and "linkedin.com/in" in href and nom_lower in href.lower():
                    logging.info("[LinkedIn] Profil trouvé : %s", href)
                    return href
        except Exception as exc:
            logging.warning("[LinkedIn] Erreur pendant la recherche: %s", exc)

        logging.warning("[LinkedIn] Aucun profil trouvé")
        return ""
