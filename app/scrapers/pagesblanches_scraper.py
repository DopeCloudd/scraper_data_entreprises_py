import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app.driver import Driver


class PagesBlanchesScraper:
    """
    Recherche téléphone du dirigeant via Google et Pages Blanches.
    """
    GOOGLE_SEARCH_URL = "https://www.google.com/search?q=site%3Apagesjaunes.fr/pagesblanches+"

    def __init__(self, driver: Driver):
        self.driver = driver

    def enrich(self, rows: list[dict]) -> list[dict]:
        for idx, row in enumerate(rows, start=1):
            prenom = row.get("prenom", "").strip()
            nom = row.get("nom", "").strip()
            adresse = row.get("adresse", "").strip()

            if not prenom or not nom:
                print(f"[PagesBlanches][{idx}] Pas de prénom ou nom pour la recherche")
                row["telephone"] = ""
                continue

            # Essayer d'extraire la ville
            ville = ""
            if adresse:
                try:
                    ville = adresse.split(",")[-1].strip()
                except Exception:
                    ville = ""

            # Construire la query enrichie
            parts = [f'"{prenom} {nom}"']
            if ville:
                parts.append(f'"{ville}"')

            query = " ".join(parts)

            print(f"[PagesBlanches][{idx}] Recherche téléphone pour : {query}")
            phone = self.search(query)
            row["telephone"] = phone

        return rows

    def search(self, query: str) -> str:
        url = self.GOOGLE_SEARCH_URL + query.replace(" ", "+")
        self.driver.get(url)
        time.sleep(2)

        try:
            results = WebDriverWait(self.driver.driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a"))
            )
            first_url = ""
            for link in results:
                href = link.get_attribute("href")
                if href and "pagesjaunes.fr/pagesblanches" in href:
                    first_url = href
                    break

            if not first_url:
                return ""

            self.driver.get(first_url)
            time.sleep(2)

            # Chercher le téléphone
            phone_el = self.driver.driver.find_element(
                By.CSS_SELECTOR,
                "a[href^='tel:']"
            )
            phone = phone_el.get_attribute("href").replace("tel:", "").strip()
            return phone

        except Exception:
            return ""
