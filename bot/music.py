import asyncio
import functools
import itertools
import math
import random
import urllib
import discord
import youtube_dl
from discord.ext import commands
import re
from discord.ui import Button, View
from pytube import Playlist
from config import bot_prefix

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
        return '**`{0.title}`** by **`{0.uploader}`**'.format(self)

    @classmethod
    async def create_source(cls, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None):
        loop = loop or asyncio.get_event_loop()

        partial = functools.partial(cls.ytdl.extract_info, search, download=False, process=False)
        data = await loop.run_in_executor(None, partial)

        if data is None:
            raise YTDLError('Couldn\'t find anything that matches `{}`'.format(search))

        if 'entries' not in data:
            process_info = data
        else:
            process_info = None
            for entry in data['entries']:
                if entry:
                    process_info = entry
                    break

            if process_info is None:
                raise YTDLError('Couldn\'t find anything that matches `{}`'.format(search))

        webpage_url = process_info['webpage_url']
        partial = functools.partial(cls.ytdl.extract_info, webpage_url, download=False)
        processed_info = await loop.run_in_executor(None, partial)

        if processed_info is None:
            raise YTDLError('Couldn\'t fetch `{}`'.format(webpage_url))

        if 'entries' not in processed_info:
            info = processed_info
        else:
            info = None
            while info is None:
                try:
                    info = processed_info['entries'].pop(0)
                except IndexError:
                    raise YTDLError('Couldn\'t retrieve any matches for `{}`'.format(webpage_url))

        return cls(ctx, discord.FFmpegPCMAudio(info['url'], **cls.FFMPEG_OPTIONS), data=info)

    @staticmethod
    def parse_duration(duration: int):
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        duration = []
        if days > 0:
            duration.append('{} dias'.format(days))
        if hours > 0:
            duration.append('{} horas'.format(hours))
        if minutes > 0:
            duration.append('{} minutos'.format(minutes))
        if seconds > 0:
            duration.append('{} segundos'.format(seconds))
        else:
            duration.append('AO VIVO')

        return ', '.join(duration)


