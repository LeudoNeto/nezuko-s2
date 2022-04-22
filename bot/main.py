import discord
from discord.ext import commands
from datetime import datetime
import os
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.members = True

#Baseado em https://gist.github.com/EvieePy/d78c061a4798ae81be9825468fe146be
def get_prefix(bot, message):
    """Lista com mais de um prefixo possível por servidor."""

    #Você também pode usar espaços nos prefixos
    prefixes = ['ns2', 'nezuko ', '+']

    #Checa se a mensagem foi no server ou no direct.
    if not message.guild:
        #Permite apenas que o prefixo '+' seja usado nos direct.
        return '+'

    # Se foi no server, permite que o usuário mencione o bot ou use algum dos prefixos dentro da lista.
    return commands.when_mentioned_or(*prefixes)(bot, message)

bot = commands.Bot(command_prefix=get_prefix, intents=intents, allowed_mentions=discord.AllowedMentions(roles=False, users=True, everyone=False, replied_user=True))
bot.launch_time = datetime.utcnow()

#bot.load_extension('music') posteriormente

#on_ready: Quando ativo e funcional, retornará mensagem falando que foi conectado
@bot.event
async def on_ready():
    print(f'Fui conectado como {bot.user}')
    await bot.change_presence(activity=discord.Game(name=f'+help | Bot do GDG'))


#on message: Quando receber qualquer mensagem, retornará o usuário que mandou e a própria mensagem.
@bot.listen()
async def on_message(message):
    print(f'Mensagem de {message.author}: {message.content}')

load_dotenv()
bot.run(os.getenv('Token')) #na pasta .env substitua seu-token-aqui pelo token do bot (Se não souber o que é ou como pega, leia o README.md)