import os
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin, urlparse

# Target URL
url = "https://web.archive.org/web/20241112194819/https://apueducation.us/"

# Set user-agent to avoid blocks
headers = {"User-Agent": "Mozilla/5.0"}

print("Fetching webpage...")
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# Create directories for saving data
output_dir = "scraper/data/html"
image_dir = "scraper/data/images"
os.makedirs(output_dir, exist_ok=True)
os.makedirs(image_dir, exist_ok=True)

# Save HTML locally
html_path = os.path.join(output_dir, "backup.html")
with open(html_path, "w", encoding="utf-8") as file:
    file.write(soup.prettify())
print(f"Saved HTML to {html_path}")

# Extract all image URLs
img_urls = []
for img in soup.find_all("img", src=True):
    img_url = urljoin(url, img["src"])  # Convert to absolute URL
    img_urls.append(img_url)

# Save image URLs to a text file
img_links_path = os.path.join(output_dir, "image_links.txt")
with open(img_links_path, "w", encoding="utf-8") as file:
    file.write("\n".join(img_urls))
print(f"Saved {len(img_urls)} image links to {img_links_path}")

# **Download images while keeping original names and avoiding overwriting**
for img_url in img_urls:
    time.sleep(2)  # Prevents getting blocked

    # Extract image filename from URL
    img_name = os.path.basename(urlparse(img_url).path)
    
    # If the filename is empty (some URLs might not have filenames), generate a unique one
    if not img_name:
        img_name = f"image_{int(time.time())}.jpg"

    img_path = os.path.join(image_dir, img_name)

    # Check if the file already exists
    if os.path.exists(img_path):
        print(f"Skipping {img_url}, already exists as {img_name}.")
        continue

    try:
        img_data = requests.get(img_url, headers=headers).content
        with open(img_path, "wb") as img_file:
            img_file.write(img_data)
        print(f"Downloaded {img_url} -> {img_name}")
    except Exception as e:
        print(f"Failed to download {img_url}: {e}")

print("Image download complete!")
