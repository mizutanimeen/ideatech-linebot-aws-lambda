import selenium
from selenium import webdriver
import json
import urllib.request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome import service
import re
import boto3

LINE_CHANNEL_ACCESS_TOKEN = '2M07AZXtvOywMJmsEQDoHfJymesBFqnt6ERnHzCW41F2vp/Aj4A6YP26vEEhiMGUd0s31BttYvrUi+iaGyXYAyW2ojy0ilDZS13Rbbi0jXYW4EO3k9W94UoBIgjV4N7yhVxhQgRflEWiZuC1NVJCXQdB04t89/1O/w1cDnyilFU='
TABLE_NAME = "linebot-test"
TABLE_COLUMN_1 = "line-id"
TABLE_COLUMN_2 = "student-id"
TABLE_COLUMN_3 = "student-pass"
dynamodb = boto3.resource('dynamodb')

def getAttendanceData(studentID,studentPass):
    options = webdriver.ChromeOptions()
    # headless-chromiumのパスを指定
    options.binary_location = "/opt/headless/headless-chromium"
    options.add_argument("--headless")
    options.add_argument('--single-process')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(
        # chromedriverのパスを指定
        executable_path="/opt/headless/chromedriver",
        options=options
    )
    driver.implicitly_wait(10)
    driver.get('https://rpportal.meijo-u.ac.jp/Portal/index.do;jsessionid=2612E26253777FDFCBE907DFC46488E8')
    original_window = driver.current_window_handle
    gakuseki_box = driver.find_element(By.NAME,"callback_0")
    gakuseki_box.send_keys(studentID)
    pass_box = driver.find_element(By.NAME,"callback_1")
    pass_box.send_keys(studentPass)
    login = driver.find_element(By.NAME,"callback_2")
    login.click()

    gakumu = driver.find_elements(By.XPATH,'//nav[@class="templatemo-left-nav sp-none"]/ul/li/a')
    gakumu[1].click()

    for window_handle in driver.window_handles:
        if window_handle != original_window:
            driver.switch_to.window(window_handle)
            break
    attend0 = driver.find_elements(By.XPATH,'//div[@id="top_menu"]/ul/li/a')
    attend0[5].click()
    
    attend1 = driver.find_elements(By.XPATH,'//div[@id="sideMenuMiddle"]/ul/li[@class="item"]/a')
    attend1[0].click()
    
    rate = driver.find_elements(By.XPATH,'//table[@style="margin-top:-40px"]/tbody/tr/td/div/table[@class="ssekitable"]/tbody/tr/td[@class="item"]')
    
    test = ""

    for s in rate:
        subject = s.text
        if subject!="未" and subject!="-" and subject!="出" and subject!="欠"and subject!="遅" and subject!="":
            print(subject)
            test += subject
    return test

def sendMessageToLine(event,aMessage):
    for message_event in json.loads(event['body'])['events']:
        url = 'https://api.line.me/v2/bot/message/reply'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + LINE_CHANNEL_ACCESS_TOKEN
        }
        body = {
            'replyToken': message_event['replyToken'],
            'messages': [
                { 
                    "type": "text",
                    "text": aMessage,
                }
            ]
        }
        req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), method='POST', headers=headers)
        urllib.request.urlopen(req)

def showCommand(event,lineMessage):
    messageList = re.findall(r'[^::]+', lineMessage)
    studentID = messageList[1]
    studentPass = messageList[2]
    test = getAttendanceData(studentID,studentPass)
    sendMessageToLine(event,studentID + studentPass + test)

def setCommand(event,lineMessage):
    try: #userIDは常にあるのかわからないので配列からデータをとるときLineIDが空白の時で二重でエラーチェックしてる。片方で良ければ片方消す
        lineID = json.loads(event['body'])['events'][0]['source']['userId']
    except:
        sendMessageToLine(event,"エラー：lineIDが取得できませんでした。")
        exit(1)
    if lineID == "":
        sendMessageToLine(event,"エラー：lineIDが取得できませんでした。")
        exit(1)
    messageList = re.findall(r'[^::]+', lineMessage)
    studentID = messageList[1]
    studentPass = messageList[2]
    table = dynamodb.Table(TABLE_NAME)
    table.put_item(
        Item={
            TABLE_COLUMN_1:lineID,
            TABLE_COLUMN_2:studentID,
            TABLE_COLUMN_3:studentPass
        }
    )
    return

def lambda_handler(event, context):
    lineMessage = json.loads(event['body'])['events'][0]['message']['text']
    if re.fullmatch(r'show::\d{9}::.+', lineMessage):
        showCommand(event,lineMessage)
    elif re.fullmatch(r'set::\d{9}::.+', lineMessage):
        setCommand(event,lineMessage)
        sendMessageToLine(event,"dynamodbにLineIDと学籍番号、パスワードを保存")
    else:#エラー
        sendMessageToLine(event,"存在しないコマンドです。")
    
    return 
#lineに返信できるのは１メッセージにつき５メッセージまで
# -- 'replyToken': message_event['replyToken'],が１つにつき５回までしか使えない
#dynamodb に lineid id pass 一緒に保存するコマンドを作る
#eventbridge とかを使って定期実行するようにする。
#linebotにリッチメニューをつくる


#カードリーダーじゃない授業の出席を記録してくれるやつ
# - #カードリーダーじゃない授業の登録
# -- #eventbridge とかを使って定期実行するようにする。ー登録した授業の時間に確認してくれる質問を配信する。
# - dynamodbに質問の回答を記録する

#エラー処理が全体的に必要