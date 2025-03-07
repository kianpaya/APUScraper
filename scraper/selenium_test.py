import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# 1️⃣ Setup Chrome in normal mode (not headless)
chrome_options = Options()
chrome_options.add_argument("--start-maximized")  # Open in full-screen mode
chrome_options.add_argument("--disable-gpu")      # Fix potential GPU issues
chrome_options.add_argument("--no-sandbox")       # Bypass sandboxing issues

# 2️⃣ Initialize WebDriver using explicit chromedriver path
service = Service("/usr/bin/chromedriver")  # Explicitly specify the path
driver = webdriver.Chrome(service=service, options=chrome_options)

# 3️⃣ Open Google and Search for "Selenium Testing"
driver.get("https://www.google.com")

# 🛑 BREAKPOINT 1: Check if page loaded
print("Page Title:", driver.title)  # Should print "Google"
time.sleep(2)

# 4️⃣ Find the search box, enter "Selenium Testing", and press Enter
search_box = driver.find_element(By.NAME, "q")
search_box.send_keys("Selenium Testing")
search_box.send_keys(Keys.RETURN)

# 🛑 BREAKPOINT 2: Wait for search results
time.sleep(3)
print("New Page Title:", driver.title)  # Should include "Selenium Testing"

# 5️⃣ Extract and print search results
results = driver.find_elements(By.CSS_SELECTOR, "h3")
for i, result in enumerate(results[:5]):  # Print first 5 results
    print(f"Result {i+1}: {result.text}")

# 🛑 BREAKPOINT 3: Pause before closing
time.sleep(3)

# 6️⃣ Close the browser
driver.quit()
print("✅ Test Completed!")
