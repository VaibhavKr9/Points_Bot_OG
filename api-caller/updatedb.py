from os import environ
from os import path

import pickle

    
def getDB(dbPath):
    db = {}
    if path.isfile(dbPath):
        dbfile = open(dbPath, 'rb')
        db = pickle.load(dbfile)
        dbfile.close()
    return db

def updateDB(db) :
    dbfile = open('/home/container/db','wb')
    pickle.dump(db, dbfile)
    dbfile.close()
    
if __name__ == "__main__":
    #dbpath = path.join(path.dirname(__file__), "/db")
    db = getDB(environ.get("PROJ_HOME") + "/api-caller/db")
    print(db)
    """ db["round"]=16
    updateDB(db)
    db=getDB()
    print(db) """