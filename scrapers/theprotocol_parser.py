import logging
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup, Tag
import time
import random

# Configure logging for debugging and error tracking
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(), # Output to console
        logging.FileHandler("parser.log") # Save logs to file
    ]
)
logger = logging.getLogger(__name__)

def fetch_page_playwright(url: str) -> BeautifulSoup | None:
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
                locale="pl-PL",
                timezone_id="Europe/Warsaw"
            )
            page = context.new_page()

            # Navigate and wait for job cards to load
            logger.info(f"Loading page: {url}")
            page.goto(url, wait_until="networkidle", timeout=60000)

            # Wait for at least one job card to appear
            try:
                page.wait_for_selector('a[data-test="list-item-offer"]', timeout=30000)
            except PlaywrightTimeoutError:
                logger.warning(f"No job cards found within 30s on {url}. Possible soft block or empty page.")

            html = page.content()
            soup = BeautifulSoup(html, "html.parser")
            logger.info(f"Page loaded successfully: {url} | HTML length: {len(html)}")
            return soup

    except PlaywrightTimeoutError as e:
        logger.error(f"Timeout loading {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Critical error loading {url}: {type(e).__name__} - {e}")
        return None

def parse_single_offer(card: Tag) -> dict | None:
    try:
        title_tag = card.select_one('h2[data-test="text-jobTitle"]')
        title = title_tag.get_text(strip=True) if title_tag else None

        company_tag = card.select_one('div[data-test="text-employerName"]')
        company = company_tag.get_text(strip=True) if company_tag else None

        location_tag = card.select_one('div[data-test="text-workplaces"]')
        location = location_tag.get_text(strip=True) if location_tag else ""
        if location and ("Oferta w wielu lokalizacjach" in location)  or ("Multiple locations offer" in location):
            locations_tags = card.select('div[data-test="chip-location"]')
            location = [l.get_text(strip=True) for l in locations_tags]

        salary_tag = card.select_one('div[data-test="text-salary"]')
        salary = salary_tag.get_text(strip=True)  if salary_tag else None

        work_mode_tag = card.select_one('div[data-test="text-workModes"]')
        work_mode = work_mode_tag.get_text(strip=True) if work_mode_tag else None

        link = card.get("href")
        if link and not link.startswith("http"):
            link = "https://theprotocol.it" + link

        technologies_tags = card.select('div[data-test="chip-expectedTechnology"]')
        technologies = [t.get_text(strip=True) for t in technologies_tags] if technologies_tags else []


        return {
            "title": title,
            "company": company,
            "location" : location,
            "salary": salary,
            "Work Mode": work_mode,
            "link": link,
            "technologies": technologies,
        }
    except AttributeError as e:
        logger.warning(f"Missing tag in card: {e}")
        return None

    except Exception as e:
        logger.error(f"Error parsing card: {type(e).__name__} - {e}")
        return None

def parse_page(soup: BeautifulSoup) -> list[dict]:
    if not soup:
        logger.warning("Soup is None — page not loaded")
        return []

    vacancies = []
    try:
        #Parse each cards
        cards = soup.select('a[data-test="list-item-offer"]')
        logger.info(f"Found {len(cards)} job cards on page")

        for i, card in enumerate(cards, 1):
            vacancy = parse_single_offer(card)
            if vacancy:
                vacancies.append(vacancy)
            else:
                logger.debug(f"Skipped card {i} — parsing returned None")

        logger.info(f"Successfully parsed {len(vacancies)} vacancies")
        return vacancies

    except Exception as e:
        logger.error(f"Critical error parsing page: {type(e).__name__} - {e}")
        return []


def add_level_to_vacancies(vacancies: list[dict], level: str) -> list[dict]:
    for v in vacancies:
        v["level"] = level  # Junior, Trainee and Assistant.
    return vacancies




