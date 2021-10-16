from typing import Tuple
import discord, random, json, os

TOKEN = 'ODk1MDc3Mzk5NzI3ODQ1Mzc2.YVzTyQ.D55M2yT1Z7Nt0QpTl0ZbixIz0yA'

client = discord.Client()
#const
BASELIFE = 5
CURRENTPATH = os.getcwd()
#Array party
party = {}
"""
idParty:
{   "start":False,
    "finish":False,
    "pharse":None,
    "word":None,
    "whiteword":[],
    "keys":[],
    "showword":None,
    "players":
    [
        idPlayer:
        {
            nickname:pippo,
            boss:True
        },
        idPlayer:
        {
            nickname:pippa,
            boss:False,
            "myturn":False,
            "life":5
        },
        ...
    ]
},
idParty:
...
"""
#index
index = {}
"""
playerId:PartyId,
playerId:PartyId,
...
"""
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.find("!hanged") >= 0:
        #create new party
        if message.content.find("new-party") > 0:
            if await checkPlayer(message.author.id) == False:
                while True:
                    id = random.randrange(0,999999)
                    if await checkIdParty(id) == False:
                        break
                await CreateParty(id, message.author)
                await message.channel.send("ok, your id party is: "+str(id))
            else:
                await message.channel.send("you are already in a party")

        #join party
        elif message.content.find("join") > 0:
            #get id by message
            idParty = int(message.content.split("join", 1)[1])

            #check
            if await checkIdParty(idParty) == True:
                if await checkPlayerFromParty(message.author.id, idParty) == False:
                    await JoinParty(message.author, idParty)
                    await message.channel.send("you just joined the party")
                else:
                    await message.channel.send("you are already in a party")
            else:
                await message.channel.send("Id party not exsit")
        
        #leave party
        elif message.content.find("leave") > 0:
            #get position of party
            idParty = await getIdPartyFromIdPlayer(message.author.id)
            if idParty == None:
                await message.channel.send("You aren't joined in party")
            else:
                #leave party
                await leaveIdPlayerFromPosParty(message.author.id, idParty)
                await message.channel.send("Okay bye bye")
        
        #list player in party
        elif message.content.find("list") > 0:
            idParty = await getIdPartyFromIdPlayer(message.author.id)
            if idParty == None:
                await message.channel.send("You aren't joined in party")
            else:
                messageList = await getListPlayer(idParty)
                await message.channel.send(messageList)
        
        #start game
        elif message.content.find("start") > 0:
            bodyMessage = ""
            idPlayer = message.author.id
            #check player id
            if (index.get(idPlayer) != None):
                idParty = index[idPlayer]
                #check boss
                if party[idParty]["players"][idPlayer]["boss"] == True:
                    if party[idParty]["finish"] == True:
                        await resetParty(idParty)
                    if party[idParty]["start"] == False:
                        party[idParty]["start"] = True
                        randomPlayer = randomStartPlayer(idParty)
                        party[idParty]["players"][randomPlayer]["myturn"] = True
                        bodyMessage += "Player start is "+party[idParty]["players"][randomPlayer]["nickname"]+"\n"
                        #print lsit
                        messageList = await getListPlayer(idParty)
                        bodyMessage += messageList +"\n"
                        # set game question
                        with open(CURRENTPATH+'\\src\\list_question.json', encoding='utf-8') as json_file:
                            data = json.load(json_file)

                            #get random question
                            while True:
                                pos = random.randrange(0,len(data)-1)
                                #check equal question of the before
                                if data[pos]["answare"] == party[idParty]["word"]:
                                    continue
                                #set
                                party[idParty]["pharse"]=data[pos]["question"]
                                party[idParty]["word"]=data[pos]["answare"]
                                party[idParty]["keys"]=initialKeys(party[idParty]["word"])
                                party[idParty]["showword"]=replaceHideWord(party[idParty]["word"])
                                break
                        #
                        bodyMessage += party[idParty]["pharse"] + "\n"
                        bodyMessage += party[idParty]["showword"] + "\n"
                        bodyMessage += str(party[idParty]["keys"])
                        await message.channel.send(bodyMessage)
                    else:
                        await message.channel.send("The party has already started!")
                else:
                    await message.channel.send("You aren't boss")
            else:
                await message.channel.send("Player not exist")

        elif message.content.find("answ") > 0:
            bodyMessage = ""
            idPlayer = message.author.id
            #check player
            if index.get(idPlayer) != None:
                idParty = index.get(idPlayer)
                if party[idParty]["players"][idPlayer]["myturn"] == True:
                    if party[idParty]["finish"] == True:
                        await message.channel.send("This round is finish")
                        return
                    
                    #single char
                    if message.content.find("char") > 0:
                        #get answare with remove withspace
                        answare = message.content.split("char", 1)[1].strip()
                        if len(answare) == 1:
                            if answare in party[idParty]["keys"]:
                                #check answare in word
                                if answare in party[idParty]["word"]:
                                    party[idParty]["whiteword"].append(answare)
                                    party[idParty]["showword"] = showWord(idParty)
                                    bodyMessage += "You are lucky!" +"\n"
                                else:
                                    #remove life
                                    party[idParty]["players"][idPlayer]["life"] -= 1
                                    bodyMessage += "You were wrong!" + "\n"
                            else:
                                 bodyMessage += "The char not exist" + "\n"
                        else:
                            bodyMessage += "Not correct format answare" + "\n"

                    #word
                    elif message.content.find("word") > 0:
                        answare = message.content.split("word", 1)[1].strip()
                        if len(answare) > 1:
                            if answare in party[idParty]["word"]:
                                party[idParty]["showword"] = answare
                                bodyMessage += "You are lucky!"+ "\n"
                            else:
                                bodyMessage += "You were wrong!"+ "\n"
                                party[idParty]["players"][idPlayer]["life"] -= 1
                                return

                    #set party
                    if checkDeathAll(idParty) == True:
                        party[idParty]["finish"]=True
                        bodyMessage += "Game Over"+ "\n"
                        await message.channel.send(bodyMessage)
                        return
                    else:
                        if party[idParty]["word"] == party[idParty]["showword"]:
                            party[idParty]["finish"]=True
                            bodyMessage += "you are win!"+ "\n"
                            await message.channel.send(bodyMessage)
                            return
                        #remove key
                        removeKeys(answare, idParty)
                        #next turn
                        idPlayerTurn = nextTurn(idParty, idPlayer)
                        bodyMessage += party[idParty]["players"][idPlayerTurn]["nickname"]+" it's up to you" + "\n"
                        #print lsit
                        messageList = await getListPlayer(idParty)
                        bodyMessage += messageList + "\n"
                        #print question
                        bodyMessage += party[idParty]["pharse"] + "\n"
                        bodyMessage += party[idParty]["showword"] + "\n"
                        bodyMessage += str(party[idParty]["keys"])
                        await message.channel.send(bodyMessage)
                else:
                    await message.channel.send("Not is your turn! await.")
            else:
                await message.channel.send("Player not exist")

        elif message.content.find("help") > 0:
            bodyMessage = "**new-party** --> crea nuovo party per invitare i tuoi amici per poi giocare insieme!\n"
            bodyMessage += "**join** [id] --> entri con un id del party da qualcuno che ti ha invitato\n"
            bodyMessage += "**list** --> vedi tutti i giocatori presenti nel party\n"
            bodyMessage += "* **start** --> inizi/ricomincia una nuova partita\n"
            bodyMessage += "**answ** <*char*/*word*> [your answare] --> rispondi con due modalità possibili\n"
            bodyMessage += "\n* solo chi ha creato party può eseguire questo commando\n"
            await message.channel.send(bodyMessage)

