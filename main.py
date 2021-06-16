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

client = commands.Bot(command_prefix = "!")



#Courage quote function
def get_quote():
  response = requests.get("https://zenquotes.io/api/random")
  json_data = json.loads(response.text)
  quote = json_data[0]["q"] + " -" + json_data[0]["a"]
  return quote
###
#joke function
def get_joke():
  response = requests.get("https://official-joke-api.appspot.com/random_joke")
  json_data = json.loads(response.text)
  joke = json_data["setup"]+ " -" + json_data["punchline"]
  return joke
###
#Role assign function
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
###
#Role remove function
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
###
#
@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))
    #assign_channel = discord.utils.get(client.get_all_channels(), id=852611783696711701)
    #await assign_channel.purge()
    #Text= ": Assign Role by reaction \n\n 🏹:    Monster Hunter \n 🇿:    Zelda Randomizer \n  \n____________ "
    #message = await assign_channel.send(Text)
    #await message.add_reaction("🏹")
    #await message.add_reaction('🇿')
###
#


@commands.command(name='joke', aliases=['witz'], pass_context=True)
@commands.has_permissions(manage_guild=True)
async def _joke(ctx):
  channel = ctx.channel
  if channel.id == 851128177366925332:
    joke = get_joke()
    await ctx.send(joke)

@commands.command(name='quote', pass_context=True)
@commands.has_permissions(manage_guild=True)
async def _quote(ctx):
  channel = ctx.channel
  if channel.id == 851128177366925332:
    quote = get_quote()
    await ctx.send(quote)



client.add_command(_joke)
client.add_command(_quote)

token = os.environ['TOKEN']

keep_alive()
client.run(token)




