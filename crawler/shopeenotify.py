from crawler import crawl
from webDriver import ChromeDriver
import requests
import  io 

url = 'https://notify-api.line.me/api/notify'
token = 'l2ixxn1wear77gmLwK8WLKWQZrph1ySNoaCkGcG0jQd'   ###授權碼
headers = {
    'Authorization': 'Bearer ' + token    # 設定 LINE Notify 權杖
}

# image = open('./108703043.png', 'rb')    # 以二進位方式開啟圖片
# imageFile = {'imageFile' : image}   # 設定圖片資訊
#【test】

def job():
    driver = ChromeDriver().driver
    data=dict()
    data=crawl(driver)
    underlinelist={"減資","庫藏股","轉換","澄清","本公司召開","公司債","增資"}
    for key in data.keys():
        for word in underlinelist:
            if word in key:
                underline="【"+word+"】"
                cmpnynum="("+key[0:4]+")"
                count=0
                cmpnyname=''
                announcement=''
                for i in range(0,len(key)):
                    if key[i] ==' ' and count!=4:
                        count+=1
                    if count==1:
                            cmpnyname+=key[i]    
                    elif count == 4:
                        announcement+=key[i]
                message=underline+"\n"+cmpnynum+cmpnyname+"-重大消息"+"\n"+announcement
            #    image = open('./screen.png', 'rb')
                # ii=io.BytesIO(data[key]['png'])
                image = data[key]['png']
                imageFile = {'imageFile' : image}   # 設定圖片資訊
                data = {
                'message':message ,     # 設定 LINE Notify message ( 不可少 )
                }
                data = requests.post(url, headers=headers, data=data, files=imageFile)   # 發送 LINE Notify