import discord
from discord.ext import commands
import os
import requests
import json
from replit import db
from keep_alive import keep_alive
from riotwatcher import LolWatcher
import pprint
import asyncio
# Private API Tokens
import config

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Private Tokens
API_KEY = config.API_KEY
TOKEN = config.TOKEN

# watcher = LolWatcher(os.environ['API_KEY'])
watcher = LolWatcher(API_KEY)
platformRoutingValue = 'NA1'

# db.clear()


def showUserTrackerDB():
  if "actualNamesTracked" in db.keys():
    actualNamesTracked = list(db["actualNamesTracked"])
    if len(actualNamesTracked) > 0:
      return (", ".join(tuple(actualNamesTracked)))
    else:
      return None


def showMatchTrackerDB():
  if "matches" in db.keys():
    matchesTracked = list(db["matches"])

    # the most scuffed way of getting around ObservedList & concatenating
    if len(matchesTracked) > 0:
      x = len(matchesTracked) - 1
      result = ''
      while x >= 0:
        if x + 1 < len(matchesTracked):
          result = matchesTracked[x][0] + ", " + result
        else:
          result = matchesTracked[x][0] + " " + result
        x -= 1

      return (result)

    else:
      return None


def updateUserTrackerDB():
  if "actualNamesTracked" in db.keys():
    actualNamesTracked = db["actualNamesTracked"]
    matches = db["matches"]

    # if(len(actualNamesTracked) >= 10):
    #   return (f"You have tracked too many accounts. Please remove some to add more")

    if summonerName in actualNamesTracked:
      # User already tracked
      return (False)
    else:
      actualNamesTracked.append(summonerName)
      db["actualNamesTracked"] = actualNamesTracked

      matches.append(list(getMatches()))
      db["matches"] = matches

      #user wasn't already tracked
      return (True)
  else:
    db["actualNamesTracked"] = [summonerName]
    db["matches"] = [getMatches()]


def updateMatchTrackerDB():
  actualNamesTracked = db["actualNamesTracked"]
  index = actualNamesTracked.index(summonerName)
  matches = db["matches"]
  matches[index] = getMatches()
  db["matches"] = matches


def deleteTrackerDB():
  if "actualNamesTracked" in db.keys():
    actualNamesTracked = db["actualNamesTracked"]
    matches = db["matches"]

    if summonerName in actualNamesTracked:
      matchIndex = actualNamesTracked.index(summonerName)
      actualNamesTracked.remove(summonerName)
      db["actualNamesTracked"] = actualNamesTracked
      del matches[matchIndex]
      db["matches"] = matches
      return (True)
    else:
      return (False)


# used for manual testing
def setMatchTrackerDB():
  actualNamesTracked = db["actualNamesTracked"]
  index = actualNamesTracked.index(summonerName)

  matches = db["matches"]
  matches[index] = "test"
  db["matches"] = matches


def getIDs(key):
  # {
  #     'id': 'qIZ-qZ9aabbF3K32wbX7mrZ-pDXY4WXsgQJY_yk2ojZrGx3e',
  #     'accountId': '6zT9PohGZaig112iF942b21KH5CH2_2nh74YNQm_isjEK3PUaSYk5MFr',
  #     'puuid': 'zeILcuHlnuw5Bwt93N8sJanzdJSuZXZZ-lFMpcoHMkwdOfzFqUoJHYb4jmZLA40dbl73y9m818Lwxw',
  #     'actualName': 'hamlegs',
  #     'profileIconId': 5499,
  #     'revisionDate': 1682827487000,
  #     'summonerLevel': 498
  # }
  #   {
  #     "id": "z29tqgcJp4T9MfZNr1A0z8lCMCqODyuXWkWyHBtLufnhpFtu",
  #     "accountId": "gerOFonyPsg7hQM4A049dkMOv15KIZ3ldnqr8KctEqyPhLrLob2y7RsY",
  #     "puuid": "btSSf87gAPi8rK_rg8eURSEEk-sDgF_E23N9sTx5U-yRx8UYekN9LPXkKCUOFC8sWXWqn0_3mnQ-2A",
  #     "name": "hamlegy",
  #     "profileIconId": 3478,
  #     "revisionDate": 1684707059143,
  #     "summonerLevel": 61
  # }
  return (watcher.summoner.by_name(platformRoutingValue, summonerName)[key])


