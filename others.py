import discord
from discord.ext import commands
import time

class others(commands.Cog):
  """
  Outros comandos, nada fora do comum.

  """
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  #Comando de teste/ping
  @commands.command(name="ping")
  async def ping(self, ctx: commands.Context):
        """
        Pong!

        """
        start_time = time.time()
        
        message = await ctx.send("Testando ping...")
        
        typings = time.monotonic()
        await ctx.trigger_typing()
        typinge = time.monotonic()
        typingms = round((typinge - typings) * 1000)
        
        end_time = time.time()
        
        embed = discord.Embed(
          title="🏓 Pong",
            description=(f'Ping: **{round(self.bot.latency * 1000)}ms**\nAPI: **{round((end_time - start_time) * 1000)}ms**\nEscrevendo: **{typingms}ms**'),
            color=0xfbf9fa
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/933420163326423041/3507f298a2c64325b6843d4e7c6fe4b2.png?width=465&height=473")
        await ctx.send(embed=embed)
  
  @commands.command(name="git")
  async def git(self, ctx: commands.Context):
        """
        Código fonte do bot
        """
        await ctx.send("Pode revisar meu código fonte em: https://github.com/LeudoNeto/nezuko-s2")
  
  @commands.command(name="invite")
  async def invite(self, ctx: commands.Context):
      """
      Links para convidar o bot para um servidor

      """
      embed = discord.Embed(
          title="Quer me convidar a um servidor?",
          description="Aqui o link para isso:",
          color=0xfbf9fa,
      )
      embed.add_field(
          name="Link Nezuko s2",
          value="[Me convide](https://discord.com/api/oauth2/authorize?client_id=933420163326423041&permissions=0&scope=bot)",
          inline=True
      )
      #embed.set_image(url="pra quando eu fizer o banner"
      #)
      await ctx.send("Mandei os links de convite aqui e na sua DM", delete_after = 10)
      await ctx.author.send(embed=embed)
      await ctx.send(embed=embed)

  @commands.command(aliases=['si', 'server']) #Extraído de https://github.com/cree-py/RemixBot/blob/master/cogs/info.py
  async def serverinfo(self, ctx):
        '''Informação básica do servidor.'''
        guild = ctx.guild
        guild_age = (ctx.message.created_at - guild.created_at).days
        created_at = f"Servidor criado em {guild.created_at.strftime('%b %d %Y │ %H:%M')}.\nIsso foi há {guild_age} dias!"

        em = discord.Embed(description=created_at, color=0xfbf9fa)
        em.add_field(name='Dono', value=guild.owner, inline=False)
        em.add_field(name='Membros', value=len(guild.members), inline=False)
        em.add_field(name='Cargos', value=len(guild.roles))
        em.add_field(name='Canais de texto', value=len(guild.text_channels))
        em.add_field(name='Canais de voz', value=len(guild.voice_channels))


        em.set_thumbnail(url=None or guild.icon)
        em.set_author(name=guild.name, icon_url=None or guild.icon)
        await ctx.send(embed=em)

  #@commands.command(aliases=["topgg"])
  #async def vote(self, ctx: commands.Context):
  #    """
  #    Perfil da Nezuko s2 no top.gg
  #    """
  #    embed = discord.Embed(
  #        title="Me ajuda no top.gg",
  #        description="Considere votar em mim no top.gg plz",
  #        color=0xfbf9fa,
  #    )
  #    embed.add_field(
  #        name="Nezuko s2 no top.gg",
  #        value="[Top.gg](url quando eu fizer)",
  #        inline=True
  #    )
  #    embed.set_image(url="url do banner, qnd eu fizer"
  #    )
  #    await ctx.send("Enviando meu perfil no top.gg", delete_after = 10)
  #    await ctx.author.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(others(bot))