class Song:
    __slots__ = ('source', 'requester')

    def __init__(self, source: YTDLSource):
        self.source = source
        self.requester = source.requester

    def create_embed(self):
        em = (discord.Embed(description='```css\n{0.source.title}\n```'.format(self), color=discord.Color.from_rgb(244,127,255))
                 .add_field(name='?????? Dura????o:', value=f"`{self.source.duration}`", inline = True)
                 .add_field(name='???? Artista:', value='[{0.source.uploader}]({0.source.uploader_url})'.format(self))
                 .set_thumbnail(url=self.source.thumbnail)
                 .set_footer(text=f"Solicitado por {self.requester.name}", icon_url=f"{self.requester.avatar}"))
        em.set_author(
            name=f" Tocando agora: ",
            icon_url = "https://images-ext-2.discordapp.net/external/wCoxd5EKV3CrmZ6HlEaIS0F-Ggsdk9MyzoLFRVFefsY/https/images-ext-1.discordapp.net/external/DkPCBVBHBDJC8xHHCF2G7-rJXnTwj_qs78udThL8Cy0/%253Fv%253D1/https/cdn.discordapp.com/emojis/859459305152708630.gif")
        return em


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

    def move(self, index1: int, index2:int):
        if index1 == index2:
            raise ValueError('Voc?? n??o est?? trocando o lugar da m??sica')
        if not (0 < index1 <= self.__len__()) or not (0 < index2 <= (self.__len__()+1)):
            raise IndexError('Pelo menos um dos n??meros que voc?? forneceu n??o equivalem a alguma m??sica da lista')
        if index1 < index2:
            self._queue.insert(index2,self._queue[index1-1])
            del self._queue[index1-1]
        else:
            self._queue.insert(index2-1,self._queue[index1-1])
            del self._queue[index1]


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
                self.current = await self.songs.get()
                    
            self.current.source.volume = self._volume
            self.voice.play(self.current.source, after=self.play_next_song)

            sair = Button(label='Sair', style=discord.ButtonStyle.red, emoji='????')
            pausar = Button(label='Pausar', emoji='???')
            retomar = Button(label='Retomar', style=discord.ButtonStyle.green, emoji='???')
            pular = Button(label='Pular', style=discord.ButtonStyle.blurple, emoji='???')
            lista = Button(label='Lista', style=discord.ButtonStyle.blurple, emoji='????')

            self.sair_button = sair
            self.pausar_button = pausar
            self.retomar_button = retomar
            self.pular_button = pular
            self.lista_button = lista

            async def sair_callback(interaction):

                if not interaction.user.voice or not interaction.user.voice.channel or interaction.user.voice.channel != self._ctx.guild.me.voice.channel:
                    return await interaction.response.send_message('Voc?? n??o est?? no meu canal de voz', ephemeral=True)

                dest = self._ctx.author.voice.channel
                em = discord.Embed(title=f":zzz: Desconectado de  {dest}", color = interaction.user.color)
                em.set_footer(text=f"Solicitado por {interaction.user}") 
                await interaction.response.edit_message(embed=self.current.create_embed(),view=None)
                await interaction.channel.send(embed=em)
                await self._ctx.voice_state.stop()

            async def pausar_callback(interaction):
                self._ctx.message.guild.voice_client.pause()
                atual = self.current.create_embed()
                atual.set_footer(text=atual.footer.text+f"\nM??sica pausada por {interaction.user.name}", icon_url=f"{interaction.user.avatar}")
                await interaction.response.edit_message(embed=atual,view=self.viewcomresume)

            async def retomar_callback(interaction):
                self._ctx.message.guild.voice_client.resume()
                atual = self.current.create_embed()
                atual.set_footer(text=atual.footer.text+f"\nM??sica retomada por {interaction.user.name}", icon_url=f"{interaction.user.avatar}")
                await interaction.response.edit_message(embed=atual,view=self.viewcompause)
            
            async def pular_callback(interaction):
                await interaction.response.edit_message(embed=self.current.create_embed(),view=None)
                await interaction.message.add_reaction('???')
                em = discord.Embed(title=f"M??sica pulada ???", color = interaction.user.color)
                em.set_footer(text=f"por {interaction.user}") 
                await interaction.channel.send(embed=em)
                self._ctx.voice_state.skip()
            
            async def lista_callback(interaction):
                page = 1
                if len(self._ctx.voice_state.songs) == 0:
                    return await interaction.response.send_message('A fila est?? vazia.', ephemeral=True)

                items_per_page = 10
                pages = math.ceil(len(self._ctx.voice_state.songs) / items_per_page)

                start = (page - 1) * items_per_page
                end = start + items_per_page

                queue = ''
                for i, song in enumerate(self._ctx.voice_state.songs[start:end], start=start):
                    queue += '`{0}.` [**{1.source.title}**]({1.source.url})\n`{1.source.duration}`\n\n'.format(i + 1, song)

                embed = (discord.Embed(description='**{} Tracks:**\n\n{}'.format(len(self._ctx.voice_state.songs), queue))
                     .set_footer(text='Vendo p??gina {}/{}'.format(page, pages)))
                await interaction.message.add_reaction('????')
                await interaction.response.send_message(embed=embed, ephemeral=True)
            
            self.sair_button.callback = sair_callback
            self.pausar_button.callback = pausar_callback
            self.retomar_button.callback = retomar_callback
            self.pular_button.callback = pular_callback
            self.lista_button.callback = lista_callback

            self.viewcompause = View()
            self.viewcomresume = View()

            self.viewcompause.add_item(sair)
            self.viewcompause.add_item(pausar)
            self.viewcompause.add_item(pular)
            self.viewcompause.add_item(lista)

            self.viewcomresume.add_item(sair)
            self.viewcomresume.add_item(retomar)
            self.viewcomresume.add_item(pular)
            self.viewcomresume.add_item(lista)

            self.now_playing = await self.current.source.channel.send(embed=self.current.create_embed(),view=self.viewcompause)

            await self.next.wait()

            before = (discord.Embed(description='```css\n{0.source.title}\n```'.format(self.current), color=discord.Color.from_rgb(244,127,255))
                 .set_thumbnail(url=self.current.source.thumbnail)
                 .set_footer(text=f"Solicitado por {self.current.requester.name}", icon_url=f"{self.current.requester.avatar}"))
            before.set_author(
                name=f"???? Tocou antes: ")

            await self.now_playing.edit(embed=before,view=None)

            self.current = None

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


