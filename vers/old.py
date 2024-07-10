from os import path
import pickle

def getDB():
    db = {}
    if path.isfile('/home/container/db'):
        dbfile = open('db', 'rb')
        db = pickle.load(dbfile)
        dbfile.close()
    return db
    
def updateDB() :
    dbfile = open('db','wb')
    pickle.dump(db, dbfile)
    dbfile.close()


def update_predictions(u, x):
    db = getDB()
    d = {}
    if "predictions" not in db.keys():
        db["predictions"] = {str(u): [x[1], x[2], x[3]]}
    else:
        d = db["predictions"]
        d.update({str(u): [x[1], x[2], x[3]]})
        db["predictions"] = d
    return 'Prediction made by ' + str(u) + ': ' + '\t'.join(
        driver.upper() for driver in d[str(u)])


def update_points(x):
    db = getDB()
    p = {}
    d = db["predictions"]
    db["result"] = x

    if "points" not in db.keys():
        for pd in d.keys():
            p.update({pd: 0})
    else:
        p = db["points"]

    for us in d.keys():
        if us not in p.keys():
            po = 0
        else:
            po = p[us]
        for pos in range(3):
            if d[us][pos] in x:
                po = po + 1
            if d[us][pos] == x[pos]:
                po = po + 1
        p.update({us: po})
    db["points"] = p


def sum():
    db = getDB()
    message = ''
    if "result" in db.keys():
        r = db["result"]
        message = 'Latest result: ' + '\t'.join(driver.upper()
                                                for driver in r) + '\n'

    if "predictions" in db.keys():
        d = db["predictions"]
        message = message + '\nLatest predictions:\n'
        for us in d.keys():
            message = message + us + ': ' + '\t'.join(
                driver.upper() for driver in d[us]) + '\n'

    if "points" in db.keys():
        p = db["points"]
        message = message + '\nPoints:\n'
        for us in p.keys():
            message = message + us + ': ' + str(p[us]) + '\n'

    return message


def update_user(us, po):
    db = getDB()
    if "points" not in db.keys():
        p = {us: po}
        db["points"] = p
    else:
        p = db["points"]
        p.update({us: int(po)})
    db["points"] = p
    return us + ' points updated to ' + po


def reset():
    db = getDB()
    p = db["points"]
    for us in p.keys():
        p[us] = 0
    db["points"] = p
    return "All users' points set to 0"