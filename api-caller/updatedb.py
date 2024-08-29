from os import path

import pickle

    
def getDB():
    db = {}
    if path.isfile('/home/container/db'):
        dbfile = open('db', 'rb')
        db = pickle.load(dbfile)
        dbfile.close()
    return db

def updateDB(db) :
    dbfile = open('/home/container/db','wb')
    pickle.dump(db, dbfile)
    dbfile.close()
    
if __name__ == "__main__":
    db = getDB()
    print(db)
    db["round"]=14
    updateDB(db)
    db=getDB()
    print(db)