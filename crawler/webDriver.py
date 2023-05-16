from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
class ChromeDriver(object):
    def __init__(self):
#        self.cdm = ChromeDriverManager().install()
        self.options = Options()
        self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.driver = webdriver.Chrome( options=self.options)

    def __delete__(self):
        self.driver.quit()




if __name__ == '__main__':
    driver = ChromeDriver().driver
    driver.get('https://www.google.com')
    print(driver.title)
    