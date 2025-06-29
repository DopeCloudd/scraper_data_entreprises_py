import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app.driver import Driver


class LinkedInScraper:
    GOOGLE_SEARCH_URL = "https://www.google.com/search?q=site%3Alinkedin.com+"

    def __init__(self, driver: Driver):
        self.driver = driver

    def enrich(self, rows: list[dict]) -> list[dict]:
        for idx, row in enumerate(rows, start=1):
            prenom = row.get("prenom", "").strip()
            nom = row.get("nom", "").strip()
            adresse = row.get("adresse", "").strip()
            denomination = row.get("denominationUniteLegale", "").strip()

            if not prenom or not nom:
                print(f"[LinkedIn][{idx}] Pas de prénom ou nom pour la recherche")
                row["linkedin_url"] = ""
                continue

            # Essaie d'extraire la ville de l'adresse si possible
            ville = ""
            if adresse:
                try:
                    ville = adresse.split(",")[-1].strip()
                except Exception:
                    ville = ""

            # Construire la query enrichie
            parts = [f'"{prenom} {nom}"']
            if denomination:
                parts.append(f'"{denomination}"')
            if ville:
                parts.append(f'"{ville}"')

            query = " ".join(parts)

            print(f"[LinkedIn][{idx}] Recherche LinkedIn pour : {query}")
            url = self.search(query)
            row["linkedin_url"] = url

        return rows

    def search(self, query: str) -> str:
        url = self.GOOGLE_SEARCH_URL + query.replace(" ", "+")
        self.driver.get(url)
        time.sleep(2)

        try:
            results = WebDriverWait(self.driver.driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a"))
            )
            for link in results:
                href = link.get_attribute("href")
                if href and "linkedin.com/in" in href:
                    return href
        except Exception:
            pass

        return ""
