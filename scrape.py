import requests
from bs4 import BeautifulSoup

# BASE_URL = "https://www.nita.go.ug"
BASE_URL = "https://consumer.nita.go.ug"
pages_to_scrape = [
    "/",
    "/services/it-consumer-protection-and-compliance-in-uganda/",
    "/services/arbitration-framework-for-it-consumer-protection-in-uganda/",
    "/services/uganda-legal-framework-for-tech-and-consumer-protection/",
    "/faqs/"
    # "/leased-lines",
    # "/dark-fibre",
    # "/bulk internet",
    # "/myug wifi",
    # "/data-center",
    # "/unified-messaging-and-collaboration-system",
    # "/system-app-development",
    # "/ ELECTRONIC SOLUTIONS",
    # "/node/280",
    # "/ughub",
    # "/ugpass",
    # "/services-and-guidelines/website-development",
    # "/certug",
    # "/gou-it-servicedesk",
    # "/Technical Services",
    # "/IT Advisory Services",
    # "/Capacity Development and Skilling",
    # "/I.T Certification",
    # "/services-and-guidelines/data-protection-and-privacy",
    # "/node/275",
    # "/node/277",
    # "/node/276",
    # "/laws-regulations-0",
    # "/guidelines-it-standards-0",
    # "/security",
    # "/nita-u-publications",
    # "/downloadable-forms",
    # "/publications/reports/national-it-survey/all",
    # "/reports",
    # "/faqs",
    # "/UDAP-GOVNET_Documents",
    # "/projects-service-portfolio/regional-communications-infrastructure-programrcip",
    # "/projects-service-portfolio/business-process-outsourcing-it-enabled-services",
    # "/projects-service-portfolio/uganda-enterprise-architecture-and-interoperability-framework",
    # "/projects-service-portfolio/national-backbone-infrastructure-project-nbiegi",
    # "/advice-consumer-1",
    # "/consumer-advice-2"
]

scraped_text = ""

for path in pages_to_scrape:
    full_url = BASE_URL + path
    try:
        response = requests.get(full_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.find("h1")
        if title:
            scraped_text += f"### {title.text.strip()}\n\n"

        # Collect paragraphs
        for para in soup.find_all("p"):
            text = para.get_text(strip=True)
            if len(text) > 40:
                scraped_text += text + "\n\n"

        print(f"[✓] Scraped: {full_url}")
    except Exception as e:
        print(f"[X] Failed: {full_url} - {e}")

# Save output
file_path = "rag_docs.txt"
with open(file_path, "w", encoding="utf-8") as f:
    f.write(scraped_text)

file_path
