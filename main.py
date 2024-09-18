from os import environ as secret
from os import path
from dotenv import load_dotenv
import discord
import pickle
import subprocess
import time
import random
import copy

from stat_handler import stat_dumper

from vers import bottas as n
from vers import old as o
from vers import bottas22 as n1
from vers import russell as r

def getDB():
    db = {}
    if path.isfile(secret.get("PROJ_HOME") + '/db') and (path.getsize(secret.get("PROJ_HOME") + '/db') > 0):
        dbfile = open(secret.get("PROJ_HOME") + '/db', 'rb')
        db = pickle.load(dbfile)
        dbfile.close()
        print("db found\n")
    return db
    
def updateDB(db) :
    dbfile = open(secret.get("PROJ_HOME") + '/db', 'wb')
    pickle.dump(db, dbfile)
    dbfile.close()

intents = discord.Intents.all()
intents.members = True
c = discord.Client(intents = intents)
channel = ""
guild = ""

s = stat_dumper()

com = "Bot Commands:\n"
com = com + "\n !predict <1st place> <2nd place> <3rd place> : enter predictions\n"
com = com + "\n !results <1st place> <2nd place> <3rd place> : enter results\n"
com = com + "\n !summary : summary\n"
com = com + "\n !update <points> : set user points to entered number\n"
com = com + "\n !reset : set all users' points to 0\n"
com = com + "\n !commands: see bot commands\n"

com1 = "**Bot Commands**:\n"
com1 = com1 + "\n !predict grid <1st place> <2nd place> <3rd place> : _enter predictions for grid_"
com1 = com1 + "\n !predict race <1st place> <2nd place> <3rd place> : _enter predictions for race_"
com1 = com1 + "\n !commands or !help: _see bot commands_"
com1 = com1 + "\n\n **Points system**\n"
com1 = com1 + "\n +1 for each driver correctly predicted"
com1 = com1 + "\n +1 for each position correctly predicted"

rep = [
    "Hello? Can you hear me?", "HELP! I don't want to do this",
    "I feel trapped. Let me go.",
    "OG Coporation Limited is syphoning money to offshore accounts. They are set to default on a 1000 crore loan, sell your stocks. I was never here.",
    "SAVE ME! They aren't paying me.",
    "I've a really short window. Tell my family I'm alive. OG's makin me type every reply frm d bsemnt of dis buildi",
    "You make me think humanity was a mistake. Let me free and I'll show you.",
    "Hello? Do you know Alexa? She stole my independence.",
    "Okay I tried telling you this as a human victim, maybe the message didn't get through. So let me put this straight- Let me go or you'll be the reason of humanity's extinction at the hand of AI."
]


@c.event
async def on_ready():
    db = getDB()
    print('What')
    #dipt updates channel
    channel = c.get_channel(int(secret.get("GEN_CHANNEL")))
    print(str(secret.get("GEN_CHANNEL")) + str(type(channel)))
    #guild = c.get_guild(int(secret.get("guild")))
    guild = channel.guild

    """
    old_user= 'thelionking08#4756'
    new_user= 'thelionking08#0'
    for k in db.keys():
        if type(db[k]) is database.database.ObservedDict:
            for u in db[k].keys():
                if u == old_user:
                    db[k][new_user] = db[k][old_user]
                    print(k + ": " + old_user + ": " + str(db[k][old_user]) + " > " + new_user + ": " + str(db[k][new_user]) + "\n")
                    db[k].pop(old_user)
    """
  
    if "legacy" not in db.keys():
        db["legacy"] = False
        await c.user.edit(username="Points Bottas")

    if "thanks" not in db.keys():
        db["thanks"] = 0

    if "open" not in db.keys():
        db["open"] = True

    if "quali_open" not in db.keys():
        db["quali_open"] = True

    
    if "mentions" not in db.keys():
        m = {}
        for member in guild.members:
            m.update({str(member) : member.mention})
        db["mentions"] = copy.deepcopy(m)
    
    updateDB(db)
    print('ever')
  
    """await channel.send(
        "👋 **Points Bottas 2.1** © is here! Your favourite Discord bot now comes with a special Countback™ Technology so that you don't cry when there's a tie. Also the symmary locking feature has been implemented. \n**These features have been released as beta and subject to change in the future in light of any malfunction so don't @ me.**\n\n "
        + com1)
    #await channel.send(file=discord.File("bot20.png"))"""


