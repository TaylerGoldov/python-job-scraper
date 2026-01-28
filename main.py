from scrapers.theprotocol_parser import fetch_page_playwright, parse_page, add_level_to_vacancies
import pandas as pd

# Our url
url_python_junior = "https://theprotocol.it/filtry/python;t/junior;p?sort=date"
url_python_trainee = "https://theprotocol.it/filtry/python;t/trainee;p?sort=date"
url_python_assistant = "https://theprotocol.it/filtry/python;t/assistant;p?sort=date"

def main():
    print("We're starting to parse job postings with theprotocol.it...")

    # Junior
    print("\nParse junior...")
    soup_junior = fetch_page_playwright(url_python_junior)
    vacancies_junior = parse_page(soup_junior)
    vacancies_junior = add_level_to_vacancies(vacancies_junior, "Junior")
    print(f"Found junior: {len(vacancies_junior)}")

    # Trainee
    print("\nParse trainee...")
    soup_trainee = fetch_page_playwright(url_python_trainee)
    vacancies_trainee = parse_page(soup_trainee)
    vacancies_trainee = add_level_to_vacancies(vacancies_trainee, "Trainee")
    print(f"Found trainee: {len(vacancies_trainee)}")

    #Assistant
    print("\nParse assistant...")
    soup_assistant = fetch_page_playwright(url_python_assistant)
    vacancies_assistant = parse_page(soup_assistant)
    vacancies_assistant = add_level_to_vacancies(vacancies_assistant,"Assistant")
    print(f"Found assistant: {len(vacancies_assistant)}")

    # Unite
    vacancies = vacancies_junior + vacancies_trainee + vacancies_assistant

    df_data = []
    for v in vacancies:
        row = {
            "title": v.get("title", ""),
            "company": v.get("company", ""),
            "location": v.get("location", ""),
            "salary": v.get("salary", ""),
            "Work Mode": v.get("Work Mode", ""),
            "link": v.get("link", ""),
            "technologies": ", ".join(v.get("technologies", [])) if isinstance(v.get("technologies"), list) else v.get(
                "technologies", ""),
            "level": v.get("level", "Unknown")
        }
        df_data.append(row)

    # Create DataFrame
    df = pd.DataFrame(df_data)

    # Sort (optionally by level or name)
    df = df.sort_values(by=["level", "title"])

    # Save
    df.to_csv("works_offers.csv", index=False, encoding="utf-8-sig")

if __name__ == "__main__":
    main()