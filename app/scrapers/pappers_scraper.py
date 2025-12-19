import time
import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app.driver import Driver


class PappersScraper:
    BASE_URL = "https://www.pappers.fr/recherche?q="

    def __init__(self, driver: Driver):
        self.driver = driver

    def enrich(self, rows: list[dict]) -> list[dict]:
        for idx, row in enumerate(rows, start=1):
            query = str(row.get("siret") or row.get("denominationUniteLegale"))
            if not query:
                logging.warning("[Pappers][%s] Pas de SIRET ou dénomination", idx)
                continue

            logging.info("[Pappers][%s] Scraping pour : %s", idx, query)
            data = self.scrape(query)

            row["adresse"] = data.get("adresse", "")
            row["nom"] = data.get("nom", "")
            row["prenom"] = data.get("prenom", "")

        return rows

    def scrape(self, query: str) -> dict:
        url = self.BASE_URL + query
        logging.info("[Pappers] Ouverture : %s", url)
        self.driver.get(url)
        time.sleep(2)

        # Si Pappers redirige directement vers la fiche établissement,
        # il n'y a pas de résultat à cliquer.
        if "recherche?q=" in self.driver.driver.current_url:
            try:
                first_link = WebDriverWait(self.driver.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a.SearchResults_link__Ak3y_"))
                )
                first_link.click()
                time.sleep(2)
                logging.info("[Pappers] Clic sur le premier résultat")
            except Exception as exc:
                logging.warning("[Pappers] Impossible de cliquer sur le premier résultat: %s", exc)

        try:
            adresse = self.driver.driver.find_element(
                By.XPATH,
                "//th[contains(text(), 'Adresse')]/following-sibling::td"
            ).text.strip()
            logging.info("[Pappers] Adresse trouvée")
        except Exception:
            adresse = ""
            logging.warning("[Pappers] Adresse non trouvée")

        try:
            dirigeant = self.driver.driver.find_element(
                By.XPATH,
                "//th[contains(text(), 'Dirigeant')]/following-sibling::td/a"
            ).text.strip()
            logging.info("[Pappers] Dirigeant trouvé")
        except Exception:
            dirigeant = ""
            logging.warning("[Pappers] Dirigeant non trouvé")

        nom, prenom = "", ""
        if dirigeant:
            parts = dirigeant.split(" ")
            if len(parts) >= 2:
                prenom = parts[-1]
                nom = " ".join(parts[:-1])
            else:
                prenom = dirigeant

        return {
            "adresse": adresse,
            "nom": nom,
            "prenom": prenom
        }
