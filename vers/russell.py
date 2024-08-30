
import copy

from vers import bottas22 as b
from os import path
from os import environ
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

def sort_points():
    db = getDB()
    d = {}
    p = copy.deepcopy(db["points"])
    if "disp_points" not in db.keys():
        for u in p.keys():
            d.update({u: [p[u], 1, "0", "↔️","(0,0,0)"]})
        db["disp_points"] = copy.deepcopy(d)

    dt = {}
    dp = copy.deepcopy(db["disp_points"])
    cb = copy.deepcopy(db["countback"])
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
                n = b.lead_by_countback(n, u)
        dt.update({n: [maxp, pos]})
        if pos == 1:
            dt[n].append("")
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


    for u in dt.keys():
        if u not in cb.keys():
            dt[u].append("(0,0,0)")
        else:
            s = "(" + ','.join(str(num) for num in cb[u]) + ")"
            dt[u].append(s)
        
    db["disp_points"] = copy.deepcopy(dt)
    updateDB(db)

def sort_weekend():
    db = getDB()
    d = {}
    p = copy.deepcopy(db["weekend"])
    if "disp_week" not in db.keys():
        for u in p.keys():
            d.update({u: [p[u], 1,"(0,0,0)"]})
        db["disp_week"] = copy.deepcopy(d)

    dt = {}
    pos = 1
    for m in range(len(p)):
        maxp = -1
        n = []
        for u in p.keys():
            if p[u][0] > maxp and u not in dt.keys():
                maxp = p[u][0]
                n.clear()
                n.append(u)
            elif p[u][0] == maxp and u not in dt.keys():
                for po in range(3):
                    if p[u][1][po] > p[n[0]][1][po]:
                        n.clear()
                        n.append(u)
                        break
                    elif p[u][1][po] < p[n[0]][1][po]:
                        break
                    elif po == 2:
                        n.append(u)
        for u in n:
            dt.update({u: [maxp, pos]})
            dt[u].append("(" + ','.join((("+" if (cp > 0) else "") + str(cp)) for cp in p[u][1]) + ")")
        pos = pos + 1
        
    db["disp_week"] = copy.deepcopy(dt)
    updateDB(db)

def update_points(x, y):
    db = getDB()
    p = {}
    cb = {}
    wp = {}
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
        db["countback"] = copy.deepcopy(cb)
    else:
        cb = copy.deepcopy(db["countback"])

    for us in dr.keys():
        if us not in cb.keys():
            cb.update({us: [0,0,0]})
        wp.update({us:[0, [0,0,0]]})
          
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
        wp[us][0] = po - p[us]
        p.update({us: po})

    for us in wp.keys():
        for pos in range(3):
            wp[us][1][pos] = cb[us][pos] - db["countback"][us][pos]
    
    db["points"] = copy.deepcopy(p)
    db["countback"] = copy.deepcopy(cb)
    db["weekend"] = copy.deepcopy(wp)
    print(1,db["points"],db["countback"], db["weekend"])
    updateDB(db)
    sort_weekend()
    sort_points()
    

def sum():
    db = getDB()
    message = ""

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

    if "disp_week" in db.keys():
        w = db["disp_week"]
        message += "\nWeekend Points:\n"
        message += "`Pos|    Player        |Pts   |Countback\n"
        for us in w.keys():
            l = us.split("#")
            message += " " + str(w[us][1]) + " | "
            message += l[0] + " ".join('' for i in range(18-len(l[0]))) + '|'
            message += (" " if (w[us][0] < 10) else "") + "+" + str(w[us][0]) + '   |'
            message += w[us][2] +'\n'
        message += "`\nThe Weekend Winner(s) 🏅: "
        for us in w.keys():
            if w[us][1] == 1:
                message += db["mentions"][us]
        message += '\n'
      
    if "disp_points" in db.keys():
        p = copy.deepcopy(db["disp_points"])
        message = message + '\nPoints Table:\n'
        message = message + '`Pos|    Player       |Pts.  |Int. |Countback\n'
        for us in p.keys():
            l = us.split('#')
            message += str(p[us][3]) +' '
            message += str(p[us][1]) + "| "
            message += l[0] + ' '.join('' for i in range(17-len(l[0]))) + "|"
            message += (" " if (p[us][0] < 100) else "") + (" " if (p[us][0] < 10) else "") +str(p[us][0]) + "   |" 
            message += p[us][2] + ' '.join('' for i in range(6-len(p[us][2])))+ "|"
            try:
                message += p[us][4] + '\n'
            except:
                message+= '\n'
        message += "`"

    return message