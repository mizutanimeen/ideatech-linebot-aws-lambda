import re
from selenium import webdriver
from selenium.webdriver.common.by import By

import db
import util

def getAttendData(studentID,studentPass):
    #要望：IDとかパスワードが間違ってた時のエラー処理とか欲しい
    try:
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
                test += subject + "\n"
    except:
        return "データが取得できませんでした。" # エラー文増やす。ログインできたか、運用時間外か、などでtry小分けする
    return test

def ShowCommand(event,lineMessage):
    if re.fullmatch(r'show', lineMessage):#データベースからデータを取ってきて出席データを返す
        lineID = util.GetLineIDByMessage(event)
        studentID,studentPass = db.GetIDAndPassByLineID(lineID)
    elif re.fullmatch(r'show::\d{9}::.+', lineMessage):#LineMessageからデータを抽出して出席データを返す
        studentID,studentPass = util.ParseLineMessageIntoIDAndPass(lineMessage)
    attendData = getAttendData(studentID,studentPass)
    util.SendMessageToLine(event,attendData)
    return

