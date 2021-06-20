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

client = commands.Bot(command_prefix = "!", description='Folgende Befehle sind mit !<Befehl> verfügbar. Bitte beachten, dass diese nur in den jeweiligen Kanälen funktionieren.')


BOT_CHANNEL_ID = 762336254133534731
MUSIC_CHANNEL_ID = 855884940524781588
ASSIGN_ROLE_MESSAGE_ID = 855889788477243402

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
    if payload.emoji.name == "🐉":
      mh = discord.utils.get(guild.roles, name="Monster Hunter")
      await member.add_roles(mh)
    if payload.emoji.name == "🎲":
      community = discord.utils.get(guild.roles, name="StruggleDudes")
      await member.add_roles(community)
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
    if payload.emoji.name == "🐉":
      mh = discord.utils.get(guild.roles, name="Monster Hunter")
      await member.remove_roles(mh)
    if payload.emoji.name == "🎲":
      community = discord.utils.get(guild.roles, name="StruggleDudes")
      await member.remove_roles(community)
  else: 
    print("Member not found")
###
#
@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))
    
    
# Silence useless bug reports messages
youtube_dl.utils.bug_reports_message = lambda: ''

class VoiceError(Exception):
    pass
class YTDLError(Exception):
    pass
class YTDLSource(discord.PCMVolumeTransformer):
    YTDL_OPTIONS = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
    }

    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }

    ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)

    def __init__(self, ctx: commands.Context, source: discord.FFmpegPCMAudio, *, data: dict, volume: float = 0.5):
        super().__init__(source, volume)

        self.requester = ctx.author
        self.channel = ctx.channel
        self.data = data

        self.uploader = data.get('uploader')
        self.uploader_url = data.get('uploader_url')
        date = data.get('upload_date')
        self.upload_date = date[6:8] + '.' + date[4:6] + '.' + date[0:4]
        self.title = data.get('title')
        self.thumbnail = data.get('thumbnail')
        self.description = data.get('description')
        self.duration = self.parse_duration(int(data.get('duration')))
        self.tags = data.get('tags')
        self.url = data.get('webpage_url')
        self.views = data.get('view_count')
        self.likes = data.get('like_count')
        self.dislikes = data.get('dislike_count')
        self.stream_url = data.get('url')

    def __str__(self):
        return '**{0.title}** von **{0.uploader}**'.format(self)

    @classmethod
    async def create_source(cls, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None):
        loop = loop or asyncio.get_event_loop()

        partial = functools.partial(cls.ytdl.extract_info, search, download=False, process=False)
        data = await loop.run_in_executor(None, partial)

        if data is None:
            raise YTDLError('Konnte nichts passendes finden: `{}`'.format(search))

        if 'entries' not in data:
            process_info = data
        else:
            process_info = None
            for entry in data['entries']:
                if entry:
                    process_info = entry
                    break

            if process_info is None:
                raise YTDLError('Konnte nichts passendes finden: `{}`'.format(search))

        webpage_url = process_info['webpage_url']
        partial = functools.partial(cls.ytdl.extract_info, webpage_url, download=False)
        processed_info = await loop.run_in_executor(None, partial)

        if processed_info is None:
            raise YTDLError('Fehlgeschlagen: `{}`'.format(webpage_url))

        if 'entries' not in processed_info:
            info = processed_info
        else:
            info = None
            while info is None:
                try:
                    info = processed_info['entries'].pop(0)
                except IndexError:
                    raise YTDLError('Keine passende Übereinstimmung: `{}`'.format(webpage_url))

        return cls(ctx, discord.FFmpegPCMAudio(info['url'], **cls.FFMPEG_OPTIONS), data=info)

    @staticmethod
    def parse_duration(duration: int):
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        duration = []
        if days > 0:
          if days == 1:
            duration.append('{} Tag'.format(days))
          else:
            duration.append('{} Tage'.format(days))
        if hours > 0:
          if hours == 1:
            duration.append('{} Stunde'.format(hours))
          else:
            duration.append('{} Stunden'.format(hours))
        if minutes > 0:
          if minutes == 1:
            duration.append('{} Minute'.format(minutes))
          else:
            duration.append('{} Minuten'.format(minutes))
        if seconds > 0:
          if seconds == 1:
            duration.append('{} Sekunde'.format(seconds))
          else:
            duration.append('{} Sekunden'.format(seconds))

        return ', '.join(duration)
