import discord
import random

TOKEN = 'ODk1MDc3Mzk5NzI3ODQ1Mzc2.YVzTyQ.D55M2yT1Z7Nt0QpTl0ZbixIz0yA'

client = discord.Client()

#Array party
party = {}
"""
idParty:
{
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
            boss:False
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
        if message.content.find("new-game") > 0:
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
            id = int(message.content.split("join", 1)[1])

            #check
            if await checkIdParty(id) == True:
                if await checkPlayerFromParty(message.author.id, id) == False:
                    await JoinParty(message.author, id)
                    await message.channel.send("you just joined the party")
                else:
                    await message.channel.send("you are already in a party")
            else:
                await message.channel.send("Id party not exsit")
        
        #leave party
        elif message.content.find("leave") > 0:
            #get position of party
            id = await getIdPartyFromIdPlayer(message.author.id)
            if id == None:
                await message.channel.send("You aren't joined in party")
            else:
                #leave party
                await leaveIdPlayerFromPosParty(message.author.id, id)
                await message.channel.send("Okay bye bye")
        
        #list player in party
        elif message.content.find("list") > 0:
            id = await getIdPartyFromIdPlayer(message.author.id)
            if id == None:
                await message.channel.send("You aren't joined in party")
            else:
                messageList = "Party ID: "+str(id)+"\n "
                messageList += "Players are:\n "
                i=0
                for player in party[id]["players"]:
                    i += 1
                    messageList += str(i)+" - "+party[id]["players"][player]['nickname']+"\n"
                await message.channel.send(messageList)
        
        #start game
        elif message.content.find("start") > 0:
            playerId = message.author.id
            #check player id
            if (index.get(playerId) != None):
                id = index[playerId]
                #check boss
                if party[id]["players"][playerId]["boss"] == True:
                    if party[id]["start"] == False:
                        party[id]["start"] = True
                        randomPlayer = randomStartPlayer(id)
                        party[id]["players"][randomPlayer]["myturn"] = True
                        await message.channel.send("Player start is "+party[id]["players"][randomPlayer]["nickname"])
                        # set game question
                        party[id]["pharse"]="E\' un animale domestico"
                        party[id]["word"]="gatto"
                        party[id]["keys"]=initialKeys(party[id]["word"])
                        party[id]["showword"]=replaceHideWord(party[id]["word"])
                        #
                        await message.channel.send(party[id]["pharse"])
                        await message.channel.send(party[id]["showword"])
                        await message.channel.send(party[id]["keys"])
                    else:
                        await message.channel.send("The party has already started!")
                else:
                    await message.channel.send("You aren't boss")
            else:
                await message.channel.send("Player not exist")

        elif message.content.find("answare-single") > 0:
            #get answare with remove withspace
            answare = message.content.split("answare-single", 1)[1].strip()
            playerId = message.author.id
            #check player
            if index.get(playerId) != None:
                partyId = index.get(playerId)
                if party[partyId]["players"][playerId]["myturn"] == True:
                    if len(answare) == 1:
                        if answare in party[partyId]["keys"]:
                            #check answare in word
                            if answare in party[partyId]["word"]:
                                party[partyId]["whiteword"].append(answare)
                                party[partyId]["showword"] = showWord(answare, partyId)
                                removeKeys(answare, partyId)
                                await message.channel.send("You are lucky!")
                                await message.channel.send(party[partyId]["pharse"])
                                await message.channel.send(party[partyId]["showword"])
                                await message.channel.send(party[partyId]["keys"])
                            else:
                                await message.channel.send("You were wrong!")
                            #next turn
                            playerIdTurn = nextTurn(partyId, playerId)
                            await message.channel.send(party[partyId]["players"][playerIdTurn]["nickname"]+" it's up to you")
                        else:
                            await message.channel.send("The char not exist")
                    else:
                        await message.channel.send("Not correct format answare")
                else:
                    await message.channel.send("Not is your turn! await.")
            else:
                await message.channel.send("Player not exist")

#add party
async def CreateParty(idParty, playerAdmin):
    party[idParty] = {
        "start":False,
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
                "myturn":False
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
            "myturn":False
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

def checkList(list, key):
    for word in list:
        if word == key:
            return True
    return False

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

def showWord(answare, partyId):
    word = ""
    for key in party[partyId]["word"]:
        if key in party[partyId]["whiteword"]:
            word += key + " "
        else:
            word += "\_ "
    return word

def removeKeys(answare, partyId):
    keysCopy = []
    for key in party[partyId]["keys"]:
        if key == answare:
            keysCopy.append("*")
        else:
            keysCopy.append(key)
    party[partyId]["keys"] = keysCopy

def nextTurn(partyId, playerId):
    i = list(party[partyId]["players"]).index(playerId)
    i += 1
    if i >= len(party[partyId]["players"]):
        playerIdChange = list(party[partyId]["players"])[0]
    else:
        playerIdChange = list(party[partyId]["players"])[i]

    party[partyId]["players"][playerId]["myturn"] = False
    party[partyId]["players"][playerIdChange]["myturn"] = True
    return playerIdChange
    
client.run(TOKEN)