import os
import time
import logging
import requests
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

# 📌 **Setup Logging**
logging.basicConfig(
    format="%(asctime)s - %(levelname)s: %(message)s", 
    level=logging.INFO,
    datefmt="%H:%M:%S"
)

# **Base URL**
base_url = "https://web.archive.org/web/20240911141314/https://apueducation.us/faculty-staff/"

# **Set up Selenium WebDriver**
chrome_options = Options()
chrome_options.add_argument("--start-maximized")  # Open browser in full-screen mode
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# **Initialize WebDriver**
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# **Directories for saving scraped data**
output_dir = "scraper/data/html"
image_dir = "scraper/data/images"
os.makedirs(output_dir, exist_ok=True)
os.makedirs(image_dir, exist_ok=True)

# **Tracking visited pages & images**
visited_pages = set()
visited_images = set()


def sanitize_filename(url):
    """Generate a safe filename from a URL."""
    parsed = urlparse(url)
    filename = os.path.basename(parsed.path)
    return filename if filename else f"image_{int(time.time())}.jpg"


# **Scroll the page to load content**
def scroll_page():
    """Scrolls down the page to load lazy-loaded images."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Wait for new content
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


# **Simulate mouse movement over images**
def hover_over_images():
    """Hover over images dynamically to prevent stale references."""
    logging.info("🖱 Hovering over images to trigger lazy loading...")
    img_elements = driver.find_elements(By.TAG_NAME, "img")  # Detect images

    for i in range(len(img_elements)):
        try:
            img_elements = driver.find_elements(By.TAG_NAME, "img")  # **Re-fetch images**
            if i >= len(img_elements):  
                continue

            img = img_elements[i]  
            ActionChains(driver).move_to_element(img).perform()  
            logging.info(f"Hovered over image {i+1}/{len(img_elements)}")
            WebDriverWait(driver, 2).until(EC.visibility_of(img))  # **Wait dynamically**
        except Exception as e:
            logging.warning(f"❌ Error hovering over image {i+1}: {e}")

            
def scrape_page(url):
    """Scrape images and extract links from a given page."""
    if url in visited_pages or not url.startswith(base_url):
        logging.warning(f"⏩ Skipping already visited or external URL: {url}")
        return  

    logging.info(f"🟢 Visiting: {url}")
    visited_pages.add(url)

    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        scroll_page()

        # **Save HTML**
        html_filename = urlparse(url).path.strip("/").replace("/", "_") or "index.html"
        html_path = os.path.join(output_dir, html_filename)
        with open(html_path, "w", encoding="utf-8") as file:
            file.write(driver.page_source)
        logging.info(f"✅ Saved HTML to {html_path}")

        # **Extract images**
        img_elements = driver.find_elements(By.TAG_NAME, "img")
        img_urls = [urljoin(url, img.get_attribute("src")) for img in img_elements if img.get_attribute("src")]

        logging.info(f"🖼 Found {len(img_urls)} images on {url}")

        # **Save image URLs to a text file**
        img_links_path = os.path.join(output_dir, "image_links.txt")
        with open(img_links_path, "a", encoding="utf-8") as file:
            file.write("\n".join(img_urls) + "\n")

        # **Download images**
        for img_url in img_urls:
            time.sleep(2)  
            if img_url in visited_images:
                logging.info(f"⏩ Skipping duplicate image: {img_url}")
                continue

            img_name = sanitize_filename(img_url)
            img_path = os.path.join(image_dir, img_name)

            if os.path.exists(img_path):
                logging.info(f"⏩ Skipping {img_url}, already exists.")
                continue

            try:
                img_data = requests.get(img_url, timeout=10).content
                with open(img_path, "wb") as img_file:
                    img_file.write(img_data)
                visited_images.add(img_url)
                logging.info(f"✅ Downloaded {img_url} -> {img_name}")
            except Exception as e:
                logging.warning(f"❌ Failed to download {img_url}: {e}")

        # **Extract and visit new links**
        links = [urljoin(url, a.get_attribute("href")) for a in driver.find_elements(By.TAG_NAME, "a") if a.get_attribute("href")]
        logging.info(f"🔗 Found {len(links)} links on {url}")

        for link in links:
            if link.startswith(base_url) and link not in visited_pages:
                scrape_page(link)  

    except Exception as e:
        logging.error(f"❌ Failed to process {url}: {e}")


# **Start the scraping process**
scrape_page(base_url)

logging.info("🎉 Scraping complete!")
input("Press ENTER to close the browser...")
driver.quit()