def getRank():
  summonerID = getIDs('id')
  summonerLeagueStats = watcher.league.by_summoner(platformRoutingValue,
                                                   summonerID)
  # [
  #   {'leagueId': '91891182-c0fc-43e6-90f8-e196bdda5fc3',
  #   'queueType': 'RANKED_SOLO_5x5',
  #   'tier': 'GOLD',
  #   'rank': 'I',
  #   'summonerId': 'qIZ-qZ9aabbF3K32wbX7mrZ-pDXY4WXsgQJY_yk2ojZrGx3e',
  #   'summonerName': 'hamlegs',
  #   'leaguePoints': 8,
  #   'wins': 35,
  #   'losses': 37,
  #   'veteran': False,
  #   'inactive': False,
  #   'freshBlood': False,
  #   'hotStreak': False},
  #  {'leagueId': 'a7a35cef-8ca5-4fee-8072-164efb0adade',
  #   'queueType': 'RANKED_FLEX_SR',
  #   'tier': 'SILVER',
  #   'rank': 'III',
  #   'summonerId': 'qIZ-qZ9aabbF3K32wbX7mrZ-pDXY4WXsgQJY_yk2ojZrGx3e',
  #   'summonerName': 'hamlegs',
  #   'leaguePoints': 39,
  #   'wins': 4,
  #   'losses': 6,
  #   'veteran': False,
  #   'inactive': False,
  #   'freshBlood': False,
  #   'hotStreak': False}
  # ]
  return (f"{summonerLeagueStats[0]['tier']} {summonerLeagueStats[0]['rank']}")


def getMatches():
  summonerPUUID = getIDs('puuid')
  matches = watcher.match.matchlist_by_puuid(platformRoutingValue,
                                             summonerPUUID,
                                             count=1)
  return matches


def getMatchStats():
  match = getMatches()[0]
  stats = watcher.match.by_id(platformRoutingValue, match)
  participants = stats['metadata']['participants']
  # pprint.pprint((participants), sort_dicts=False)

  participant = participants.index(getIDs('puuid'))
  participantStats = stats['info']['participants'][participant]
  # print(participant)
  # pprint.pprint((stats['info']['participants'][participant]), sort_dicts=False)
  intValue = None
  KDA = (int(participantStats['kills']) +
         int(participantStats['assists'])) / int(participantStats['deaths'])
  if KDA > 3:
    intValue = False
  if KDA < .75:
    intValue = True

  return [(
    f"{getIDs('name')} had a KDA of {participantStats['kills']}/{participantStats['deaths']}/{participantStats['assists']} in their latest game."
  ), intValue]


def cleanName(msg):
  actualNameInput = msg[(msg.index(' ') + 1):]
  return actualNameInput.replace(" ", "")


@client.event
async def on_ready():
  print("Ready! Logged in as {0.user}".format(client))
  client.loop.create_task(autoChecker())
  count = 0
  while (True):
    await autoChecker()
    count += 1
    print(count)
    await asyncio.sleep(60)  # Sleep for 60 seconds before running again


#Stores all commands
@client.event
async def autoChecker():
  global summonerName
  summonerName = ''

  channel = client.get_channel(1109734902854844509)
  if ("matches" in db.keys() and "actualNamesTracked" in db.keys()):
    matchesTracked = list(db["matches"])
    index = 0
    for user in db["actualNamesTracked"]:
      print(user)
      summonerName = user
      if (getMatches()[0] != matchesTracked[index][0]):
        print(f"Match for {user} is not the same")
        updateMatchTrackerDB()

        gameStats = getMatchStats()[0]
        inted = getMatchStats()[1]
        # print(inted) # check what value inted is
        intedString = "They were probably okay."
        if inted == True:
          intedString = "They were probably an inter."
        if inted == False:
          intedString = "They were probably a carry."

        # haha embed

        actualName = getIDs('name')  # actualName is the name with spaces
        url = f"https://op.gg/summoners/na/{summonerName}"
        description = f"{gameStats} {intedString}"
        imageUrl = f"http://ddragon.leagueoflegends.com/cdn/13.10.1/img/profileicon/{str(getIDs('profileIconId'))}.png"
        # print(imageUrl)

        color = 0x9BF6FF  #Aqua

        embed = discord.Embed(title=actualName,
                              url=url,
                              description=description,
                              color=color)
        embed.set_thumbnail(url=imageUrl)

        await channel.send(embed=embed)

      # await channel.send(f"{gameStats} {intedString}")

      # await message.channel.send(f"Match for {user} is not the same")

      else:
        print(f"Match for {user} is the same")
        # await message.channel.send(f"Match for {user} is the same")
      index += 1


