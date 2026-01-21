from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup, Tag

url = "https://theprotocol.it/filtry/python;t?sort=date"

def fetch_page_playwright(url: str) -> BeautifulSoup:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="pl-PL",
            timezone_id="Europe/Warsaw"
        )
        page = context.new_page()
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(3000) # download 10s
        html = page.content()
        soup = BeautifulSoup(html, "html.parser")

        if soup.title:
            print("Title page:", soup.title.string.strip())
        else:
            print("Title not found")
        browser.close()
        return soup

def parse_single_offer(card: Tag) -> dict:

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

    is_quick_apply_tag = card.select_one('span[data-test="text-quick-apply-badge"]')
    is_quick_apply = is_quick_apply_tag is not None

    level_tag = card.select_one('span[data-test="content-positionLevels"]')
    level = level_tag.get_text(strip=True) if level_tag else None


    return {
        "title": title,
        "company": company,
        "location" : location,
        "salary": salary,
        "Work Mode": work_mode,
        "link": link,
        "technologies": technologies,
        "is_quick_apply": is_quick_apply,
        "level" : level
    }


def parse_page(soup: BeautifulSoup) -> list[dict]:

    cards = soup.select('a[data-test="list-item-offer"],a[class="a4pzt2q"]') # find all cards

    print(f"Cards found on page: {len(cards)}") #Check that we found at least something

    #Parse each card
    vacancies = []
    for card in cards:
        vacancy = parse_single_offer(card)
        if vacancy.get("title"):
            vacancies.append(vacancy)

    return vacancies

if __name__ == "__main__":
    soup = fetch_page_playwright(url)
    vacancies = parse_page(soup)
    print(f"Total vacancies: {len(vacancies)}")
    for v in vacancies[:50]:
        print (v)



