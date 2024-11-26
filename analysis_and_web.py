import pandas as pd
import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import schedule

#Selenium ChromeDriver
CHROME_DRIVER_PATH = "C:/Users/11cha/Downloads/chromedriver-win32/chromedriver.exe"  
service = Service(CHROME_DRIVER_PATH)
SEARCH_QUERY = "EU Grants"
GOOGLE_URL = f"https://www.google.com/search?q={SEARCH_QUERY}&tbs=qdr:w"  

#file to store scraped articles(csv)
DATA_FILE = "data.csv"
SEEN_URLS_FILE = "seen_urls.txt"

# webDriver
def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    return webdriver.Chrome(service=service, options=options)

#scrapes articles
def scrape_articles():
    print(f"[{datetime.now()}] Starting scrape...")
    driver = get_driver()
    driver.get(GOOGLE_URL)

    articles = []
    seen_urls = set()

    #loads and savess previously seen URLs
    if os.path.exists(SEEN_URLS_FILE):
        with open(SEEN_URLS_FILE, "r") as f:
            seen_urls = set(f.read().splitlines())

    try:
        WebDriverWait(driver, 25).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.g"))
        )
        results = driver.find_elements(By.CSS_SELECTOR, "div.g")
        count = 0

        for result in results:
            if count >= 20:
                break

            #extract URL and title
            try:
                link = result.find_element(By.TAG_NAME, "a")
                url = link.get_attribute("href")

                if url in seen_urls:
                    continue

                
                link.click()
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )

                #extract content
                title = driver.title
                paragraphs = driver.find_elements(By.TAG_NAME, "p")
                content = " ".join([p.text for p in paragraphs])

                if content.strip():
                    articles.append({
                        "title": title,
                        "url": url,
                        "content": content,
                        "timestamp": datetime.now()
                    })
                    seen_urls.add(url)
                    count += 1

                driver.back()
                time.sleep(2)  

            except Exception as e:
                print(f"Error processing result: {e}")
                continue

    except Exception as e:
        print(f"Error occurred while scraping: {e}")

    finally:
        driver.quit()

    if articles:
        save_articles(articles)
    save_seen_urls(seen_urls)
    print(f"[{datetime.now()}] Scrape completed: {len(articles)} articles.")

#saves articles to csv file
def save_articles(articles):
    df = pd.DataFrame(articles)
    if not os.path.exists(DATA_FILE):
        df.to_csv(DATA_FILE, index=False)
    else:
        df.to_csv(DATA_FILE, mode='a', header=False, index=False)

#function to save seen URLs
def save_seen_urls(seen_urls):
    with open(SEEN_URLS_FILE, "w") as f:
        f.write("\n".join(seen_urls))

#SCHEDULER
#task to run every 5 hours
def scheduled_task():
    scrape_articles()

schedule.every(5).hours.do(scheduled_task)

if __name__ == "__main__":
    scrape_articles()  

    
    while True:
        schedule.run_pending()
        time.sleep(1)
