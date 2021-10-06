import discord, os
import random

TOKEN = 'ODk1MDc3Mzk5NzI3ODQ1Mzc2.YVzTyQ.D55M2yT1Z7Nt0QpTl0ZbixIz0yA'

client = discord.Client()

#Array party
party = []

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
            if await checkPlayer(message.author.discriminator) == False:
                while True:
                    id = random.randrange(0,999999)
                    if await checkIdParty(id) == False:
                        break
                await CreateParty(id, message.author)
                await message.channel.send("ok, your id party is: "+str(id))
            else:
                await message.channel.send("you are already in a party")

        #join party
        if message.content.find("join") > 0:
            #get id by message
            id = int(message.content.split("join", 1)[1])

            #check
            if await checkPlayer(id, message.author.discriminator) == False:
                await message.channel.send("you just joined the party")
            else:
                await message.channel.send("you are already in a party")
#add party
async def CreateParty(idParty, playerAdmin):
    party.append({
        "id":idParty,
        "players":[{
            "id":playerAdmin.discriminator,
            "nickname":playerAdmin.display_name
        }]
    })

#check exists id party
async def checkIdParty(idCheck):
    if len(party) > 0:
        for pos in party:
            if pos['id'] == idCheck:
                return True
    return False

#check with specific id of party
async def checkPlayer(idParty, idPlayer):
    if len(party) > 0:
        for pos in party:
            if pos['id'] == idParty:
                for players in pos['players']:
                    if players['id'] == idPlayer:
                        return True
    return False

#check player in general party
async def checkPlayer(idPlayer):
    if len(party) > 0:
        for pos in party:
            for players in pos['players']:
                if players['id'] == idPlayer:
                    return True
    return False
client.run(TOKEN)