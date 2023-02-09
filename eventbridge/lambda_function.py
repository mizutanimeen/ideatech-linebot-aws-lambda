import json
import urllib.request
import os
import boto3

ID_TABLE_NAME = "linebot-test"
ID_TABLE_COLUMN_1 = "line-id"
ID_TABLE_COLUMN_2 = "student-id"
ID_TABLE_COLUMN_3 = "student-pass"

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(ID_TABLE_NAME)
    response = table.scan()
    for response_items in response['Items']:
        url = 'https://api.line.me/v2/bot/message/push'
        headers = {
            'Content-Type': 'application/json',
            #lambdaにLINE_CHANNEL_ACCESS_TOKENで環境変数を追加が必要
            'Authorization': 'Bearer ' + os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
        }
        body = {
            'to':  response_items[ID_TABLE_COLUMN_1],
            'messages': [
                { 
                    "type": "text",
                    "text":  "テストです",
                }
            ]
        }
        req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), method='POST', headers=headers)
        urllib.request.urlopen(req)
        print(response_items[ID_TABLE_COLUMN_2])
        print(response_items[ID_TABLE_COLUMN_3])
    return 