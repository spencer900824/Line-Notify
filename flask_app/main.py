from flask import Flask
from run_scraper import run_scraper
from flask_apscheduler.scheduler import APScheduler
from driver.web_driver import ChromeDriver

def create_app():
    app = Flask(__name__)
    app.add_url_rule('/', 'index', lambda: 'ALIVE')

    chrome_driver = ChromeDriver(headless=True)

    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.add_job(id='run_scraper', func=run_scraper, args=[chrome_driver], trigger='interval', seconds=5)
    scheduler.start()
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0')