#add party
async def CreateParty(idParty, playerAdmin):
    party[idParty] = {
        "start":False,
        "finish":False,
        "pharse":None,
        "word":None,
        "whiteword":[],
        "keys":[],
        "showword":None,
        "players":
        {
            playerAdmin.id:{
                "nickname":playerAdmin.display_name,
                "boss":True,
                "myturn":False,
                "life":BASELIFE
            }
        }
    }
    index[playerAdmin.id] = idParty

#get idParty
async def getIdPartyFromIdPlayer(idPlayer):
    return index.get(idPlayer)

#join party
async def JoinParty(player, idParty):
    party[idParty]["players"][player.id]={
            "nickname":player.display_name,
            "boss":False,
            "myturn":False,
            "life":BASELIFE
        }
    index[player.id] = idParty

#check exist id party
async def checkIdParty(idParty):
    if len(party) > 0:
        if party.get(idParty) != None:
            return True
    return False

#check with specific id of party
async def checkPlayerFromParty(idPlayer, idParty):
    if len(party) > 0:
        value = index.get(idPlayer)
        if value != None:
            if value == idParty:
                return True
    return False

#check player in general party
async def checkPlayer(idPlayer):
    if len(party) > 0:
        if index.get(idPlayer) != None:
            return True
    return False

