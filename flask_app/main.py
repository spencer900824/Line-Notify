from flask import Flask, request, abort, send_file
from run_scraper import run_scraper
from flask_apscheduler.scheduler import APScheduler
from driver.web_driver import ChromeDriver
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import json
import logging

import os
import threading

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


temp_users_keywords_lock = threading.Lock()
flag_lock = threading.Lock()

keywords_lock = threading.Lock()

message_lock = threading.Lock()
message_dict = {}


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global flag, temp_users_keywords
    text = event.message.text

    if event.source.user_id not in flag:
        flag_lock.acquire()
        try:
            flag[event.source.user_id] = 0
        finally:
            flag_lock.release()

    if(text == "重新設定"):
        flag_lock.acquire()
        try:
            flag[event.source.user_id] = 1
        finally:
            flag_lock.release()
        
        temp_users_keywords_lock.acquire()
        try:
            temp_users_keywords[event.source.user_id] = []
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='請輸入您想查詢的所有關鍵字，輸入完成後請輸入\"結束\"'))
        finally:
            temp_users_keywords_lock.release()
        
    elif(text == "結束"):
        flag_lock.acquire()
        try:
            flag[event.source.user_id] = 0
        finally:
            flag_lock.release()


        keywords_lock.acquire()
        try:
            try:
        # Try to open the file in write mode with "x" flag
                with open("keywords.json", 'x') as file:
                    # File does not exist, created successfully
                    json.dump({}, file, ensure_ascii=False, indent=4)
                    print("File created successfully.")

            except FileExistsError:
                # File already exists
                print("File already exists.")


            with open("keywords.json", "r") as file:
                json_data = json.load(file)
            
            json_data[event.source.user_id] = temp_users_keywords[event.source.user_id]

            with open("keywords.json", 'w') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4)
        finally:
            keywords_lock.release()

        
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='設定完成，您重新設定的關鍵字為: ' + str(temp_users_keywords[event.source.user_id])))
        
        temp_users_keywords_lock.acquire()
        try:
            del temp_users_keywords[event.source.user_id]
        finally:
            temp_users_keywords_lock.release()
            
    else:
        if(flag[event.source.user_id]==1):
            temp_users_keywords_lock.acquire()
            try:
                temp_users_keywords[event.source.user_id].append(text)
            finally:
                temp_users_keywords_lock.release()
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
    
    @app.route('/hello')
    def hello():
        return 'OK'
    
    @app.route('/image/<image_name>')
    def get_image(image_name):
        image_path = image_name
        if os.path.isfile(image_path):
            return send_file("/app/"+image_path, mimetype='image/x-png')
        else:
            return 'Image not found', 404

    chrome_driver = ChromeDriver(headless=True)

    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.add_job(id='run_scraper', func=run_scraper, args=[chrome_driver, line_bot_api, keywords_lock, message_lock, message_dict], trigger='interval', seconds=30)
    scheduler.start()
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0')
