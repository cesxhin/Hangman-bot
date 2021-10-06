import discord, os
import random

TOKEN = 'ODk1MDc3Mzk5NzI3ODQ1Mzc2.YVzTyQ.D55M2yT1Z7Nt0QpTl0ZbixIz0yA'

client = discord.Client()

#Array party
party = {}
"""
idParty:
{
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
                for player in party[id]:
                    i += 1
                    messageList += str(i)+" - "+party[id][player]['nickname']
                await message.channel.send(messageList)

#add party
async def CreateParty(idParty, playerAdmin):
    party[idParty] = {
        playerAdmin.id:{
            "nickname":playerAdmin.display_name,
            "boss":True
        }
    }
    index[playerAdmin.id] = idParty
async def getIdPartyFromIdPlayer(idPlayer):
    return index.get(idPlayer)

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
    if party[idParty][idPlayer].get("boss") == True:
        party.pop(idParty)
    else:
        party[idParty].pop(idPlayer, None)

client.run(TOKEN)