
from google.oauth2 import service_account
from googleapiclient.discovery import build
from os import path
import pickle

def getDB():
    db = {}
    if path.isfile('/home/container/db') and (path.getsize('/home/container/db') > 0):
        dbfile = open('/home/container/db', 'rb')
        db = pickle.load(dbfile)
        dbfile.close()
    return db
    
def updateDB(db) :
    dbfile = open('db','wb')
    pickle.dump(db, dbfile)
    dbfile.close()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'discord-bot-dipc.json'


class stat_dumper:
    def __init__(self,
                 scopes=['https://www.googleapis.com/auth/spreadsheets']):
        self.scopes = scopes
        self.range = "Sheet2!A1:O2"

    def connect(self, spreadsheetId):
        self.spreadsheetId = spreadsheetId

        creds = service_account.Credentials.from_service_account_file(
            'img/discord-bot-dipc.json', scopes=self.scopes)

        service = build('sheets', 'v4', credentials=creds, static_discovery=False)
        self.sheets = service.spreadsheets()

    def update(self):
        db = getDB()
        self.extracted = self. sheets.values().get(spreadsheetId=self.spreadsheetId,
                                                   range=self.range,
                                                   majorDimension="COLUMNS"
                                                   ).execute()
        """result = self.sheets.values().update(spreadsheetId=self.spreadsheetId,
                                             range=self.range,
                                             valueInputOption="USER_ENTERED",
                                             body={
                                                 'values': [['1', '2'],
                                                            ['3', '4']]
                                             }).execute()"""
      
        if "values" in self.extracted.keys():
        	print(self.extracted["values"])
        if db["next_race_name"] not in self.extracted["values"][0]:
            values = [db["next_race_name"]]
            values.extend(db["q_result"])
            values.extend(db["r_result"])

            q_pred = db["q_predictions"]
            r_pred = db["r_predictions"]
            week = db["weekend"]
            points = db["points"]
            for u in q_pred:
                values.extend(q_pred[u])
                values.extend(r_pred[u])
                values.append(week[u][0])
                values.append(points[u])

            print(values)
            appended = self.sheets.values().append(spreadsheetId=self.spreadsheetId,
                                                   range="Sheet2!A1:AZ10",
                                                   valueInputOption="USER_ENTERED",
                                                   body={"values":[values]
                                                   }).execute()
            print(str(appended))