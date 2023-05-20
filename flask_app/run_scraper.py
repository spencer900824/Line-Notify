from scraper.mission import crawl_mops
from driver.web_driver import ChromeDriver
import traceback

def run_scraper(driver=None):
    try:
        if not driver:
            print("Init a new driver")
            driver = ChromeDriver()
        crawl_mops(driver.driver)
        print("OK", 200)
    except Exception as e :
        print(f"Error:  {e}\n{traceback.format_exc()}", 500)

# example
if __name__ == '__main__':
    run_scraper()
