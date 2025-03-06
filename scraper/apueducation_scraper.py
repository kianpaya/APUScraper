import requests
from bs4 import BeautifulSoup
import os

# Target URL (Wayback Machine snapshot)
url = "https://web.archive.org/web/20241112194819/https://apueducation.us/"

# Set user-agent to avoid blocks
headers = {"User-Agent": "Mozilla/5.0"}

# Fetch the webpage
response = requests.get(url, headers=headers)

# Parse the HTML
soup = BeautifulSoup(response.text, "html.parser")

# Create a directory for saving the data
output_dir = "scraper/data/html"
os.makedirs(output_dir, exist_ok=True)

# Save HTML locally
html_path = os.path.join(output_dir, "backup.html")
with open(html_path, "w", encoding="utf-8") as file:
    file.write(soup.prettify())

print(f"Saved HTML to {html_path}")

# Extract all links
links = [a["href"] for a in soup.find_all("a", href=True)]
print("Extracted Links:", links)

# Save links to a text file
with open(os.path.join(output_dir, "links.txt"), "w", encoding="utf-8") as file:
    file.write("\n".join(links))

print(f"Saved {len(links)} links to {output_dir}/links.txt")
