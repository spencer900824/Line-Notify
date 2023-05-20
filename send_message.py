from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import json

app = Flask(__name__)
flag = 2 
keywords = []

with open('config.json','r',encoding='utf-8') as f:
    config = json.loads(f.read())

access_token = config['access_token']
secret = config['secret']

# Channel Access Token 和 Channel Secret
line_bot_api = LineBotApi(access_token)
handler = WebhookHandler(secret)

# 处理来自 Line 平台的 Webhook 讯息
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

@app.route("/postlist", methods=['POST'])
def postlist():
    return json.dumps(keywords)


# 处理收到的 Text Message 讯息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global flag, keywords
    text = event.message.text
    if(text == "重新設定"):
        keywords = []
        flag = 1
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='請輸入您想查詢的所有關鍵字，輸入完成後請輸入\"結束\"'))
    elif(text == "結束"):
        flag = 0
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='設定完成，您重新設定的關鍵字為: ' + str(keywords)))
    else:
        if(flag==1):
            keywords.append(text)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='輸入完成後請輸入\"結束\"'))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='請輸入\"重新設定\"以重新設定您想要的關鍵字'))
        
if __name__ == "__main__":
    app.run(debug=True)