class music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_states = {}


    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Music Loaded")


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
            raise commands.NoPrivateMessage('Esse comando n??o pode ser usado em DMs.')

        return True

    async def cog_before_invoke(self, ctx: commands.Context):
        ctx.voice_state = self.get_voice_state(ctx)

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send('Um erro ocorreu: {}'.format(str(error)))

    @commands.command(help="Entra no canal de voz.", name="join", aliases = ["j","entrar"], invoke_without_subcommand=True)
    async def _join(self, ctx: commands.Context):

        destination = ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)          

        ctx.voice_state.voice = await destination.connect()

        em = discord.Embed(title=f"??? Me conectei no canal  {destination}", color = ctx.author.color)
        em.set_footer(text=f"Solicitado por {ctx.author.name}")  
        await ctx.send(embed=em)

    @commands.command(help="Chama o bot para um canal", name="summon", aliases = ["s","chamar"])
    async def _summon(self, ctx: commands.Context, *, channel: discord.VoiceChannel = None):

        if not channel and not ctx.author.voice:
            raise VoiceError('Voc?? n??o est?? em um canal de voz / n??o especificou o canal para eu me unir.')

        destination = channel or ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            em = discord.Embed(title=f"??? Fui chamado para o canal  {destination}", color = ctx.author.color)
            em.set_footer(text=f"Solicitado por {ctx.author.name}")
            await ctx.send(embed=em)

        ctx.voice_state.voice = await destination.connect()

    @commands.command(help="Sai do canal de voz.", name="leave", aliases = ["l","sair"])
    async def _leave(self, ctx: commands.Context):

        if not ctx.voice_state.voice:
            return await ctx.send('N??o estou conectado a nenhum canal de voz.')

        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send('Voc?? n??o est?? conectado em nenhum canal de voz.')

        if ctx.author.voice.channel != ctx.guild.me.voice.channel:
            return await ctx.send("Voc?? n??o est?? no meu canal de voz.")

        dest = ctx.author.voice.channel
        await ctx.voice_state.stop()
        em = discord.Embed(title=f":zzz: Desconectado de  {dest}", color = ctx.author.color)
        em.set_footer(text=f"Solicitado por {ctx.author.name}")            
        await ctx.send(embed=em)


