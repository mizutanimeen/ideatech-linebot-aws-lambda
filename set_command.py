import util
import db

def SetCommand(event,lineMessage):
    lineID = util.GetLineIDByMessage(event)    
    studentID,studentPass = util.ParseLineMessageIntoIDAndPass(lineMessage)
    db.PutDataIntoIDTable(lineID,studentID,studentPass)
    util.SendMessageToLine(event,"dynamodbにLineIDと学籍番号、パスワードを保存")
    return