import copy
from os import path
from os import environ
import pickle
def getDB():
    db = {}
    if path.isfile(environ.get("PROJ_HOME") + '/db') and (path.getsize(environ.get("PROJ_HOME") + '/db') > 0):
        dbfile = open(environ.get("PROJ_HOME") + '/db', 'rb')
        db = pickle.load(dbfile)
        dbfile.close()
        print("db found\n")
    return db
    
def updateDB(db) :
    if (path.getsize(environ.get("PROJ_HOME") + '/db') > 0):
        dbread = open(environ.get("PROJ_HOME") + '/db','rb')
        dbr = pickle.load(dbread)
        print(dbr)
        dbread.close()
        dbfile = open(environ.get("PROJ_HOME") + '/db','wb')
        pickle.dump(db, dbfile)
        dbfile.close()
        print("db updated\n")
        dbread = open(environ.get("PROJ_HOME") + '/db','rb')
        dbr = pickle.load(dbread)
        print(dbr)
        dbread.close()

def update_predictions(u, x, t):
    db = getDB()
    d = {}

    if t == 'r':
        if "r_predictions" not in db.keys():
            db["r_predictions"] = {str(u): [x[2], x[3], x[4]]}
        else:
            d = db["r_predictions"]
            d.update({str(u): [x[2], x[3], x[4]]})
            db["r_predictions"] = d
        updateDB(db)
        db = getDB()
        d = db["r_predictions"]
        return '✅Race prediction made by ' + str(u) + ': ' + '\t'.join(
            driver.upper() for driver in d[str(u)])

    if t == 'q':
        if "q_predictions" not in db.keys():
            db["q_predictions"] = {str(u): [x[2], x[3], x[4]]}
        else:
            d = db["q_predictions"]
            d.update({str(u): [x[2], x[3], x[4]]})
            db["q_predictions"] = d
        updateDB(db)
        db = getDB()
        d = db["q_predictions"]
        return '✅Grid prediction made by ' + str(u) + ': ' + '\t'.join(
            driver.upper() for driver in d[str(u)])
    
    updateDB(db)


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
    updateDB(db)


def update_points(x, y):
    db = getDB()
    p = {}
    dr = db["r_predictions"]
    dq = db["q_predictions"]
    db["r_result"] = x
    db["q_result"] = y

    if "points" not in db.keys():
        for pd in dr.keys():
            p.update({pd: 0})
    else:
        p = copy.deepcopy(db["points"])

    for us in dr.keys():
        if us not in p.keys():
            po = 0
        else:
            po = p[us]
        
        temp = 0
        for pos in range(3):
            if dr[us][pos] in x or dr[us][pos]+'👀' in x:
                temp = temp + 1
            if dr[us][pos] == x[pos] or dr[us][pos]+'👀' == x[pos]:
                temp = temp + 1
            if dq[us][pos] in y or dq[us][pos]+'👀' in y:
                temp = temp + 1
            if dq[us][pos] == y[pos] or dq[us][pos]+'👀' == y[pos]:
                temp = temp + 1
        
        p.update({us: po + temp})

    db["points"] = copy.deepcopy(p)
    print(1, db["points"])
    sort_points()
    print(3, db["points"])
    updateDB(db)


def sum(x):
    db = getDB()
    message = ""
    if x:
        if "q_result" in db.keys():
            r = db["q_result"]
            message = ' '.join(
                i.capitalize() for i in db["this_race"]
            ) + ' results:\n\nTop 3 on the grid:\n' + '\n'.join(
                ((str(r.index(driver) + 1) + ": " + driver.upper())
                 for driver in r)) + '\n'

        if "r_result" in db.keys():
            r = db["r_result"]
            message = message + '\nPodium finishers:\n' + '\n'.join(
                ((str(r.index(driver) + 1) + ": " + driver.upper())
                 for driver in r)) + '\n'

    if "q_predictions" in db.keys():
        d = db["q_predictions"]
        message = message + '\nLatest grid predictions:\n'
        for us in d.keys():
            l = us.split('#')
            message = message + l[0] + ': ' + '\t'.join(
                driver.upper() for driver in d[us]) + '\n'

    if "r_predictions" in db.keys():
        d = db["r_predictions"]
        message = message + '\nLatest race predictions:\n'
        for us in d.keys():
            l = us.split('#')
            message = message + l[0] + ': ' + '\t'.join(
                driver.upper() for driver in d[us]) + '\n'

    if "disp_points" in db.keys():
        p = copy.deepcopy(db["disp_points"])
        message = message + '\nPoints:\n'
        for us in p.keys():
            l = us.split('#')
            message = message + "#" + str(
                p[us][1]) + (" " if(p[us][1] == 1) else "") + p[us][3] + " " + l[0] + ': ' + str(p[us][0]) + "    " + p[us][2] + '\n'

    if x:
        if "next_race" in db.keys():
            message = message + '\n' + db["next_race"]

    return message


def reset():
    db = getDB()
    p = copy.deepcopy(db["points"])
    for us in p.keys():
        p[us] = 0
    db["points"] = p
    sort_points()
    return "Points = 💩 . Me = 😤➡🚽. You = 😎🤣"
    updateDB(db)


def this_race(x):
    db = getDB()
    i = x.index("the")
    j = x.index("prix")
    r = x.index("(round")
    db["this_race"] = x[i + 1:j + 1]
    db["round_current"] = int(x[r + 1].split('/')[0])
    updateDB(db)

def next_race(x):
    db = getDB()
    i = x.index("at")
    r = x.index("(Round")
    db["next_race_name"] = ' '.join( i for i in x[2:i])
    db["round_next"] = int(x[r + 1].split('/')[0])
    updateDB(db)


def celebrate(year):
    db = getDB()
    message = "\nI didn't calculate who took the crown in F1 (go HAM) but for DIPT (more important imo), here are the results-\n\n"

    p = copy.deepcopy(db["disp_points"])
    n = 1
    name = ""
    for us in p.keys():
        l = us.split('#')
        if n == 1:
            message = message + "🥇"
            name = us
        elif n == 2:
            message = message + "🥈"
        elif n == 3:
            message = message + "🥉"
        else:
            message = message + "      "
        message = message + " " + l[0] + ': ' + '\n'
        n = n + 1

    message = message + '\n' + "Congratulations " + db["mentions"][name] + " on winning The Danka Imli Predictions Championship! You are **THE "+ year +" CHAMPION**. And well played everyone else! \n\nCHAMPAGNE!!"
    return message
