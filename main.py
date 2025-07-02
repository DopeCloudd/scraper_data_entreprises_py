from app.driver import Driver
from app.readers.excel_reader import read
from app.scrapers.linkedin_scraper import LinkedInScraper
from app.scrapers.pappers_scraper import PappersScraper
from app.writers.mailer import Mailer
from app.writers.result_writer import ResultWriter


def main():
    rows = read()
    # Juste 2 lignes pour le test
    # rows = rows[:2]
    print(f"Nombre de lignes à traiter : {len(rows)}")

    driver = Driver(headless=False)

    # Scraper Pappers
    pappers_scraper = PappersScraper(driver)
    rows = pappers_scraper.enrich(rows)

    # Scraper LinkedIn
    linkedin_scraper = LinkedInScraper(driver)
    rows = linkedin_scraper.enrich(rows)

    driver.quit()

    # Colonnes souhaitées
    columns = [
        "siret",
        "denominationUniteLegale",
        "adresse",
        "nom",
        "prenom",
        "linkedin_url"
    ]

    # Écriture
    writer = ResultWriter("output.xlsx", columns)
    writer.write(rows)

    # Envoi email
    mailer = Mailer("scraper.logpro@gmail.com", "ryop uslc xnbp apvh")
    mailer.send_email(
        to=["welance.mail@gmail.com", "act2011@hotmail.fr"],
        # to=["test.mail@gmail.com"],
        subject="Données récupérées sur les entreprises",
        body="Voici le fichier avec les données récupérées.",
        attachment="output.xlsx"
    )


if __name__ == "__main__":
    main()