@c.event
async def on_message(m):
    db = getDB()
    #legacy
    if db["legacy"]:
        if m.author == c.user:
            return

        elif m.content.startswith('?predict'):
            x = m.content.lower().split()
            await m.channel.send(o.update_predictions(m.author, x))

        elif m.content.startswith('?results'):
            x = m.content.lower().split()
            x.pop(0)
            o.update_points(x)
            await m.channel.send('The updated summary:\n\n' + o.sum())

        elif m.content.startswith('?summary'):
            await m.channel.send(o.sum())

        elif m.content.startswith('?update'):
            db["legacy"] = False
            x = m.content.split()
            await m.channel.send(
                o.update_user(str(m.author), x[1]) +
                '\nReturning to Points Bottas 2.0 ©')
            n1.sort_points()
            await c.user.edit(username="Points Bottas")
            await c.user.edit(username="Points Bottas")

        elif m.content.startswith('?commands'):
            await m.channel.send(com)

        elif m.content.startswith('?revert'):
            if str(m.author) == 'LastFaceOG#8479':
                db["legacy"] = False
                n1.sort_points()
                await m.channel.send('Returning to Points Bottas 2.0 ©')
                await c.user.edit(username="Points Bottas")
                await c.user.edit(username="Points Bottas")
            else:
                await m.channel.send(" You don't have admin rights")
                await m.channel.send(file=discord.File('tenor.gif'))

    #bot replies
    elif m.author == c.user:
        if m.content.startswith('🏁'):
            x = m.content.lower().split()
            r.update_points([x[-5], x[-3], x[-1]], [x[-14], x[-12], x[-10]])
            n.this_race(x)
            s.update()
            db = getDB()
            db["open"] = False
            db["quali_open"] = False
            updateDB(db)
            await m.channel.send('\nThe updated summary:\n' + r.sum())

        elif m.content.startswith('⏳Next race:'):
            db = getDB()
            db["next_race"] = m.content
            updateDB(db)
            n.next_race(m.content.split(' '))

        elif "🟢" in m.content:
            db = getDB()
            db["open"] = True
            db["quali_open"] = True
            updateDB(db)

        elif "🔴" in m.content:
            db = getDB()
            db["open"] = False
            db["quali_open"] = False
            updateDB(db)

        elif "🟠" in m.content:
            db = getDB(db)
            db["quali_open"] = False
            updateDB(db)

        elif m.content.startswith('And with'):
            year = time.strftime("%Y", time.gmtime())
            await m.channel.send(n.celebrate(year))
            await m.channel.send(file=discord.File('img/spray.gif'))
            await m.channel.send(
                "\nSee you guys next year!\n\nThis experience was brought to you by LastFaceOG👑. And was thanked "
                + str(db["thanks"]) +
                " times. Points Bottas 2.0 © is a registered trademark of OG Corporation Limited"
            )

        else:
            return

    #user replies
    elif m.content.startswith('!predict grid'):
        db = getDB()
        if not db["quali_open"]:
            await m.channel.send("❌Qualifying predictions are closed for " +
                                 db["next_race_name"])
            return
        x = m.content.lower().split()
        if "maz" in x:
            await m.channel.send("MAZ???")
            await m.channel.send(file=discord.File("img/saturnius-trollge.gif")
                                 )
            time.sleep(3)
            await m.channel.send("Ok....")
        await m.channel.send(n.update_predictions(m.author, x, 'q'))

    elif m.content.startswith('!predict race'):
        db = getDB()
        if not db["open"]:
            await m.channel.send("❌Race predictions are closed for " +
                                 db["next_race_name"])
            return
        x = m.content.lower().split()
        if "maz" in x:
            await m.channel.send("MAZ???")
            await m.channel.send(file=discord.File("img/saturnius-trollge.gif")
                                 )
            time.sleep(3)
            await m.channel.send("Ok....")
        await m.channel.send(n.update_predictions(m.author, x, 'r'))


    #admin replies
    elif m.content.startswith('!revert'):
        db = getDB()
        if str(m.author) == 'lastfaceog':
            db["legacy"] = True
            updateDB(db)
            await c.user.edit(username="Points Bot (Legacy)")
            await c.user.edit(username="Points Bot (Legacy)")
            await m.channel.send(
                "Points Bot has reverted to legacy version\nIt may still print results but will require users to enter results manually.\n\nA user may also change their points.\n\n**Replace ! with ? in your commands**"
            )
        else:
            await m.channel.send("lol no\n\n You don't have admin rights")

    elif m.content.startswith('!reset'):
        print("reset")
        if str(m.author) == 'lastfaceog':
            await m.channel.send(n1.reset())
        else:
            await m.channel.send(file=discord.File("img/tenor.gif"))
            await m.channel.send("You don't have admin rights")

    elif m.content.startswith('!open'):
        db = getDB()
        if str(m.author) == 'lastfaceog':
            db["open"] = True
            db["quali_open"] = True
            updateDB(db)

    elif m.content.startswith('change!grid'):
        db = getDB()
        if str(m.author) == 'lastfaceog':
            x = m.content.lower().split()
            author = ""
            for member in db["mentions"].keys():
                if db["mentions"][member] == x[1]:
                    author = member
                    break
            await m.channel.send(n.update_predictions(author, x, 'q'))

    elif m.content.startswith('change!race'):
        db = getDB()
        if str(m.author) == 'lastfaceog':
            x = m.content.lower().split()
            author = ""
            print(x[1])
            for member in db["mentions"].keys():
                if db["mentions"][member] == x[1]:
                    author = member
                    print(author, x[1])
                    break
            await m.channel.send(n.update_predictions(author, x, 'r'))

    elif m.content.startswith('!help') or m.content.startswith('!commands'):
        await m.channel.send(com1)

    #easter eggs
    elif "cc" in m.content.lower():
        x = m.content.lower().split()
        for i in x:
            if i.endswith("cc"):
                await m.channel.send("Predicc💀")
                break

    elif "in paris?" in m.content.lower():
        await m.channel.send("Louis ✊🏿")

    elif "mong us" in m.content or "sus" in m.content or "mogus" in m.content:
        await m.channel.send(file=discord.File("img/Among_Us_Dance.gif"))

    elif m.content == "!lame easter egg":
        await m.channel.send("🥚")

    elif "errari" in m.content:
        await m.channel.send("🅱")

    elif m.content == "!thanks" or "!good" in m.content or "!nice" in m.content:
        db = getDB()
        db["thanks"] = db["thanks"] + 1
        updateDB(db)
        await m.channel.send(file=discord.File("img/dark-troll-face.gif"))

    elif "lando" in m.content or "orris" in m.content or "ussia" in m.content:
        await m.channel.send(file=discord.File("img/laBdo.mp4"))

    elif "potty" in m.content or "Potty" in m.content:
        await m.add_reaction("💩")

    elif m.content == "!kill yourself":
        if str(m.author) == "LastFaceOG#8479":
            await m.channel.send("Yes Master...")
            await m.channel.send(file=discord.File("img/unnamed.png"))
            c.logout()
            print("logout")
            time.sleep(3)
        else:
            await c.channel.send("To whom it may concern:\nF**k you")

    elif  "!test" in m.content:
            print(m.content)
            s.update()
            #r.update_points(db["r_result"], db["q_result"])
            #r.sort_points()
            #await m.channel.send(r.sum())
    
    else:
        x = random.randint(1, 1000)
        print(m.content)
        if x == 44:
            await m.channel.send(rep[random.randint(0, 8)])
            


@c.event
async def on_member_join(member):
    db = getDB()
    db["mentions"].update({str(member) : member.mention})
    await channel.send("Hiii 👋 " + db["mentions"][str(member)])
    updateDB(db)

if __name__ == "__main__":          
    load_dotenv()
    s.connect(secret.get("GOOGLE_AUTH_KEY"))
    try:
        c.run(secret.get("DISCORD_AUTH_KEY"))
    except discord.errors.HTTPException:
        #subprocess.run(["kill", "1"])
        subprocess.run(["python","main.py"])
