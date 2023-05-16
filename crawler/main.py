from apscheduler.schedulers.blocking import BlockingScheduler
from crawler import crawl
from webDriver import ChromeDriver
from shopeenotify import job

# example
if __name__ == '__main__':
    scheduler = BlockingScheduler()
    driver = ChromeDriver().driver
    scheduler.add_job(crawl, 'interval', args=[driver], seconds=120)
    scheduler.start()

   
   
