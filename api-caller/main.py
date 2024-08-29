import discord
import requests
import time
from datetime import timedelta
from datetime import datetime
from discord.ext import tasks
from dotenv import load_dotenv
from os import path
from os import environ as secret

import pickle

    
def getDB():
    db = {}
    if path.isfile('/home/container/api-caller/db'):
        dbfile = open('db', 'rb')
        db = pickle.load(dbfile)
        dbfile.close()
    return db

def updateDB(db) :
    dbfile = open('/home/container/api-caller/db','wb')
    pickle.dump(db, dbfile)
    dbfile.close()

intents = discord.Intents.all()
intents.members = True
c = discord.Client(intents = intents)
channel = []

def get_round():
    db = getDB()
    if not db["over"]:
        season = requests.get("http://ergast.com/api/f1/current.json").json()
        for r in season["MRData"]["RaceTable"]["Races"]:
            d = r["date"].split("-")
            t = r["time"].split(":")
            x = datetime(int(d[0]), int(d[1]), int(d[2]), int(t[0]), int(t[1]))
            try:
                d_q = r["Sprint"]["date"].split("-")
                db["sprint"] = True
            except:
                db["sprint"] = False
            finally:
              d_q = r["Qualifying"]["date"].split("-")
              t_q = r["Qualifying"]["time"].split(":")
            db["racetime"] = [
                int(d[0]),
                int(d[1]),
                int(d[2]),
                int(t[0]),
                int(t[1])
            ]
            db["qualitime"] = [
                int(d_q[0]),
                int(d_q[1]),
                int(d_q[2]),
                int(t_q[0]),
                int(t_q[1])
            ]
            db["round"] = int(r["round"])
            if datetime.now() < x:
                print(db["round"])
                x = x + timedelta(minutes=330)
                db["next_race"] = r["raceName"]
                db["year"] = int(season["MRData"]["RaceTable"]["season"])
                db["over"] = False
                updateDB(db)
                return "⏳Next race: " + r["raceName"] + " at " + r["Circuit"][
                    "Location"]["locality"] + " on " + x.strftime(
                        "%d %B, %I:%M %p") + " (Round " + str(
                            db["round"]
                        ) + "/" + season["MRData"]["total"] + ")" + ("(Sprint weekend)" if db["sprint"] else "")
    x = db["racetime"]
    if datetime.now() > datetime(x[0], x[1], x[2], x[3],
                                 x[4]) and not db["over"]:
        db["over"] = True
        updateDB(db)
        return "And with this, folks, the championship comes to an end!🏆🏆"
    updateDB(db)


def check_season():
    db = getDB()
    season = requests.get("http://ergast.com/api/f1/current.json").json()
    if season["MRData"]["RaceTable"]["season"] == datetime.now().strftime(
            "%Y"):
        db["over"] = False
        print(db["over"])
        updateDB(db)
        return ("⏰ The " + datetime.now().strftime("%Y") +
                " season is now here!\n\n" + get_round())
    else:
        updateDB(db)
        return


@c.event
async def on_ready():
    db = getDB()
    channel.append(c.get_channel(794503767277961219))
    channel.append(c.get_channel(933011520516919336))
    if "over" not in db.keys():
        db["over"] = False
        db["pic_sent"] = False
        db["open_sent"] = False
        db["close_sent"] = False
        db["quali_sent"] = False
        updateDB(db)
    if "round" not in db.keys():
        await channel[0].send(get_round())
    #get_round()
    print('ready', str(db["round"]))
    
    await start_loop()

  


@tasks.loop(hours=24)
async def check_race_week():
    db = getDB()
    if not db["over"]:
        print("1")
        x = db["racetime"]
        if datetime.now() + timedelta(days=8) > datetime(
                x[0], x[1], x[2], x[3], x[4]):
            if datetime.now().strftime("%a") == "Mon" and not db["pic_sent"]:
                await channel[0].send(file=discord.File('race week.jpg'))
                db["pic_sent"] = True
                db["open_sent"] = False

            if datetime.now().strftime("%a") != "Mon":
                db["pic_sent"] = False

            if datetime.now().strftime("%a") == "Fri" and not db["open_sent"]:
                q_time = db["qualitime"]
                q_time = datetime(q_time[0], q_time[1], q_time[2], q_time[3],) + timedelta(minutes=330)
                r_time = datetime(x[0], x[1], x[2], x[3], x[4]) + timedelta(minutes=330)
                await channel[0].send(
                    "⌛ " + db["next_race"] +
                    " predictions are now open 🟢\n\nThey close at-\nQualifying time: " + q_time.strftime("%A, %H:%M") + "\nRace time:           " + r_time.strftime("%A, %H:%M"))
                db["open_sent"] = True
                db["close_sent"] = False
                db["quali_sent"] = False
            updateDB(db)

    if db["over"] and datetime.now().strftime("%b") == "Mar":
        db["round"] = 1
        updateDB(db)
        await channel[0].send(check_season())


