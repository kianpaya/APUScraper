import requests
from bs4 import BeautifulSoup

# Target URL (Wayback Machine snapshot)
url = "https://web.archive.org/web/20241112194819/https://apueducation.us/"

# Set user-agent to avoid blocks
headers = {"User-Agent": "Mozilla/5.0"}

# Fetch the webpage
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# Save HTML locally
with open("backup.html", "w", encoding="utf-8") as file:
    file.write(soup.prettify())

# Extract all links
links = [a["href"] for a in soup.find_all("a", href=True)]
print("Extracted Links:", links)
