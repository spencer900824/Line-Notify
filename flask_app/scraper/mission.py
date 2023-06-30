from selenium.webdriver.common.by import By
import json
import time
import requests
import logging
import base64
import os
import logging

import pyimgur
import boto3

import random

from linebot.models import ImageSendMessage, TextSendMessage

# def upload_image(imgpath, client_id = "42ec6a6d416cb1e"):
#     im = pyimgur.Imgur(client_id)
#     upload_image = im.upload_image(imgpath, title="Uploaded with PyImgur")
#     return upload_image.link

imgNum = 0

# def upload_image(file_path, bucket_name="linebot-notify-images"):
#     s3 = boto3.client( 's3')
    
#     # Generate a unique key for the file in S3
#     object_key = "onekey"
    
#     # Upload the file to S3 bucket
#     s3.upload_file(file_path, bucket_name, object_key)
    
#     # Generate the public URL for the uploaded file
#     public_url = f"https://{bucket_name}.s3.amazonaws.com/{object_key}"
    
#     return public_url

def wordInKey(word, key):
    allWords = word.split(' ')
    
    for word in allWords:
        if word not in key:
            return False
    
    return True


logger = logging.getLogger()

def crawl_mops(driver, line_bot_api, keywords_lock, message_lock, message_dict, image_table):
    logger.warning("Starting")
    urlline = 'https://notify-api.line.me/api/notify'
    with open('config.json','r',encoding='utf-8') as f:
        config = json.loads(f.read())
    token = config['token']
    headers = {
        'Authorization': 'Bearer ' + token    # 設定 LINE Notify 權杖
    }
    target_url = "https://mops.twse.com.tw/mops/web/t05sr01_1"
    history_dir = './history'
    history_file = history_dir + '/history.json'
    png_dir = history_dir + '/png'
    if not os.path.exists(png_dir):
        os.mkdir(png_dir)
    try:
        with open(history_file, "r") as f:
            history = json.loads(f.read())
            if type(history) != dict:
                history = {}
    except Exception as e:
        history = {}

    keywords_lock.acquire()

    try:
        with open("keywords.json", 'r') as f:
            users = json.loads(f.read())
    except Exception as e:
        users = {}

    finally:
        keywords_lock.release()

    logger.warning(f"keywords: {users}")
    # 1. goto url
    logger.warning("go to url")
    if driver.current_url == target_url:
        driver.refresh()
    else:
        driver.get(target_url)
    # 2. find new events
    logger.warning("getting new events")
    try:
        eventsTable = driver.find_element(By.XPATH, '//*[@id="table01"]/form[2]/table/tbody')
    except Exception as e:
        logger.warning("No events table found")
        return
    trs = eventsTable.find_elements(By.TAG_NAME, 'tr')
    newEvents = {}
    for tr in trs[1:]:
        try:
            tds = tr.find_elements(By.TAG_NAME, 'td')
            key = ''
            for td in tds[:-1]:
                key+=td.text
                key+=' '
            if key in history.keys(): # old events
                continue
            else: # new events
                newEvents[key] = tds[-1].find_element(By.TAG_NAME, 'input').get_attribute('onclick')
        except Exception as e:
            logger.warning(f"Error in 2 : {str(e)}")
    
    # 4. check target
    baseWindow = driver.window_handles[0]
    
    print(reversed(newEvents.items()))
    
    for key, script in reversed(newEvents.items()):
      
       
        stock_id, cmpnyname, date, time_, = key.split(' ')[:4]
        date = date.replace('/', '-')
        announcement = ''.join(key.split(' ')[4:])
        
        script = script.replace('openWindow','openWindowAction').replace('this.form', 'document.fm_t05sr01_1') # magic method
        #logger.warning(script)
        png_file = f"{stock_id}-{date}-{time_}.png"
        if png_file not in image_table:

            fetchImage = True

            try:
                driver.execute_script(script)
                driver.switch_to.window(driver.window_handles[-1])
                delay = random.randint(4,5)
                time.sleep(delay)
            except Exception as e:
                logger.error(e)
                fetchImage = False

            
            # set window to fit table
            try:
                bottom = driver.find_element(By.XPATH, '/html/body/table[3]/tbody/tr/td/b')
                bottomLocation = bottom.location['y']
                if bottomLocation < 800:
                    bottomLocation = 800
                driver.set_window_size(driver.get_window_size()['width'], bottomLocation)
            except:
                fetchImage = False
                
            # save newData
            
            img = driver.get_screenshot_as_base64()
            with open(png_file, 'wb') as f:
                f.write(base64.b64decode(img))
            # logger.error(f"Save {png_file}: {driver.save_screenshot(png_file)}")
            
            driver.close()
            driver.switch_to.window(baseWindow)
            if(fetchImage):
                image_table[png_file] = True

            # try:
            #     driver.execute_script(script)
            #     driver.switch_to.window(driver.window_handles[-1])
            #     delay = random.randint(4,5)
            #     time.sleep(delay)
            # # set window to fit table
            
            #     bottom = driver.find_element(By.XPATH, '/html/body/table[3]/tbody/tr/td/b')
            #     bottomLocation = bottom.location['y']
            #     if bottomLocation < 800:
            #         bottomLocation = 800
            #     driver.set_window_size(driver.get_window_size()['width'], bottomLocation)
            
            # # save newData
            #     png_file = f"{stock_id}-{date}-{time_}.png"
            #     img = driver.get_screenshot_as_base64()
            #     with open(png_file, 'wb') as f:
            #         f.write(base64.b64decode(img))
            #     # logger.error(f"Save {png_file}: {driver.save_screenshot(png_file)}")
                
            #     driver.close()
            #     driver.switch_to.window(baseWindow)
                
            #     image_table[png_file] = True
            # except Exception as e:
            #     logger.warning("warning to many request")
            #     logger.warning(str(e))
            
               

        else:
            logger.warning("skip image")
       
        #img_url = upload_image(png_file)
        ####判斷字詞發送notify
        for userId in list(users.keys()):
            logger.warning(userId)
            continue_flag = False
            message_lock.acquire()
            try:
                if(userId not in message_dict.keys()):
                    message_dict[userId] = []
                elif png_file in message_dict[userId]:
                    continue_flag = True
            finally:
                message_lock.release()
            if(continue_flag):
                continue

            for word in users[userId]:
                logger.warning(word)
                logger.warning(key)


                if wordInKey(word, key):

                    

                    logger.warning("word check")
                    #history.update({key:script})
                    target_word = f"[{word}]"
                    message = f"{target_word}:\n{cmpnyname} {stock_id}\n{announcement}\n{date} {time_}"
                    exist_image = True
                    # try:

                    #     image = open(png_file, 'rb')
                    # except:
                    #     logger.warning("image not exist")
                    #     exist_image = False
                    #     image = None
                    # image = io.BytesIO(newData[key]['png'])
                    # imageFile = {'imageFile' :image}   # 設定圖片資訊
                    
                    # if(exist_image == True):
                    #     logger.warning("upload_image")
                    #     img_url = upload_image(png_file)
                    #     logger.warning(f"url {img_url}")
                    #   data = {
                    #   'message':message ,     # 設定 LINE Notify message ( 不可少 )
                    #   }
                    img_url = "\n\nhttp://52.65.27.113:5001/image/"+png_file
                    line_bot_api.push_message(userId, TextSendMessage(text=message+img_url))
                    logger.warning("push message")
                    
                    logger.warning(img_url)
                    
                    #line_bot_api.push_message(userId, ImageSendMessage(original_content_url=img_url,preview_image_url=img_url))

                    # data = requests.post(urlline, headers=headers, data=data, files=imageFile)   # 發送 LINE Notify
                    logger.warning(f"Msg pushed:\n{message}")

                    message_lock.acquire()
                    try:
                        message_dict[userId].append(png_file)
                    finally:
                        message_lock.release()
                    break

    # 5. save history
    with open(history_file, "w") as f:
        json.dump(history, f ,ensure_ascii=False, indent=4)