# Pesquisa o que voc?? quiser no youtube
    @commands.command(help="Procura por algo no youtube", name="search", aliases= ["syt","procurar","pesquisar"])
    async def syt(self, ctx, *, search):
        async with ctx.typing():
            query_string = urllib.parse.urlencode({
                    "search_query": search
            })
            html_content = urllib.request.urlopen(
                "http://youtube.com/results?" + query_string
            )
        
            search_content = re.findall(r"watch\?v=(\S{11})", html_content.read().decode())
            yt_search = "http://youtube.com/watch?v=" + search_content[0]
        
        await ctx.send("???? **Foi isso que encontrei no Youtube. ?? o que buscava?** ????????????????\n" + yt_search)



    @commands.command(help="Ajusta o volume da minha m??sica.", name="volume", aliases = ["vol"])
    async def _volume(self, ctx: commands.Context, *, volume:int):

        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send('Voc?? n??o est?? conectado em nenhum canal de voz.')

        if not ctx.voice_state.is_playing:
            return await ctx.send('N??o estou em nenhum canal de voz.')

        if ctx.author.voice.channel != ctx.guild.me.voice.channel:
            return await ctx.send("Voc?? n??o est?? no mesmo canal de voz que eu.")

        if volume > 200:
            return await ctx.send(':x: O volume deve estar entre **0 e 200**')

        ctx.voice_client.source.volume = volume / 75
        em = discord.Embed(title=f"Volume ajustado para **`{volume}%`**", color = ctx.author.color)
        em.set_footer(text=f"Solicitado por {ctx.author.name}")    
        await ctx.send(embed=em)

    @commands.command(help="Mostra o que est?? tocando atualmente.", name="now", aliases=['n','np', 'current', 'playing', 'agora', 'tocando'])
    async def _now(self, ctx: commands.Context):

        if not ctx.voice_state.voice:
            if ctx.voice_state.current:
                await ctx.send('N??o estou tocando nada no momento, mas ao sair eu estava tocando:')
                em = (discord.Embed(description='```css\n{0.source.title}\n```'.format(ctx.voice_state.current), color=discord.Color.from_rgb(244,127,255))
                    .add_field(name='?????? Dura????o:', value=f"`{ctx.voice_state.current.source.duration}`", inline = True)
                    .add_field(name='???? Artista:', value='[{0.source.uploader}]({0.source.uploader_url})'.format(ctx.voice_state.current))
                    .set_thumbnail(url=ctx.voice_state.current.source.thumbnail)
                    .set_footer(text=f"Solicitado por {ctx.voice_state.current.requester.name}", icon_url=f"{ctx.voice_state.current.requester.avatar}"))
                await ctx.send(embed=em)
            else:
                await ctx.send('Eu n??o estou tocando nada.')

        else:
            if ctx.voice_state.current:
                await ctx.send(embed=ctx.voice_state.current.create_embed())
            else:
                await ctx.send('Eu n??o estou tocando nada.')

    @commands.command(name='pause', help='Pausa a m??sica.', aliases=["pa","pausar"])
    async def _pause(self, ctx):
        server = ctx.message.guild
        voice_channel = server.voice_client

        if ctx.author.voice.channel != ctx.guild.me.voice.channel:
            return await ctx.send("Voc?? n??o est?? no meu canal de voz.")

        voice_channel.pause()

        atual = ctx.voice_state.current.create_embed()
        atual.set_footer(text=atual.footer.text+f"\nM??sica pausada por {ctx.author.name}", icon_url=f"{ctx.author.avatar}")
        await ctx.voice_state.now_playing.edit(embed=atual,view=ctx.voice_state.viewcomresume)

    @commands.command(name='resume', help="Retoma o que estava tocando", aliases=["r","continuar","retomar"])
    async def _resume(self, ctx):
        server = ctx.message.guild
        voice_channel = server.voice_client

        if ctx.author.voice.channel != ctx.guild.me.voice.channel:
            return await ctx.send("Voc?? n??o est?? no meu canal de voz.")


        voice_channel.resume()
        
        atual = ctx.voice_state.current.create_embed()
        atual.set_footer(text=atual.footer.text+f"\nM??sica retomada por {ctx.author.name}", icon_url=f"{ctx.author.avatar}")
        await ctx.voice_state.now_playing.edit(embed=atual,view=ctx.voice_state.viewcompause)

    @commands.command(name="stop", help="Para a lista de reprodu????o.", aliases=["st","parar"])
    async def _stop(self, ctx):

        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send('Voc?? n??o est?? conectado a nenhum canal de voz.')

        if ctx.author.voice.channel != ctx.guild.me.voice.channel:
            return await ctx.send("Voc?? n??o est?? no meu canal de voz.")

        em = discord.Embed(title=f"???? Ok, n??o tocarei mais m??sicas.", color = ctx.author.color)
        em.set_footer(text=f"Solicitado por {ctx.author.name}", icon_url=f"{ctx.author.avatar}")
        await ctx.send(embed=em)
        await ctx.voice_state.stop()

    @commands.command(name='skip', help="Pula a m??sica atual.", aliases=["sk","pular"])
    async def _skip(self, ctx: commands.Context):

        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send('Voc?? n??o est?? conectado a nenhum canal de voz.')

        if not ctx.voice_state.is_playing:
            return await ctx.send('N??o estou reproduzindo nada...')

        if ctx.author.voice.channel != ctx.guild.me.voice.channel:
            return await ctx.send("Voc?? na?? est?? no meu canal de voz.")

        voter = ctx.message.author
        if voter == ctx.voice_state.current.requester:
            await ctx.message.add_reaction('???')
            ctx.voice_state.skip()

        elif voter.id != ctx.voice_state.current.requester:
            if ctx.voice_state.current.requester not in ctx.author.voice.channel.members:
                await ctx.message.add_reaction('???')
                ctx.voice_state.skip()

        elif voter.id not in ctx.voice_state.skip_votes:
            ctx.voice_state.skip_votes.add(voter.id)
            total_votes = len(ctx.voice_state.skip_votes)

            if total_votes >= 3:
                await ctx.message.add_reaction('???')
                ctx.voice_state.skip()
            else:
                await ctx.send('Voto adicionado, atualmente em **{}/3**'.format(total_votes))

        else:
            await ctx.send('Voc?? j?? votou para pular essa m??sica.')

    @commands.command(name='queue', help="Mostra a fila de reprodu????o atual.", aliases=["q","lista","fila"])
    async def _queue(self, ctx: commands.Context, *, page: int = 1):

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('A fila est?? vazia.')

        items_per_page = 10
        pages = math.ceil(len(ctx.voice_state.songs) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue = ''
        for i, song in enumerate(ctx.voice_state.songs[start:end], start=start):
            queue += '`{0}.` [**{1.source.title}**]({1.source.url})\n`{1.source.duration}`\n\n'.format(i + 1, song)

        embed = (discord.Embed(description='**{} Tracks:**\n\n{}'.format(len(ctx.voice_state.songs), queue))
                 .set_footer(text='Vendo p??gina {}/{}'.format(page, pages)))
        await ctx.send(embed=embed)

    @commands.command(name='shuffle', help="Randomiza a lista de reprodu????o.", aliases=["sh"])
    async def _shuffle(self, ctx: commands.Context):


        if ctx.author.voice.channel != ctx.guild.me.voice.channel:
            return await ctx.send("Voc?? n??o est?? no meu canal de voz.")

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('Lista vazia.')

        ctx.voice_state.songs.shuffle()
        await ctx.message.add_reaction('???')

    @commands.command(name='remove', help="Remove uma can????o da fila de reprodu????o", aliases=["re","remover"])
    async def _remove(self, ctx: commands.Context, index: int):


        if ctx.author.voice.channel != ctx.guild.me.voice.channel:
            return await ctx.send("Voc?? n??o est?? no meu canal de voz.")

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('Lista vazia.')

        ctx.voice_state.songs.remove(index - 1)
        await ctx.message.add_reaction('???')

    @commands.command(name='move', help="Move uma can????o da fila de reprodu????o", aliases=["mo","mover"])
    async def _move(self, ctx: commands.Context, index1: int, index2: int):


        if ctx.author.voice.channel != ctx.guild.me.voice.channel:
            return await ctx.send("Voc?? n??o est?? no meu canal de voz.")

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send('Lista vazia.')

        ctx.voice_state.songs.move(index1,index2)
        await ctx.message.add_reaction('???')
        

    @commands.command(name='play', help="Adiciona uma m??sica na fila para tocar.", aliases=["p","reproduzir","tocar"])
    async def _play(self, ctx: commands.Context, *, search: str = None):

        if not search:
            em = discord.Embed(title = 'Talvez voc?? n??o saiba usar o bot ainda', description= f"Envie {bot_prefix}help para receber mais ajuda", color = ctx.author.color)
            em.add_field(name= "Como usar:", value=f"{bot_prefix}{ctx.invoked_with} [Pesquisa ou URL]\n Com isso irei procurar o que voc?? mandou e adicionar ?? fila.\n")
            em.add_field(name= "Exemplo:", value=f"{bot_prefix}{ctx.invoked_with} `Hey Jude` - Procura por Hey Jude no You Tube e pega a primeira m??sica encontrada, colocando-a na fila",inline=False)
            
            nameandaliases = ["play","p","reproduzir","tocar"]
            nameandaliases.remove(ctx.invoked_with)
            em.add_field(name="Alternativos:", value=f'{bot_prefix}{nameandaliases[0]}, {bot_prefix}{nameandaliases[1]} ou {bot_prefix}{nameandaliases[2]}',inline=False)

            await ctx.send(embed=em)

        else:

            if not ctx.voice_state.voice:
                ctx.voice_state.current = None
                await ctx.invoke(self._join)

            if 'playlist' in search:
                playlist = Playlist(search)
                url = playlist.video_urls[0]
                try:
                    source = await YTDLSource.create_source(ctx, url, loop=self.bot.loop)
                except YTDLError as e:
                    await ctx.send('**`ERRO`**: {}'.format(str(e)))
                else:
                    song = Song(source)

                    await ctx.voice_state.songs.put(song)
                em = discord.Embed(title = 'Adicionado ?? fila',description=f':headphones: Foram adicionadas `{playlist.length} m??sicas` da playlist `{playlist.title}` ?? lista', color = ctx.author.color)
                em.set_footer(text=f"Solicitado por {ctx.author.name}", icon_url=f"{ctx.author.avatar}")
                await ctx.send(embed=em)

                for url in list(playlist.video_urls)[1:]:
                    try:
                        source = await YTDLSource.create_source(ctx, url, loop=self.bot.loop)
                    except YTDLError as e:
                        await ctx.send('**`ERRO`**: {}'.format(str(e)))
                    else:
                        song = Song(source)

                        await ctx.voice_state.songs.put(song)

            else:
                async with ctx.typing():
                    try:
                        source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop)
                    except YTDLError as e:
                        await ctx.send('**`ERRO`**: {}'.format(str(e)))
                    else:
                        song = Song(source)

                        await ctx.voice_state.songs.put(song)

                        em = discord.Embed(title = 'Adicionado ?? fila',description=f':headphones: Adicionado ?? fila: {str(source)}', color = ctx.author.color)
                        em.set_footer(text=f"Solicitado por {ctx.author.name}", icon_url=f"{ctx.author.avatar}")
                        await ctx.send(embed=em)

    @_join.before_invoke
    @_play.before_invoke
    async def ensure_voice_state(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandError('Voc?? n??o est?? em nenhum canal de voz.')

        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                raise commands.CommandError("J?? estou em um canal de voz diferente.")

async def setup(bot):
    await bot.add_cog(music(bot))