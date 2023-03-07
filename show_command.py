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
        
        tMsg = ""

        tGradeTables = driver.find_elements(By.CLASS_NAME,'ssekitable')
        for tTable in tGradeTables:
            tDayOfWeek = tTable.find_element(By.XPATH,".//tbody/tr/th")
            tMsg += f"-----{tDayOfWeek.text}-----\n" #曜日
            tLessons = tTable.find_elements(By.XPATH,".//tbody/tr")
            for i in range(len(tLessons)):
                if i < 3:
                    continue
                tItems = tLessons[i].find_elements(By.CLASS_NAME,"item")
                for j in range(len(tItems)):
                    if j == 0:
                        tMsg += f"{tItems[j].text}: "
                    elif j == 1:
                        tMsg += f"{tItems[j].text}\n"
                    elif j == 2:
                        tMsg += f"講義回数: {tItems[j].text}\n"
                    elif j == 3:
                        tMsg += f"出席回数: {tItems[j].text}\n"
                    elif j == 4:
                        tMsg += f"出席率: {tItems[j].text}\n"
                        tMsg += "-----------\n"
                    else:
                        break
    except:
        return "データが取得できませんでした。" # エラー文増やす。ログインできたか、運用時間外か、などでtry小分けする
    return tMsg

def ShowCommand(event,lineMessage):
    if re.fullmatch(r'show', lineMessage):#データベースからデータを取ってきて出席データを返す
        lineID = util.GetLineIDByMessage(event)
        studentID,studentPass = db.GetIDAndPassByLineID(lineID)
    elif re.fullmatch(r'show::\d{9}::.+', lineMessage):#LineMessageからデータを抽出して出席データを返す
        studentID,studentPass = util.ParseLineMessageIntoIDAndPass(lineMessage)
    attendData = getAttendData(studentID,studentPass)
    util.SendMessageToLine(event,attendData)
    return