class Song:
    __slots__ = ('source', 'requester')

    def __init__(self, source: YTDLSource):
        self.source = source
        self.requester = source.requester

    def create_embed(self):
        embed = (discord.Embed(title='Spielt gerade',
                               description='```css\n{0.source.title}\n```'.format(self),
                               color=discord.Color.blurple())
                 .add_field(name='Dauer', value=self.source.duration)
                 .add_field(name='Angefordert von', value=self.requester.mention)
                 .add_field(name='Uploader', value='[{0.source.uploader}]({0.source.uploader_url})'.format(self))
                 .add_field(name='URL', value='[Klick]({0.source.url})'.format(self))
                 .set_thumbnail(url=self.source.thumbnail))

        return embed


class SongQueue(asyncio.Queue):
    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    def __iter__(self):
        return self._queue.__iter__()

    def __len__(self):
        return self.qsize()

    def clear(self):
        self._queue.clear()

    def shuffle(self):
        random.shuffle(self._queue)

    def remove(self, index: int):
        del self._queue[index]


class VoiceState:
    def __init__(self, bot: commands.Bot, ctx: commands.Context):
        self.bot = bot
        self._ctx = ctx

        self.current = None
        self.voice = None
        self.next = asyncio.Event()
        self.songs = SongQueue()

        self._loop = False
        self._volume = 0.5
        self.skip_votes = set()

        self.audio_player = bot.loop.create_task(self.audio_player_task())

    def __del__(self):
        self.audio_player.cancel()

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, value: bool):
        self._loop = value

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value: float):
        self._volume = value

    @property
    def is_playing(self):
        return self.voice and self.current

    async def audio_player_task(self):
        while True:
            self.next.clear()

            if not self.loop:
                # Try to get the next song within 3 minutes.
                # If no song will be added to the queue in time,
                # the player will disconnect due to performance
                # reasons.
                try:
                    async with timeout(180):  # 3 minutes
                        self.current = await self.songs.get()
                except asyncio.TimeoutError:
                    self.bot.loop.create_task(self.stop())
                    return

            self.current.source.volume = self._volume
            self.voice.play(self.current.source, after=self.play_next_song)
            await self.current.source.channel.send(embed=self.current.create_embed())

            await self.next.wait()

    def play_next_song(self, error=None):
        if error:
            raise VoiceError(str(error))

        self.next.set()

    def skip(self):
        self.skip_votes.clear()

        if self.is_playing:
            self.voice.stop()

    async def stop(self):
        self.songs.clear()

        if self.voice:
            await self.voice.disconnect()
            self.voice = None


