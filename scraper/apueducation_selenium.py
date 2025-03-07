import os
import time
import requests
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Base URL
base_url = "https://web.archive.org/web/20240911141314/https://apueducation.us/"

# Set up Selenium WebDriver (Visible Mode for Debugging)
chrome_options = Options()
chrome_options.add_argument("--start-maximized")  # Open browser in full-screen mode
chrome_options.add_argument("--disable-gpu")  
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Initialize WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Directories for saving scraped data
output_dir = "scraper/data/html"
image_dir = "scraper/data/images"
os.makedirs(output_dir, exist_ok=True)
os.makedirs(image_dir, exist_ok=True)

# Track visited pages & images
visited_pages = set()
visited_images = set()

def sanitize_filename(url):
    """Generate a safe filename from a URL."""
    parsed = urlparse(url)
    filename = os.path.basename(parsed.path)
    return filename if filename else f"image_{int(time.time())}.jpg"

def scroll_page():
    """Scrolls down the page to load dynamically loaded images."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Allow time for loading
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def scrape_page(url):
    """Scrape images and extract links from a given page."""
    if url in visited_pages or not url.startswith(base_url):
        print(f"Skipping already visited or external URL: {url}")
        return  

    print(f"\n🟢 Visiting: {url}")
    visited_pages.add(url)

    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        scroll_page()

        # Save HTML
        html_filename = urlparse(url).path.strip("/").replace("/", "_") or "index.html"
        html_path = os.path.join(output_dir, html_filename)
        with open(html_path, "w", encoding="utf-8") as file:
            file.write(driver.page_source)
        print(f"✅ Saved HTML to {html_path}")

        # Extract images dynamically
        img_elements = driver.find_elements(By.TAG_NAME, "img")
        img_urls = [urljoin(url, img.get_attribute("src")) for img in img_elements if img.get_attribute("src")]

        print(f"🖼 Found {len(img_urls)} images on {url}")

        # Save image URLs to a text file
        img_links_path = os.path.join(output_dir, "image_links.txt")
        with open(img_links_path, "a", encoding="utf-8") as file:
            file.write("\n".join(img_urls) + "\n")

        # **Download images**
        for img_url in img_urls:
            time.sleep(2)  
            if img_url in visited_images:
                print(f"Skipping duplicate image: {img_url}")
                continue

            img_name = sanitize_filename(img_url)
            img_path = os.path.join(image_dir, img_name)

            if os.path.exists(img_path):
                print(f"Skipping {img_url}, already exists.")
                continue

            try:
                img_data = requests.get(img_url, timeout=10).content
                with open(img_path, "wb") as img_file:
                    img_file.write(img_data)
                visited_images.add(img_url)
                print(f"✅ Downloaded {img_url} -> {img_name}")
            except Exception as e:
                print(f"❌ Failed to download {img_url}: {e}")

        # Extract and visit new links
        links = [urljoin(url, a.get_attribute("href")) for a in driver.find_elements(By.TAG_NAME, "a") if a.get_attribute("href")]
        print(f"🔗 Found {len(links)} links on {url}")

        for link in links:
            if link.startswith(base_url) and link not in visited_pages:
                scrape_page(link)  

    except Exception as e:
        print(f"❌ Failed to process {url}: {e}")

# **Start the recursive scraping**
scrape_page(base_url)

print("🎉 Scraping complete!")
driver.quit()
