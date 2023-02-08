import boto3

#ID_TABLEはLineID,学生番号,パスワードを保存しているテーブル
ID_TABLE_NAME = "linebot-test"
ID_TABLE_COLUMN_1 = "line-id"
ID_TABLE_COLUMN_2 = "student-id"
ID_TABLE_COLUMN_3 = "student-pass"
#dynamodbにはlambdaの設定＞アクセス権限＞実行ロール＞ロール名にdynamodbの権限をつけなければならない
dynamodb = boto3.resource('dynamodb')

def GetIDAndPassByLineID(lineID):
    table = dynamodb.Table(ID_TABLE_NAME)
    response = table.get_item( Key={ ID_TABLE_COLUMN_1: lineID } )
    studentID = response["Item"][ID_TABLE_COLUMN_2]
    studentPass = response["Item"][ID_TABLE_COLUMN_3]
    return studentID,studentPass

def PutDataIntoIDTable(lineID,studentID,studentPass):
    table = dynamodb.Table(ID_TABLE_NAME)
    table.put_item(
        Item={
            ID_TABLE_COLUMN_1:lineID,
            ID_TABLE_COLUMN_2:studentID,
            ID_TABLE_COLUMN_3:studentPass
        }
    )