import time

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
                print(f"[Pappers][{idx}] Pas de SIRET ou dénomination")
                continue

            print(f"[Pappers][{idx}] Scraping pour : {query}")
            data = self.scrape(query)

            row["adresse"] = data.get("adresse", "")
            row["nom"] = data.get("nom", "")
            row["prenom"] = data.get("prenom", "")

        return rows

    def scrape(self, query: str) -> dict:
        url = self.BASE_URL + query
        self.driver.get(url)
        time.sleep(2)

        try:
            first_link = WebDriverWait(self.driver.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.SearchResults_link__Ak3y_"))
            )
            first_link.click()
            time.sleep(2)
        except Exception:
            pass

        try:
            adresse = self.driver.driver.find_element(
                By.XPATH,
                "//th[contains(text(), 'Adresse')]/following-sibling::td"
            ).text.strip()
        except Exception:
            adresse = ""

        try:
            dirigeant = self.driver.driver.find_element(
                By.XPATH,
                "//th[contains(text(), 'Dirigeant')]/following-sibling::td/a"
            ).text.strip()
        except Exception:
            dirigeant = ""

        nom, prenom = "", ""
        if dirigeant:
            parts = dirigeant.split(" ")
            if len(parts) >= 2:
                nom = parts[-1]
                prenom = " ".join(parts[:-1])
            else:
                nom = dirigeant

        return {
            "adresse": adresse,
            "nom": nom,
            "prenom": prenom
        }
