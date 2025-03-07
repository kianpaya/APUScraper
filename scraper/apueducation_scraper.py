import os
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin, urlparse

# Base URL (Wayback Machine snapshot)
base_url = "https://web.archive.org/web/20240911141314/https://apueducation.us/faculty-staff/"

# Set user-agent to avoid blocks
headers = {"User-Agent": "Mozilla/5.0"}

# Directories for saving scraped data
output_dir = "scraper/data/html"
image_dir = "scraper/data/images"
os.makedirs(output_dir, exist_ok=True)
os.makedirs(image_dir, exist_ok=True)

# Store visited pages to avoid duplicate scraping
visited_pages = set()
visited_images = set()

def clean_url(url):
    """Removes fragments and normalizes URLs."""
    return url.split("#")[0].strip("/")

def sanitize_filename(url):
    """Generate a safe filename from URL."""
    parsed = urlparse(url)
    filename = os.path.basename(parsed.path)
    if not filename:
        filename = f"image_{int(time.time())}.jpg"  # Fallback for missing names
    return filename

def scrape_page(url):
    """Scrape images and extract links from a given page."""
    url = clean_url(url)  # Remove fragments
    if url in visited_pages or not url.startswith(base_url):
        print(f"Skipping already visited or external URL: {url}")
        return  

    print(f"\n🟢 Visiting: {url}")
    visited_pages.add(url)

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Save HTML
        html_filename = urlparse(url).path.strip("/").replace("/", "_") or "index.html"
        html_path = os.path.join(output_dir, html_filename)
        with open(html_path, "w", encoding="utf-8") as file:
            file.write(soup.prettify())
        print(f"✅ Saved HTML to {html_path}")

        # Extract and log images
        img_urls = []
        for img in soup.find_all("img"):
            src = img.get("src") or img.get("data-src")  # Handle different attributes
            if src:
                full_url = urljoin(url, src)
                img_urls.append(full_url)

        print(f"🖼 Found {len(img_urls)} images on {url}")

        # Save image URLs to a text file
        img_links_path = os.path.join(output_dir, "image_links.txt")
        with open(img_links_path, "a", encoding="utf-8") as file:
            file.write("\n".join(img_urls) + "\n")

        # **Download images**
        for img_url in img_urls:
            time.sleep(2)  # Delay to avoid being blocked
            if img_url in visited_images:
                print(f"Skipping duplicate image: {img_url}")
                continue

            img_name = sanitize_filename(img_url)
            img_path = os.path.join(image_dir, img_name)

            if os.path.exists(img_path):
                print(f"Skipping {img_url}, already exists.")
                continue

            try:
                img_data = requests.get(img_url, headers=headers).content
                with open(img_path, "wb") as img_file:
                    img_file.write(img_data)
                visited_images.add(img_url)
                print(f"✅ Downloaded {img_url} -> {img_name}")
            except Exception as e:
                print(f"❌ Failed to download {img_url}: {e}")

        # Extract and visit new links
        links = [urljoin(url, a["href"]) for a in soup.find_all("a", href=True)]
        print(f"🔗 Found {len(links)} links on {url}")

        for link in links:
            if link.startswith(base_url) and link not in visited_pages:
                scrape_page(link)  

    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to process {url}: {e}")

# **Start the recursive scraping**
scrape_page(base_url)

print("🎉 Scraping complete!")
