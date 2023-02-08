import json
import re

import show_command
import set_command
import util

def lambda_handler(event, context):
    for message_event in json.loads(event['body'])['events']:
        lineMessage = message_event['message']['text']
        if re.fullmatch(r'show|show::\d{9}::.+', lineMessage): #出席率に関係なく全ての科目の情報を返すコマンドとか作る？
            show_command.ShowCommand(event,lineMessage)
        elif re.fullmatch(r'set::\d{9}::.+', lineMessage):
            set_command.SetCommand(event,lineMessage)
        else:
            util.SendMessageToLine(event,"存在しないコマンドです。")
    return 

#エラー処理が全体的に必要
#exit(1)とかlineにメッセージを送信ってlambda_handlerの中だけで実行した方がわかりやすいかな？？現在はlambda_handler以外からもよんでいる