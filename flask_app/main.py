from flask import Flask
from run_scraper import run_scraper

def create_app():
    app = Flask(__name__)
    app.add_url_rule('/', 'index', lambda: 'Hello World!')
    app.add_url_rule('/run-scraper', 'run_scraper', run_scraper, methods=['GET'])
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0')
