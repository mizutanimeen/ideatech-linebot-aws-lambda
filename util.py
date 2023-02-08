import re
import json
import urllib.request

LINE_CHANNEL_ACCESS_TOKEN = 

def GetLineIDByMessage(event):
    try: #userIDは常にあるのかわからないので配列からデータをとるときuserIDの配列自体存在しているか、LineIDが空白の時で二重でエラーチェックしてる。片方で良ければ片方消す
        lineID = json.loads(event['body'])['events'][0]['source']['userId'] # [0]決め打ちよくない？[1]はありえる？
    except:
        SendMessageToLine(event,"エラー：lineIDが取得できませんでした。")
        exit(1)
    if lineID == "":
        SendMessageToLine(event,"エラー：lineIDが取得できませんでした。")
        exit(1)
    return lineID

#lineMessage = "command::ID::Pass" -> return "ID", "Pass"
def ParseLineMessageIntoIDAndPass(lineMessage):
    messageList = re.findall(r'[^::]+', lineMessage)
    studentID = messageList[1]
    studentPass = messageList[2]
    return studentID,studentPass

def SendMessageToLine(event,aMessage):
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
    return

