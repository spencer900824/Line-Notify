from flask import Flask, request, abort
from run_scraper import run_scraper
from flask_apscheduler.scheduler import APScheduler
from driver.web_driver import ChromeDriver
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import json
import logging

logger = logging.getLogger(__name__)


keywords = []


with open('config.json','r',encoding='utf-8') as f:
    config = json.loads(f.read())

access_token = config['access_token']
secret = config['secret']

# Channel Access Token 和 Channel Secret
line_bot_api = LineBotApi(access_token)
handler = WebhookHandler(secret)

flag = {}
temp_users_keywords = {}


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global flag, temp_users_keywords
    text = event.message.text
    if(text == "重新設定"):
        temp_users_keywords[event.source.user_id] = []
        flag[event.source.user_id] = 1
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='請輸入您想查詢的所有關鍵字，輸入完成後請輸入\"結束\"'))
    elif(text == "結束"):
        flag[event.source.user_id] = 0
        with open("keywords.json", "r") as file:
            json_data = json.load(file)
        
        json_data[event.source.user_id] = temp_users_keywords[event.source.user_id]

        with open("keywords.json", 'w') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)

        del temp_users_keywords[event.source.user_id]
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='設定完成，您重新設定的關鍵字為: ' + str(keywords)))
    else:
        if(flag[event.source.user_id]==1):
            temp_users_keywords[event.source.user_id].append(text)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='輸入完成後請輸入\"結束\"'))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='請輸入\"重新設定\"以重新設定您想要的關鍵字'))
        


def create_app():
    app = Flask(__name__)
    app.debug=True
    logger.warning("Creating app")
    app.add_url_rule('/', 'index', lambda: 'ALIVE')

    @app.route("/callback", methods=['POST'])
    def callback():
        # get X-Line-Signature header value
        signature = request.headers['X-Line-Signature']

        # get request body as text
        body = request.get_data(as_text=True)
        app.logger.info("Request body: " + body)

        # handle webhook body
        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            print("Invalid signature. Please check your channel access token/channel secret.")
            abort(400)

        return 'OK'

    chrome_driver = ChromeDriver(headless=True)

    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.add_job(id='run_scraper', func=run_scraper, args=[chrome_driver, line_bot_api], trigger='interval', seconds=30)
    scheduler.start()
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0')
