#pip install -U git+https://github.com/Rapptz/discord.py    no terminal
import discord
from discord.ext import commands

intents = discord.Intents.all()

class MyBot(commands.Bot):
    async def setup_hook(self):
        await self.load_extension('music')
        await self.load_extension('others')
        await self.load_extension('funny')
        await self.load_extension('help')

bot = MyBot(command_prefix="+", intents=intents, help_command=None, allowed_mentions=discord.AllowedMentions(roles=False, users=True, everyone=False, replied_user=True))

#on_ready: Quando ativo e funcional, retornará mensagem falando que foi conectado
@bot.event
async def on_ready():
    print(f'Fui conectado como {bot.user}')
    await bot.change_presence(activity=discord.Game(name=f'+help | Bot do GDG 🎵'))


#on message: Quando receber qualquer mensagem, retornará o usuário que mandou e a própria mensagem.
@bot.listen()
async def on_message(message):
    print(f'Mensagem de {message.author}: {message.content}')

bot.run('seu-token-aqui') #substitua seu-token-aqui pelo token do bot (Se não souber o que é ou como pega, leia o README.md)