@client.event
async def on_message(message):

  msg = message.content

  global summonerName
  summonerName = ''

  if message.author == client.user:
    return

  # if msg.startswith('$help'):
  #   embed=discord.Embed(title="Commands:", url=None, description=description, color=color)
  #   await message.channel.send(embed=embed)

  if msg.startswith('$showusers'):
    # if(showUserTrackerDB() == None):
    #   await message.channel.send("No users currrently tracked.")
    # else:
    #   await message.channel.send(f"Tracking: {showUserTrackerDB()}.")
    output = "No users currrently tracked." if showUserTrackerDB(
    ) == None else f"Tracking: {showUserTrackerDB()}."
    await message.channel.send(output)

  if msg.startswith('$showmatches'):
    # if(showMatchTrackerDB() == None):
    #   await message.channel.send("No matches currrently tracked.")
    # else:
    #   await message.channel.send(f"Tracking: {showMatchTrackerDB()}.")
    output = "No matches currrently tracked." if showMatchTrackerDB(
    ) == None else f"Tracking: {showMatchTrackerDB()}."
    await message.channel.send(output)

  if msg.startswith('$rank'):
    summonerName = cleanName(
      msg)  # summonerName is stripped of all spaces, for URLs
    actualName = getIDs('name')  # actualName is the name with spaces
    url = f"https://op.gg/summoners/na/{summonerName}"
    rank = getRank()
    description = f"{actualName}'s rank is {rank}."
    color = 0xa0c4ff  #Blue

    embed = discord.Embed(title=actualName,
                          url=url,
                          description=description,
                          color=color)
    await message.channel.send(embed=embed)

  if msg.startswith('$track'):
    summonerName = cleanName(
      msg)  # summonerName is stripped of all spaces, for URLs
    actualName = getIDs('name')  # actualName is the name with spaces
    url = f"https://op.gg/summoners/na/{summonerName}"
    description = f"{actualName} has been added to the tracker!"
    color = 0xfdffb6  #Yellow

    # If the user is already tracked, return an error
    if (updateUserTrackerDB() == False):
      url = None
      description = f"{actualName} is already tracked!"
      color = 0xffadad  #Red

    # Otherwise, return a new tracking message
    embed = discord.Embed(title=actualName,
                          url=url,
                          description=description,
                          color=color)
    await message.channel.send(embed=embed)

  if msg.startswith('$untrack'):
    summonerName = cleanName(msg)
    actualName = getIDs('name')
    url = f"https://op.gg/summoners/na/{summonerName}"
    description = f"{actualName} has been deleted from the tracker!"
    color = 0xfdffb6  #Yellow

    if (not deleteTrackerDB()):
      url = ""
      description = f"{actualName} is not being tracked!"
      color = 0xffadad  #Red

    embed = discord.Embed(title=actualName,
                          url=url,
                          description=description,
                          color=color)
    await message.channel.send(embed=embed)

  if msg.startswith('$matchcheck'):
    summonerName = cleanName(msg)
    actualName = getIDs('name')

    gameStats = getMatchStats()[0]
    inted = getMatchStats()[1]

    intedString = "They were probably okay."
    if inted == True:
      intedString = "They were probably an inter."
    if inted == False:
      intedString = "They were probably not an inter."

    await message.channel.send(f"{gameStats} {intedString}")

  if msg.startswith('$test'):
    matchesTracked = list(db["matches"])
    index = 0
    for user in db["actualNamesTracked"]:
      print(user)
      summonerName = user
      if (getMatches()[0] != matchesTracked[index][0]):
        print(f"Match for {user} is not the same")
        updateMatchTrackerDB()

        gameStats = getMatchStats()[0]
        inted = getMatchStats()[1]

        intedString = "They were probably okay."
        if inted == True:
          intedString = "They were probably an inter."
        if inted == False:
          intedString = "They were probably not an inter."

        # haha embed

        actualName = getIDs('name')  # actualName is the name with spaces
        url = f"https://op.gg/summoners/na/{summonerName}"
        description = f"{gameStats} {intedString}"
        imageUrl = f"http://ddragon.leagueoflegends.com/cdn/13.10.1/img/profileicon/{str(getIDs('profileIconId'))}.png"
        # print(imageUrl)

        color = 0x9BF6FF  #Aqua

        embed = discord.Embed(title=actualName,
                              url=url,
                              description=description,
                              color=color)
        embed.set_thumbnail(url=imageUrl)

        await message.channel.send(embed=embed)

        # await channel.send(f"{gameStats} {intedString}")

        # await message.channel.send(f"Match for {user} is not the same")

      else:
        print(f"Match for {user} is the same")
        await message.channel.send(
          f"No new matches for {user} have been found.")
        # await message.channel.send(f"Match for {user} is the same")
      index += 1

  # used for manual testing
  if msg.startswith('$setmatch'):
    summonerName = cleanName(msg)
    setMatchTrackerDB()
    print(showMatchTrackerDB())

  if msg.startswith('$clear'):
    db.clear()
    await message.channel.send(f"The database has been cleared.")


# Write the while loop to keep it going

# Running the bot
keep_alive()
client.run(TOKEN)

# client.run(os.environ['TOKEN'])
