import discord
from discord.ext import commands
from datetime import datetime

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="+", intents=intents, allowed_mentions=discord.AllowedMentions(roles=False, users=True, everyone=False, replied_user=True))
bot.launch_time = datetime.utcnow()

bot.load_extension('music')

#on_ready: Quando ativo e funcional, retornará mensagem falando que foi conectado
@bot.event
async def on_ready():
    print(f'Fui conectado como {bot.user}')
    await bot.change_presence(activity=discord.Game(name=f'+help | 🎵'))


#on message: Quando receber qualquer mensagem, retornará o usuário que mandou e a própria mensagem.
@bot.listen()
async def on_message(message):
    print(f'Mensagem de {message.author}: {message.content}')

bot.run('OTM0MTYyMzE0ODg4ODc2MDUz.YesEcw.dupaPbcNnrm9e-Im7Fq3dBB3ROE') #substitua seu-token-aqui pelo token do bot (Se não souber o que é ou como pega, leia o README.md)