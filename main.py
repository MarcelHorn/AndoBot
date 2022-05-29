import discord
import requests
import json
import youtube_dl

import asyncio
import functools
import itertools
import math
import random
import os

from async_timeout import timeout
from keep_alive import keep_alive
from discord.ext import commands
import music

client = commands.Bot(command_prefix = "!", description='AndoBot, folgende Befehle sind mit !<Befehl> verfügbar. Bitte beachten, dass diese nur in den jeweiligen Kanälen funktionieren.')

BOT_ID = 838820360153595924
BOT_CHANNEL_ID = 851128177366925332
MUSIC_CHANNEL_ID = 855150898380275753
ASSIGN_ROLE_MESSAGE_ID = 852646486037495900

###
#Role assign function
@client.event
async def on_raw_reaction_add(payload):
  guild_id = payload.guild_id
  guild = discord.utils.find(lambda g : g.id == guild_id, client.guilds)
  if payload.message_id != ASSIGN_ROLE_MESSAGE_ID:
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
###
#Role remove function
@client.event
async def on_raw_reaction_remove(payload):
  guild_id = payload.guild_id
  guild = discord.utils.find(lambda g : g.id == guild_id, client.guilds)
  if payload.message_id != ASSIGN_ROLE_MESSAGE_ID:
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
###
#
@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))
    

youtube_dl.utils.bug_reports_message = lambda: ''




class ApiCommands(commands.Cog, name = "bot-channel"):
#Courage quote function
  def __init__(self, bot: commands.Bot):
        self.bot = bot
        
  def get_quote(self):
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]["q"] + " -" + json_data[0]["a"]
    return quote
###
  def get_fact(self, isGerman):
    if isGerman:
      response = requests.get("https://uselessfacts.jsph.pl/random.json?language=de")
    else: 
      response = requests.get("https://uselessfacts.jsph.pl/random.json?language=en")
    json_data = json.loads(response.text)
    fact = json_data["text"]
    return fact
#joke function
  #def get_joke(self):
    #response = requests.get("https://official-joke-api.appspot.com/random_joke")
    #json_data = json.loads(response.text)
    #joke = json_data["setup"]+ " -" + json_data["punchline"]
    #return joke

  #@commands.command(name='joke', aliases=['witz'], pass_context=True)
  #async def _joke(self, ctx):
    #"""Erzählt einen sehr guten Witz. (Englisch)"""
  
    #apiCommand = self.bot.get_cog('bot-channel')
    #if apiCommand is not None:
      #channel_id = ctx.channel.id
      #if channel_id == BOT_CHANNEL_ID:
        #joke = self.get_joke()
        #await ctx.send(joke)
    

  @commands.command(name='quote', pass_context=True)
  async def _quote(self, ctx):
    """Gibt ein aufheiterndes Zitat ab. (Englisch)"""

    apiCommand = self.bot.get_cog('bot-channel')
    if apiCommand is not None:
      channel_id = ctx.channel.id
      if channel_id == BOT_CHANNEL_ID:
        quote = self.get_quote()
        await ctx.send(quote)

  @commands.command(name='fakt', pass_context=True)
  async def _fakt(self, ctx):
    """Gibt dir mehr unnötiges Wissen"""

    apiCommand = self.bot.get_cog('bot-channel')
    if apiCommand is not None:
      channel_id = ctx.channel.id
      if channel_id == BOT_CHANNEL_ID:
        fact = self.get_fact(isGerman = True)
        await ctx.send(fact)

  @commands.command(name='fact', pass_context=True)
  async def _fact(self, ctx):
    """Gibt dir mehr unnötiges Wissen"""

    apiCommand = self.bot.get_cog('bot-channel')
    if apiCommand is not None:
      channel_id = ctx.channel.id
      if channel_id == BOT_CHANNEL_ID:
        fact = self.get_fact(isGerman = False)
        await ctx.send(fact)

@client.event
async def on_message(message):
    if message.author.id == BOT_ID:
            return
    if "morning" in message.content:
      if "good morning" in message.content:
        await message.channel.send("Not good! Not morning!")
        return
      await message.channel.send("It's not morning!")
    await client.process_commands(message);



client.add_cog(music.Musik(client))
client.add_cog(ApiCommands(client))
#client.add_command(_quote)

token = os.environ['TOKEN']

keep_alive()
client.run(token)