class Musik(commands.Cog, name = "jukebox"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, ctx: commands.Context):
        state = self.voice_states.get(ctx.guild.id)
        if not state:
            state = VoiceState(self.bot, ctx)
            self.voice_states[ctx.guild.id] = state

        return state

    def cog_unload(self):
        for state in self.voice_states.values():
            self.bot.loop.create_task(state.stop())

    def cog_check(self, ctx: commands.Context):
        if not ctx.guild:
            raise commands.NoPrivateMessage('Dieser Command kann nicht in Privatnachrichten ausgeführt werden.')

        return True

    async def cog_before_invoke(self, ctx: commands.Context):
        ctx.voice_state = self.get_voice_state(ctx)

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        print('Ein Fehler ist aufgetreten: {}'.format(str(error)) + "\nUser: " + ctx.author.name + "\nChannel: " + ctx.channel.name)
        #await ctx.send('Ein Fehler ist aufgetreten: {}'.format(str(error)))

    @commands.command(name='join', invoke_without_subcommand=True)
    async def _join(self, ctx: commands.Context):
        """Schiebt den Bot in deinen Voice Channel.
        """
        
        if ctx.channel.id != MUSIC_CHANNEL_ID:
          return
        destination = ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return

        ctx.voice_state.voice = await destination.connect()

    @commands.command(name='summon')
    @commands.has_permissions(manage_guild=True)
    async def _summon(self, ctx: commands.Context, *, channel: discord.VoiceChannel = None):
        """Zwingt den Bot in deinen Sprachchannel (Mod).
        """
        
        if not channel and not ctx.author.voice:
            raise VoiceError('You are neither connected to a voice channel nor specified a channel to join.')

        destination = channel or ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return

        ctx.voice_state.voice = await destination.connect()

    @commands.command(name='leave', aliases=['disconnect'])
    async def _leave(self, ctx: commands.Context):
        """Bot verlässt den Sprachkanal, Playlist wird geleert."""
        if ctx.channel.id != MUSIC_CHANNEL_ID:
          return
        if not ctx.voice_state.voice:
            return await ctx.send('Der Bot ist nicht in einem Sprachkanal.')

        await ctx.voice_state.stop()
        del self.voice_states[ctx.guild.id]

    # @commands.command(name='volume')
    # async def _volume(self, ctx: commands.Context, *, volume: int):
    #     """Setzt die Lautstä."""

    #     if not ctx.voice_state.is_playing:
    #         return await ctx.send('Nothing being played at the moment.')

    #     if 0 > volume > 100:
    #         return await ctx.send('Volume must be between 0 and 100')

    #     ctx.voice_state.volume = volume / 100
    #     await ctx.send('Volume of the player set to {}%'.format(volume))

    @commands.command(name='now', aliases=['current', 'playing'])
    async def _now(self, ctx: commands.Context):
        """Zeigt das derzeit abgespielte Lied an."""
        if ctx.channel.id != MUSIC_CHANNEL_ID:
          return
        await ctx.send(embed=ctx.voice_state.current.create_embed())

    @commands.command(name='pause')
    async def _pause(self, ctx: commands.Context):
        """Pausiert die Audiowiedergabe."""
        if ctx.channel.id != MUSIC_CHANNEL_ID:
          return
        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
            ctx.voice_state.voice.pause()
            await ctx.message.add_reaction('⏯')

    @commands.command(name='resume')
    async def _resume(self, ctx: commands.Context):
        """Setzt die Audiowiedergabe fort."""
        if ctx.channel.id != MUSIC_CHANNEL_ID:
          return
        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_paused():
            ctx.voice_state.voice.resume()
            await ctx.message.add_reaction('⏯')

    @commands.command(name='stop')
    async def _stop(self, ctx: commands.Context):
        """Stoppt die Musik und leert die Playlist."""
        if ctx.channel.id != MUSIC_CHANNEL_ID:
          return
        ctx.voice_state.songs.clear()

        if ctx.voice_state.is_playing:
            ctx.voice_state.voice.stop()
            await ctx.message.add_reaction('⏹')

    @commands.command(name='skip')
    async def _skip(self, ctx: commands.Context):
        """Stimme für einen Skip ab. Der "Requester" kann sofort skippen.
        
        """
        if ctx.channel.id != MUSIC_CHANNEL_ID:
          return
        if not ctx.voice_state.is_playing:
            return await ctx.send('Es wird keine Musik abgespielt...')

        voter = ctx.message.author
        if voter == ctx.voice_state.current.requester:
            await ctx.message.add_reaction('⏭')
            ctx.voice_state.skip()

        elif voter.id not in ctx.voice_state.skip_votes:
            ctx.voice_state.skip_votes.add(voter.id)
            total_votes = len(ctx.voice_state.skip_votes)

            if total_votes >= 3:
                await ctx.message.add_reaction('⏭')
                ctx.voice_state.skip()
            else:
                await ctx.send('Abstimmung zum skippen, aktuell bei **{}/3**'.format(total_votes))

        else:
            await ctx.send('Du hast bereits abgestimmt.')

    @commands.command(name='queue')
    async def _queue(self, ctx: commands.Context, *, page: int = 1):
        """Zeigt die Playlist.

        
        """
        if ctx.channel.id != MUSIC_CHANNEL_ID:
          return
        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('Leer.')

        items_per_page = 10
        pages = math.ceil(len(ctx.voice_state.songs) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue = ''
        for i, song in enumerate(ctx.voice_state.songs[start:end], start=start):
            queue += '`{0}.` [**{1.source.title}**]({1.source.url})\n'.format(i + 1, song)

        embed = (discord.Embed(description='**{} Song:**\n\n{}'.format(len(ctx.voice_state.songs), queue))
                 .set_footer(text='Seite {}/{}'.format(page, pages)))
        await ctx.send(embed=embed)

    @commands.command(name='shuffle')
    async def _shuffle(self, ctx: commands.Context):
        """Mischt die Playlist."""
        if ctx.channel.id != MUSIC_CHANNEL_ID:
          return
        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('leer.')

        ctx.voice_state.songs.shuffle()
        await ctx.message.add_reaction('✅')

    @commands.command(name='remove')
    async def _remove(self, ctx: commands.Context, index: int):
        """Entfernt Song aus Playlist (Index angeben)."""
        if ctx.channel.id != MUSIC_CHANNEL_ID:
          return
        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('leer.')

        ctx.voice_state.songs.remove(index - 1)
        await ctx.message.add_reaction('✅')

    @commands.command(name='loop')
    async def _loop(self, ctx: commands.Context):
        """Packt den aktuellen Song in Schleife.

        Nochmal ausgeben, um die Schleife zu beenden.
        """
        if ctx.channel.id != MUSIC_CHANNEL_ID:
          return
        if not ctx.voice_state.is_playing:
            return await ctx.send('Es wird gerade nichts abgespielt.')

        # Inverse boolean value to loop and unloop.
        ctx.voice_state.loop = not ctx.voice_state.loop
        await ctx.message.add_reaction('✅')

    @commands.command(name='play')
    async def _play(self, ctx: commands.Context, *, url: str):
        """Fügt ein Song in die Playlist ein (Youtube Link angeben!).
        Keine Livestream-URLs angeben, andernfalls muss der Bot aus dem Voice Channel gekickt und wieder eingeladen werden!
        """
        if ctx.channel.id != MUSIC_CHANNEL_ID:
          return
        if not ctx.voice_state.voice:
            await ctx.invoke(self._join)

        async with ctx.typing():
            try:
                source = await YTDLSource.create_source(ctx, url, loop=self.bot.loop)
            except YTDLError as e:
                await ctx.send('Fehler bei der Anfrage: {}'.format(str(e)))
            else:
                song = Song(source)

                await ctx.voice_state.songs.put(song)
                await ctx.send('Eingereiht {}'.format(str(source)))

    @_join.before_invoke
    @_play.before_invoke
    async def ensure_voice_state(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandError('Du befindest dich in keinem Sprachkanal.')

        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                raise commands.CommandError('Bot ist bereits in einem Sprachkanal.')


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
#joke function
  def get_joke(self):
    response = requests.get("https://official-joke-api.appspot.com/random_joke")
    json_data = json.loads(response.text)
    joke = json_data["setup"]+ " -" + json_data["punchline"]
    return joke

  @commands.command(name='joke', aliases=['witz'], pass_context=True)
  async def _joke(self, ctx):
    """Erzählt einen sehr guten Witz. (Englisch)"""
  
    apiCommand = self.bot.get_cog('bot-channel')
    if apiCommand is not None:
      channel_id = ctx.channel.id
      if channel_id == BOT_CHANNEL_ID:
        joke = self.get_joke()
        await ctx.send(joke)
    

  @commands.command(name='quote', pass_context=True)
  async def _quote(self, ctx):
    """Gibt ein aufheiterndes Zitat ab. (Englisch)"""

    apiCommand = self.bot.get_cog('bot-channel')
    if apiCommand is not None:
      channel_id = ctx.channel.id
      if channel_id == BOT_CHANNEL_ID:
        quote = self.get_quote()
        await ctx.send(quote)

  @commands.command(name='msg_c', pass_context=True, hidden=True)
  @commands.has_permissions(manage_guild=True)
  async def _msg_c(self, ctx, msg: str, chnl :str):
    channel = discord.utils.get(ctx.guild.channels, name=chnl)
    if channel is not None:
      await channel.send(msg)
      return
    await ctx.send("Channel nicht gefunden!")


  @commands.command(name='msg_u', pass_context=True, hidden=True)
  @commands.has_permissions(manage_guild=True)
  async def _msg_u(self, ctx, msg: str, user : int):
    user = await client.fetch_user(user)
    if user is not None:
      await user.send(msg)
    else: 
      await ctx.send("Name nicht gefunden!")

client.add_cog(Musik(client))
client.add_cog(ApiCommands(client))
#client.add_command(_quote)

token = os.environ['TOKEN']

keep_alive()
client.run(token)




