from os import path
from os import environ
import copy
import random
import pickle

def getDB():
    db = {}
    if path.isfile(environ.get("PROJ_HOME") + '/db'):
        dbfile = open('db', 'rb')
        db = pickle.load(dbfile)
        dbfile.close()
    return db
    
def updateDB(db) :
    dbfile = open(environ.get("PROJ_HOME") + '/db','wb')
    pickle.dump(db, dbfile)
    dbfile.close()

def update_points(x, y):
    db = getDB()
    p = {}
    cb = {}
    dr = db["r_predictions"]
    dq = db["q_predictions"]
    db["r_result"] = x
    db["q_result"] = y

    if "points" not in db.keys():
        for pd in dr.keys():
            p.update({pd: 0})
    else:
        p = copy.deepcopy(db["points"])

    if "countback" not in db.keys():
        for pd in dr.keys():
            cb.update({pd: [0,0,0]})
    else:
        cb = copy.deepcopy(db["countback"])

    for us in dr.keys():
        if us not in cb.keys():
            cb.update({us: [0,0,0]})
          
        if us not in p.keys():
            po = 0
        else:
            po = p[us]
        for pos in range(3):
            if dr[us][pos] in x or dr[us][pos]+'👀' in x:
                po = po + 1
            if dr[us][pos] == x[pos] or dr[us][pos]+'👀' == x[pos]:
                po = po + 1
                cb[us][pos] = cb[us][pos] + 1  
            if dq[us][pos] in y or dq[us][pos]+'👀' in y:
                po = po + 1
            if dq[us][pos] == y[pos] or dq[us][pos]+'👀' == y[pos]:
                po = po + 1
        p.update({us: po})
    db["points"] = copy.deepcopy(p)
    db["countback"] = copy.deepcopy(cb)
    print(1,db["points"],db["countback"])
    sort_points()
    updateDB()

def lead_by_countback(x,y):
    db = getDB()
    cb = copy.deepcopy(db["countback"])
    for p in range(3):
        if cb[x][p] > cb[y][p]:
            return x
        elif cb[y][p] > cb[x][p]:
            return y
    return [x,y][random.randint(0,1)]

def sort_points():
    db = getDB()
    d = {}
    p = copy.deepcopy(db["points"])
    if "disp_points" not in db.keys():
        for u in p.keys():
            d.update({u: [p[u], 1, "lead", "↔️⬇️⬆️"]})
        db["disp_points"] = copy.deepcopy(d)

    dt = {}
    dp = copy.deepcopy(db["disp_points"])
    pos = 1
    pre = 0
    for m in range(len(p)):
        maxp = -1
        n = ""
        for u in p.keys():
            if p[u] > maxp and u not in dt.keys():
                maxp = p[u]
                n = u
            elif p[u] == maxp and u not in dt.keys():
                n = lead_by_countback(n, u)
        dt.update({n: [maxp, pos]})
        if pos == 1:
            dt[n].append("Lead")
        else:
            dt[n].append(str(maxp - pre))
        pre = maxp
        pos = pos + 1

    for u in dt.keys():
        if u not in dp.keys():
            dt[u].append("↔️")
        elif dp[u][1] > dt[u][1]:
            dt[u].append("⬆️")
        elif dp[u][1] < dt[u][1]:
            dt[u].append("⬇️")
        else:
            dt[u].append("↔️")
    db["disp_points"] = copy.deepcopy(dt)
    updateDB()

def reset():
    db = getDB()
    p = db["points"]
    if "countback" in db.keys():
        c = db["countback"]
    else:
        c = {}
    for us in p.keys():
        p[us] = 0
        c[us] = [0,0,0]
    db["points"] = p
    db["countback"] = c
    sort_points()
    return "Points = 💩 . Me = 😤➡🚽. You = 😎🤣"
    updateDB()

