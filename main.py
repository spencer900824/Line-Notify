from scraper.mission import crawl_mops
from driver.web_driver import ChromeDriver
import os


# example
if __name__ == '__main__':
    driver = ChromeDriver().driver
    crawl_mops(driver)
