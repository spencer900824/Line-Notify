# LineNotify

# Init (only do this if using AWS ec2)
1. Create a AWS EC2 - "Amazon Linux2 AMI" instance
2. 開好 port 5001 (很重要)
2. copy "init_on_ec2.sh" to the instance created in step 1
3. input cmd:  ". ./init_on_ec2.sh"

# Run server
1. git clone https://github.com/spencer900824/Line-Notify.git (if run on EC2, skip this step)
2. set config.json
3. 依序輸入指令: 
    3-1.
    ```
    sh ./Line-Notify/build.sh
    ```
    3-2.(只有第一次要執行)
    ```
    sh ./Line-Notify/init_container.sh
    ```
    3-3.(產生暫時url)
    ```
    sh ./Line-Notify/generate_url.sh
    ```
    把產生的網址複製，把messaging api 的webhook 的 '/callback'前面的字串換成此網址，'/callback'要留著，並按verify，success就代表成功了

    <br/>
    3-4.若要關掉應用程式
    先ctr C 把url 關掉，然後輸入

    ```
    sh ./Line-Notify/stop_container.sh
    ```
4. 3是第一次才在做 若已經跑過3 之後想重啟服務只要執行以下<br/>

    4-1.開啟服務
    ```
    sh ./Line-Notify/start_container.sh
    ```
    <br/>
    4-2 做3-3 <br/>

    4-3 關掉應用程式，做3-4

    


# Check alive
1. http://[instance_public_ip]:5001

# dev
1. py3 -m flask -A flask_app/main run -p 5001
