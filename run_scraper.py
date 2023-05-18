from scraper.mission import crawl_mops
from driver.web_driver import ChromeDriver


def run(driver=None):
    if driver is not ChromeDriver :
        driver = ChromeDriver().driver
    crawl_mops(driver)

# example
if __name__ == '__main__':
    run()
