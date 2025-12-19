import argparse
import logging
import math
import os
from concurrent.futures import ProcessPoolExecutor, as_completed

from app.driver import Driver
from app.readers.excel_reader import read as read_excel
from app.readers.json_reader import read as read_json
from app.scrapers.linkedin_scraper import LinkedInScraper
from app.scrapers.pappers_scraper import PappersScraper
from app.writers.json_writer import JSONResultWriter
from app.writers.mailer import Mailer
from app.writers.result_writer import ResultWriter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_COLUMNS = [
    "siret",
    "denominationUniteLegale",
    "adresse",
    "nom",
    "prenom",
    "linkedin_url",
]


def setup_logging() -> None:
    logs_dir = os.path.join(BASE_DIR, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    log_path = os.path.join(logs_dir, "scraper.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Workflow d'enrichissement d'entreprises.")
    parser.add_argument("--input-format", choices=["excel", "json"], default="excel")
    parser.add_argument("--input-file", help="Chemin vers le fichier source à enrichir.")
    parser.add_argument("--output-format", choices=["excel", "json"], default="excel")
    parser.add_argument("--output-file", help="Chemin du fichier enrichi.")
    parser.add_argument("--workers", type=int, default=1, help="Nombre de workers Selenium à lancer en parallèle.")
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Exécute les navigateurs en mode headless (recommandé avec plusieurs workers).",
    )
    return parser.parse_args()


def resolve_input_path(input_format: str, provided_path: str | None) -> str:
    if provided_path:
        return provided_path

    if input_format == "excel":
        return os.path.join(BASE_DIR, "data", "input.xlsx")
    return os.path.join(BASE_DIR, "data", "etablissements-20251215.json")


def resolve_output_path(output_format: str, provided_path: str | None) -> str:
    if provided_path:
        return provided_path

    return os.path.join(BASE_DIR, "output.xlsx" if output_format == "excel" else "output.json")


def load_rows(input_format: str, file_path: str) -> list[dict]:
    if input_format == "excel":
        return read_excel(file_path)
    if input_format == "json":
        return read_json(file_path)
    raise ValueError(f"Format d'entrée non supporté : {input_format}")


def build_writer(output_format: str, output_path: str):
    if output_format == "excel":
        return ResultWriter(output_path, DEFAULT_COLUMNS)
    if output_format == "json":
        return JSONResultWriter(output_path, DEFAULT_COLUMNS)
    raise ValueError(f"Format de sortie non supporté : {output_format}")


def process_chunk(task: tuple[int, list[dict], bool]) -> tuple[int, list[dict]]:
    """
    Traite un lot de lignes avec ses propres instances de webdriver/scrapers.
    """
    chunk_idx, chunk_rows, headless = task
    driver = Driver(headless=headless)
    try:
        pappers_scraper = PappersScraper(driver)
        chunk_rows = pappers_scraper.enrich(chunk_rows)

        linkedin_scraper = LinkedInScraper(driver)
        chunk_rows = linkedin_scraper.enrich(chunk_rows)
    finally:
        driver.quit()

    return chunk_idx, chunk_rows


def enrich_rows_sequential(rows: list[dict], headless: bool) -> list[dict]:
    driver = Driver(headless=headless)
    try:
        pappers_scraper = PappersScraper(driver)
        rows = pappers_scraper.enrich(rows)

        linkedin_scraper = LinkedInScraper(driver)
        rows = linkedin_scraper.enrich(rows)
    finally:
        driver.quit()
    return rows


def enrich_rows_parallel(rows: list[dict], workers: int, headless: bool) -> list[dict]:
    if not rows:
        return rows

    workers = max(1, min(workers, len(rows)))
    chunk_size = math.ceil(len(rows) / workers)
    tasks = []
    chunk_idx = 0
    for start in range(0, len(rows), chunk_size):
        chunk = rows[start:start + chunk_size]
        if chunk:
            tasks.append((chunk_idx, chunk, headless))
            chunk_idx += 1

    combined: list[tuple[int, list[dict]]] = []
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(process_chunk, task) for task in tasks]
        for future in as_completed(futures):
            combined.append(future.result())

    combined.sort(key=lambda item: item[0])
    enriched_rows: list[dict] = []
    for _, chunk_rows in combined:
        enriched_rows.extend(chunk_rows)
    return enriched_rows


def enrich_rows(rows: list[dict], workers: int, headless: bool) -> list[dict]:
    if workers <= 1:
        return enrich_rows_sequential(rows, headless)
    logging.info("Traitement parallèle avec %s workers...", workers)
    return enrich_rows_parallel(rows, workers, headless)


def main():
    setup_logging()
    args = parse_args()
    input_path = resolve_input_path(args.input_format, args.input_file)
    output_path = resolve_output_path(args.output_format, args.output_file)

    rows = load_rows(args.input_format, input_path)
    logging.info("Nombre de lignes à traiter : %s", len(rows))

    workers = max(1, args.workers)
    if args.output_format == "json":
        batch_size = 50
        open(output_path, "w", encoding="utf-8").close()
        total = len(rows)
        writer = build_writer(args.output_format, output_path)
        for batch_idx, start in enumerate(range(0, total, batch_size), start=1):
            batch = rows[start:start + batch_size]
            logging.info(
                "Début lot %s: lignes %s-%s",
                batch_idx,
                start + 1,
                start + len(batch),
            )
            enriched_batch = enrich_rows(batch, workers, args.headless)
            logging.info("Fin lot %s: %s lignes écrites", batch_idx, len(enriched_batch))
            writer.append_batch(enriched_batch)
        rows = []
    else:
        rows = enrich_rows(rows, workers, args.headless)
        writer = build_writer(args.output_format, output_path)
        writer.write(rows)

    mailer = Mailer("scraper.logpro@gmail.com", "ryop uslc xnbp apvh")
    mailer.send_email(
        to=["welance.mail@gmail.com", "act2011@hotmail.fr"],
        # to=["test.mail@gmail.com"],
        subject="Données récupérées sur les entreprises",
        body="Voici le fichier avec les données récupérées.",
        attachment=output_path,
    )


if __name__ == "__main__":
    main()
