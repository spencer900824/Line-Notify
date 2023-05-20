from selenium.webdriver.common.by import By
import json
import time
import requests
import logging
import base64
import os
import logging

logger = logging.getLogger()

def crawl_mops(driver):
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

    try:
        with open("keywords.json", 'r') as f:
            targets = json.loads(f.read())
    except Exception as e:
        targets = []

    logger.warning(f"keywords: {targets}")
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
   
    for key, script in newEvents.items():

        stock_id, cmpnyname, date, time_, = key.split(' ')[:4]
        date = date.replace('/', '-')
        announcement = ''.join(key.split(' ')[4:])
        
        script = script.replace('openWindow','openWindowAction').replace('this.form', 'document.fm_t05sr01_1') # magic method
        #logger.warning(script)
        driver.execute_script(script)
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(1)
        # set window to fit table
        try:
            bottom = driver.find_element(By.XPATH, '/html/body/table[3]/tbody/tr/td/b')
            bottomLocation = bottom.location['y']
            if bottomLocation < 800:
                bottomLocation = 800
            driver.set_window_size(driver.get_window_size()['width'], bottomLocation)
        except:
            pass
        # save newData
        png_file = f"{png_dir}/{stock_id}-{date}-{time_}.png"
        img = driver.get_screenshot_as_base64()
        with open(png_file, 'wb') as f:
            f.write(base64.b64decode(img))
        # logger.error(f"Save {png_file}: {driver.save_screenshot(png_file)}")
        driver.close()
        driver.switch_to.window(baseWindow)
        ####判斷字詞發送notify
        for word in targets:
            if word in key:
                history.update({key:script})
                target_word = f"[{word}]"
                message = f"{target_word}:\n{cmpnyname} {stock_id}\n{announcement}\n{date} {time_}"
                try:
                    image = open(png_file, 'rb')
                except:
                    image = None
                # image = io.BytesIO(newData[key]['png'])
                imageFile = {'imageFile' :image}   # 設定圖片資訊
                data = {
                'message':message ,     # 設定 LINE Notify message ( 不可少 )
                }
                data = requests.post(urlline, headers=headers, data=data, files=imageFile)   # 發送 LINE Notify
                logger.warning(f"Msg pushed:\n{message}")

    # 5. save history
    with open(history_file, "w") as f:
        json.dump(history, f ,ensure_ascii=False, indent=4)