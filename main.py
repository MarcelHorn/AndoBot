import discord
import os
import requests
import json

from keep_alive import keep_alive


client = discord.Client()

def get_quote():
  response = requests.get("https://zenquotes.io/api/random")
  json_data = json.loads(response.text)
  quote = json_data[0]["q"] + " -" + json_data[0]["a"]
  return quote

def get_joke():
  response = requests.get("https://official-joke-api.appspot.com/random_joke")
  json_data = json.loads(response.text)
  joke = json_data["setup"]+ " -" + json_data["punchline"]
  return joke

@client.event
async def on_raw_reaction_add(payload):
  ChID = 852611783696711701 
  guild_id = payload.guild_id
  guild = discord.utils.find(lambda g : g.id == guild_id, client.guilds)
  
  if payload.channel_id != ChID:
        return
  
  member = await(await client.fetch_guild(payload.guild_id)).fetch_member(payload.user_id)
  if member is not None:
    if payload.emoji.name == "🏹":
      mh = discord.utils.get(guild.roles, name="Monster Hunter")
      await member.add_roles(mh)
    if payload.emoji.name == "🇿":
      zelda = discord.utils.get(guild.roles, name="Zelda Randomizer")
      await member.add_roles(zelda)
  else: 
    print("Member not found")

@client.event
async def on_raw_reaction_remove(payload):
  ChID = 852611783696711701 
  guild_id = payload.guild_id
  guild = discord.utils.find(lambda g : g.id == guild_id, client.guilds)
  
  if payload.channel_id != ChID:
        return
  
  member = await(await client.fetch_guild(payload.guild_id)).fetch_member(payload.user_id)
  if member is not None:
    if payload.emoji.name == "🏹":
      mh = discord.utils.get(guild.roles, name="Monster Hunter")
      await member.remove_roles(mh)
    if payload.emoji.name == "🇿":
      zelda = discord.utils.get(guild.roles, name="Zelda Randomizer")
      await member.remove_roles(zelda)
  else: 
    print("Member not found")


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))
    #assign_channel = discord.utils.get(client.get_all_channels(), id=852611783696711701)
    #await assign_channel.purge()
    #Text= ": Assign Role by reaction \n\n 🏹:    Monster Hunter \n 🇿:    Zelda Randomizer \n  \n____________ "
    #message = await assign_channel.send(Text)
    #await message.add_reaction("🏹")
    #await message.add_reaction('🇿')

@client.event
async def on_message(message):
  
  if message.author == client.user:
      return
  
  member = message.author
  dev_role = discord.utils.get(member.guild.roles, name="Dev Team")
  #Dev-Commands
  if message.content.startswith("!id"):
    if dev_role not in member.roles :
      await message.channel.send("You have no permission for this command, sorry.")
    else: 
      await message.channel.send("Channel ID: " + str(message.channel.id) +", User-ID: " + str(member.id))

  if message.channel.id == 851128177366925332 or message.channel.id == 769815939696033792:    
    if message.content.startswith("!hello"):
      await message.channel.send("Hello!")
      return
    
    if message.content.startswith("!quote"):
      quote = get_quote()
      await message.channel.send(quote)

    if message.content.startswith("!joke"):
      joke = get_joke()
      await message.channel.send(joke)

token = os.environ['TOKEN']

keep_alive()
client.run(token)