#get list player by idParty
async def getListPlayer(idParty):
    messageList = "Party ID: "+str(idParty)+"\n "
    messageList += "Players are:\n "
    i=0
    for player in party[idParty]["players"]:
        i += 1
        messageList += str(i)+" - "+party[idParty]["players"][player]['nickname'] + " "
        for i in range(party[idParty]["players"][player]["life"]):
            messageList += "❤️ "
        for i in range(5 - party[idParty]["players"][player]["life"]):
            messageList += "💔 "
        messageList += "\n"
    return messageList

#leave player by party
async def leaveIdPlayerFromPosParty(idPlayer, idParty):
    index.pop(idPlayer, None)
    if party[idParty]["players"][idPlayer].get("boss") == True:
        party.pop(idParty)
    else:
        party[idParty]["players"].pop(idPlayer, None)

#choose random player for first start
def randomStartPlayer(idParty):
    return random.choice(list(party[idParty]["players"].keys()))

#hide word
def replaceHideWord(word):
    wordHide = ""
    for key in word:
        wordHide += "\_ "
    return wordHide

#check exists key in list
def checkList(list, key):
    for word in list:
        if word == key:
            return True
    return False

#set list word for game
def initialKeys(word):
    keys = []
    alphabetical = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
    missing = 0
    for i in range(20):
        if i%2 == 0 and len(word) > 0:
            pos = random.randrange(len(word))
            if checkList(keys, word[pos]) == False:
                keys.append(word[pos])
            else:
                missing += 1
            word = word[0:pos]+word[pos+1:]
        else:
            while True:
                wordRandom = random.choice(alphabetical)
                if checkList(keys, wordRandom) == False:
                    keys.append(wordRandom)
                    break

    for i in range(missing):
        while True:
            wordRandom = random.choice(alphabetical)
            if checkList(keys, wordRandom) == False:
                keys.append(wordRandom)
                break
    return keys

#show only choose by players
def showWord(idParty):
    word = ""
    for key in party[idParty]["word"]:
        if key in party[idParty]["whiteword"]:
            word += key
        else:
            word += "\_ "
    return word

def removeKeys(answare, idParty):
    keysCopy = []
    for key in party[idParty]["keys"]:
        if key == answare or len(key) <= 0:
            keysCopy.append("*")
        else:
            keysCopy.append(key)
    party[idParty]["keys"] = keysCopy

#next turn of the player
def nextTurn(idParty, idPlayer):
    i = list(party[idParty]["players"]).index(idPlayer)
    while True:
        i += 1
        if i >= len(party[idParty]["players"]):
            i=0
            playerIdChange = list(party[idParty]["players"])[i]
        else:
            playerIdChange = list(party[idParty]["players"])[i]
        
        if party[idParty]["players"][playerIdChange]["life"] > 0:
            break

    party[idParty]["players"][idPlayer]["myturn"] = False
    party[idParty]["players"][playerIdChange]["myturn"] = True
    return playerIdChange

#check if death all party
def checkDeathAll(idParty):
    for player in party[idParty]["players"]:
        if party[idParty]["players"][player]["life"] > 0:
            return False
    return True

#reset party
async def resetParty(idParty):
    #reset player
    for player in party[idParty]["players"]:
        party[idParty]["players"][player]["life"] = BASELIFE
        party[idParty]["players"][player]["myturn"] = False
    party[idParty]["finish"]=False
    party[idParty]["start"]=False

client.run(TOKEN)