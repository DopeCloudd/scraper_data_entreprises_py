from app.scrapers.linkedin_scraper import LinkedInScraper
from app.scrapers.pappers_scraper import PappersScraper


class ScraperService:
    """
    Orchestrateur qui combine tous les scrapers.
    """
    def __init__(self, driver):
        self.pappers_scraper = PappersScraper(driver)
        self.linkedin_scraper = LinkedInScraper(driver)

    def scrape_all(self, siret_or_name: str) -> dict:
        pappers_data = self.pappers_scraper.scrape(siret_or_name)
        linkedin_url = self.linkedin_scraper.search(siret_or_name)

        return {
            "pappers": pappers_data,
            "linkedin_url": linkedin_url,
        }
