import asyncio
from discord.ext import commands
import discord
import random
import asyncio

def random_love():
    love = random.randint(0, 100)
    return(love)

eightballresponses = [
    "Certamente.",
    "É definitivamente assim.",
    "Sem dúvida.",
    "Sim, definitivamente.",
    "Você pode confiar nisso.",
    "Ao meu ver, sim.",
    "É o mais provável.",
    "Sim.",
    "Minhas fontes dizem que sim.",
    "Não conte com isso",
    "Minha resposta é não.",
    "Minhas fontes dizem que não.",
    "Muito duvidoso."
]

class funny(commands.Cog):
  """
  Comandos muito divertidos e variados. Experimente todos!

  """
  def __init__(self, bot: commands.Bot):
    self.bot = bot
    
  @commands.Cog.listener()
  async def on_message(self, msg):
    self.bot.mention = ["nezuko", "nezukos2"]
    mention = self.bot.mention
    if msg.author.bot:
      return
    if any(word in msg.content.lower() for word in mention):
      emoji="❤"
      await msg.add_reaction(emoji)
      await self.bot.process_commands(msg)

  @commands.command(aliases=['lovecalculator','calculadoradoamor'])
  async def love(self, ctx, member: discord.Member=None):
    """
    Calcula tua possibilidade de romance com outro usuário
    """
    calc_love = random_love()
    if member is None:
      message = "Primeiro você precisa marcar alguém!"
      await ctx.reply(message, mention_author=False)
    elif member is ctx.author:
      message = "∞ [█████████████████████]\n**Você tem autoestima suficiente para se amar.**"
      await ctx.reply(message, mention_author=False)
    else:
      if calc_love == 0:
        love_messsage = f"{calc_love}% [ . . . . . . . . . . ]\n🚫 Não existe compatibilidade entre **{ctx.author.name}** e **{member.name}**"
      elif 1 <= calc_love <= 10:
        love_messsage = f"{calc_love}% [█ . . . . . . . . . ]\n🙅‍♀️ A compatibilidade entre **{ctx.author.name}** e **{member.name}** é muito baixa"
      elif 11 <= calc_love <= 20:
        love_messsage = f"{calc_love}% [█ . . . . . . . . . ]\n🤔 A compatibilidade entre **{ctx.author.name}** e **{member.name}** é bem baixa"
      elif 21 <= calc_love <= 30:
        love_messsage = f"{calc_love}% [██ . . . . . . . ]\n😶 A compatibilidade entre **{ctx.author.name}** e **{member.name}** é baixa"
      elif 31 <= calc_love <= 40:
        love_messsage = f"{calc_love}% [███ . . . . . . ]\n💌 A compatibilidade entre **{ctx.author.name}** e **{member.name}** é baixinha"
      elif 41 <= calc_love <= 50:
        love_messsage = f"{calc_love}% [████ . . . . . ]\n💑 A compatibilidade entre **{ctx.author.name}** e **{member.name}** é normal"
      elif 51 <= calc_love <= 60:
        love_messsage = f"{calc_love}% [█████ . . . . ]\n❤️ A compatibilidade entre **{ctx.author.name}** e **{member.name}** é razoável"
      elif 61 <= calc_love <= 70:
        love_messsage = f"{calc_love}% [██████ . . . ]\n💕 A compatibilidade entre **{ctx.author.name}** e **{member.name}** é decente"
      elif 71 <= calc_love <= 80:
        love_messsage = f"{calc_love}% [███████ . . ]\n💝 A compatibilidade entre **{ctx.author.name}** e **{member.name}** é bem decente"
      elif 81 <= calc_love <= 90:
        love_messsage = f"{calc_love}% [████████ . ]\n💘 A compatibilidade entre **{ctx.author.name}** e **{member.name}** é muito boa"
      elif 91 <= calc_love <= 99:
        love_messsage = f"{calc_love}% [█████████]\n💞 A compatibilidade entre **{ctx.author.name}** e **{member.name}** é incrivelmente boa"
      elif calc_love == 100:
        love_messsage = f"{calc_love}% [██████████]\n💖 A compatibilidade entre **{ctx.author.name}** e **{member.name}** é perfeita"
    embed = discord.Embed(description = f"{love_messsage}", color = 0xff9999)
    await ctx.reply(embed = embed, mention_author=False)

  #Usado de https://github.com/iiSakuu/Marshmallow
  @commands.command(aliases=['shipname'])
  async def ship(self, ctx, member : discord.Member, member2 : discord.Member = None):
        """
        Descubra como seria o nome do ship entre dois usuários 💘
        """

        if member2 is None:
            member2 = ctx.author

        if len(member.display_name) < 4:
            N = len(member.display_name) / 2

            firstmember = member.display_name
            firstship = firstmember[0:int(N)]

            secondmember = member2.display_name
            secondship = secondmember[0:4]

        elif len(member2.display_name) < 4 :
            N = len(member2.display_name) / 2

            firstmember = member.display_name
            firstship = firstmember[0:4]

            secondmember = member2.display_name
            secondship = secondmember[0:int(N)]

        else:

            firstmember = member.display_name
            firstship = firstmember[0:4]

            secondmember = member2.display_name
            secondship = secondmember[0:4]

        shipname = firstship + secondship

        embed = discord.Embed(
            description=f'{member.display_name} + {member2.display_name} = **{shipname}** 💘',
            colour=0xffb5f7
            )

        await ctx.send(embed=embed)

  @commands.command(name ='8ball', aliases=['ball8'])
  async def _8ball(self, ctx, *, question):
    """
    Faça uma pergunta e te darei a resposta.
    """
    eightball = discord.Embed(
        title='Sua pergunta:',
        description=f'{question}',
        color=discord.Colour.random()
        )
    eightball.add_field(
        name='Minha resposta:',
        value=f'||{(random.choice(eightballresponses))}||'
      )

    await ctx.reply('🎱 Sacudindo...', embed=eightball, mention_author=False)

  @commands.command(aliases=['choice','escolha'])
  async def choose(self, ctx, *, msg: str):
    """
    Mê dê opções e escolherei por você.

    """
    await ctx.reply(f'➡️ Eu escolho... **{(random.choice(msg.split()))}**', mention_author=False)

  @commands.command(aliases=['roll','dado'])
  async def dice(self, ctx):
    """
    Gira algunos dados.
    """
    message = await ctx.send("Quantos dados quer girar?")
    await message.add_reaction("1️⃣")
    await message.add_reaction("2️⃣")
    await message.add_reaction("3️⃣")

    check = lambda r, u: u == ctx.author and str(r.emoji) in "1️⃣2️⃣3️⃣"  # r=reaction, u=user

    dado_1 = random.randint(1,6)
    dado_2 = random.randint(1,6)
    dado_3 = random.randint(1,6)

    try:
        reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=10)
    except asyncio.TimeoutError:
        await message.edit(content="⌛ Demorou muito para decidir")
        return

    if str(reaction.emoji) == "1️⃣":
        embed = discord.Embed(title=f"Girou 1 dado:\n🎲 : {dado_1}", color=ctx.author.color)
        await ctx.send(embed=embed)
        return
    elif str(reaction.emoji) == "2️⃣":
        embed = discord.Embed(title=f"Girou 2 dados:\n🎲 : {dado_1} 🎲 : {dado_2}", color=ctx.author.color)
        await ctx.send(embed=embed)
        return
    elif str(reaction.emoji) == "3️⃣":
        embed = discord.Embed(title=f"Girou 3 dados:\n🎲 : {dado_1} 🎲 : {dado_2} 🎲 : {dado_3}", color=ctx.author.color)
        await ctx.send(embed=embed)
        return

async def setup(bot: commands.Bot):
  await bot.add_cog(funny(bot))