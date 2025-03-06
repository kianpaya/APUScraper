import requests
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import urljoin

# Target URL (Wayback Machine snapshot)
url = "https://web.archive.org/web/20241112194819/https://apueducation.us/"

# Set user-agent to avoid blocks
headers = {"User-Agent": "Mozilla/5.0"}

# Create directories for saving data
output_dir = "scraper/data/html"
image_dir = "scraper/data/images"
os.makedirs(output_dir, exist_ok=True)
os.makedirs(image_dir, exist_ok=True)

# Fetch the webpage
print("Fetching webpage...")
response = requests.get(url, headers=headers)
time.sleep(2)  # Prevent getting blocked

# Parse the HTML
soup = BeautifulSoup(response.text, "html.parser")

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

# Extract all images and download them
image_tags = soup.find_all("img")
downloaded_images = 0

for img in image_tags:
    img_url = img.get("src")
    if not img_url:
        continue

    # Convert relative URLs to absolute URLs
    img_url = urljoin(url, img_url)
    
    # Get image name
    img_name = os.path.basename(img_url)
    img_path = os.path.join(image_dir, img_name)

    # Download the image
    try:
        img_response = requests.get(img_url, headers=headers)
        time.sleep(2)  # Prevent getting blocked
        if img_response.status_code == 200:
            with open(img_path, "wb") as img_file:
                img_file.write(img_response.content)
            print(f"Downloaded: {img_name}")
            downloaded_images += 1
    except Exception as e:
        print(f"Failed to download {img_url}: {e}")

print(f"Downloaded {downloaded_images} images to {image_dir}")