@tasks.loop(minutes=9)
async def close_predictions():
    db = getDB()
    print("2")
    if not db["over"] and db["open_sent"] and (not db["close_sent"]
                                               or not db["quali_sent"]):
        x = db["racetime"]
        q = db["qualitime"]
        print("here")
        racetime = datetime(x[0], x[1], x[2], x[3], x[4])
        qualitime = datetime(q[0], q[1], q[2], q[3], q[4])

        if (datetime.now() < racetime) and (
                datetime.now() + timedelta(minutes=10) > racetime):
            time.sleep((racetime - datetime.now()).total_seconds())
            await channel[0].send(db["next_race"] +
                                  " predictions are now closed 🔴 Good luck!")
            db["close_sent"] = True
            db["quali_sent"] = True
            db["open_sent"] = False

        if (datetime.now() < qualitime) and (
                datetime.now() + timedelta(minutes=10) > qualitime):
            time.sleep((qualitime - datetime.now()).total_seconds())
            await channel[0].send(db["next_race"] +
                                  (" sprint" if db["sprint"] else " qualifying") + " predictions are now closed 🟠")
            db["quali_sent"] = True
        updateDB(db)


@tasks.loop(hours = 1)
async def race_result_update():
    db = getDB()
    print("3")
    if not db["over"]:
        quali = requests.get("http://ergast.com/api/f1/current/" +
                             str(db["round"]) + "/results.json").json()
        if quali["MRData"]["RaceTable"]["Races"]:
            race_drivers = ["", "", ""]
            qual_drivers = ["", "", ""]
            name = ""
            for pos in quali["MRData"]["RaceTable"]["Races"][0]["Results"]:
                if int(pos["position"]) < 4:
                    race_drivers[int(pos["position"]) -
                                 1] = pos["Driver"]["code"].upper()
                if int(pos["grid"]) < 4 and int(pos["grid"]) > 0:
                    qual_drivers[int(pos["grid"]) -
                                 1] = pos["Driver"]["code"].upper()

            name = quali["MRData"]["RaceTable"]["Races"][0]["raceName"]
            result = '🏁' + " The " + str(db["year"]) + " " + name + " (Round " + str(db["round"]) + "/" + quali["MRData"]["total"] + ") is over and the results are in!🏁" + '\nTop 3 on the grid: \n' + '\n'.join(
                ((str(qual_drivers.index(driver) + 1) + ": " + driver +
                  ("", "👀")[driver == "HUL"]) for driver in qual_drivers
                 )) + '\n\nToday\'s race results: \n' + '\n'.join(
                     ((str(race_drivers.index(driver) + 1) + ": " + driver +
                       ("", "👀")[driver == "HUL"]) for driver in race_drivers))
            await channel[1].send(result)
            time.sleep(10)
            updateDB(db)
            await channel[1].send(get_round())


@race_result_update.before_loop
async def before_rupdate():
    time.sleep(2)
    await c.wait_until_ready()


@check_race_week.before_loop
async def before_raceweek():
    time.sleep(2)
    await c.wait_until_ready()


@close_predictions.before_loop
async def before_cpredict():
    time.sleep(2)
    await c.wait_until_ready()


@c.event
async def on_message(m):
    db = getDB()
    if str(m.author) == "LastFaceOG#8479":
        if m.content == "!kill yourself":
            c.logout()
            time.sleep(5)
        if m.content == "!reset":
            db["over"] = False
        if m.content == "!test":
            channel.append(m.channel)
            """race_result_update.stop()
            db["over"] = False
            race_result_update.start()
            """
def start_loop():
    close_predictions.start()
    race_result_update.start()
    return check_race_week.start()

if __name__ == "__main__":
    load_dotenv("../.env")
    c.run(secret.get("DISCORD_AUTH_KEY"))
