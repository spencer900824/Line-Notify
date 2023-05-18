from scraper.mission import crawl_mops
from driver.web_driver import ChromeDriver
import traceback

def run_scraper(driver=None):
    try:
        if driver is not ChromeDriver :
            driver = ChromeDriver().driver
        crawl_mops(driver)
        return "OK", 200
    except Exception as e :
        return f"Error:  {e}\n{traceback.format_exc()}", 500

# example
if __name__ == '__main__':
    run_scraper()
