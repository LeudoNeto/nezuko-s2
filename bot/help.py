import discord
from discord.ext import commands

class HelpCommand(commands.HelpCommand):

    def footer(self):
      return f"""{self.invoked_with}[comando] para informações específicas.
      
{self.invoked_with}[categoria] para informações da categoria, ou 
aperte algum dos botões:"""

    def get_command_signature(self, command):
      return f"```fix\n{command.qualified_name} {command.signature}\n```"
    
    async def send_cog_help(self, cog):
      embed = discord.Embed(title=f"__**Comandos {cog.qualified_name}**__", color = discord.Color.from_rgb(244,127,255))
      if cog.description:
        embed.description = cog.description
      
      filtered = await self.filter_commands(cog.get_commands(), sort=True)
      for command in filtered:
        embed.add_field(name=command.qualified_name, value=command.short_doc or "Sem descrição")
      
      embed.set_footer(text=self.footer())
      await self.get_destination().send(embed=embed)

    async def send_command_help(self, command):
      embed = discord.Embed(title=command.qualified_name, color = discord.Color.from_rgb(244,127,255))
      if command.help:
        embed.description = command.help
      
      embed.add_field(name="Uso", value=self.get_command_signature(command))

      await self.get_destination().send(embed=embed)

    async def send_bot_help(self, mapping):
      embed = discord.Embed(color=discord.Color.from_rgb(244,127,255))
      embed.set_author(
        name=f" Menu de ajuda ",
        icon_url = "https://cdn.discordapp.com/avatars/933420163326423041/3507f298a2c64325b6843d4e7c6fe4b2.png?width=465&height=473")
      #embed.set_image(url="url do banner, quando eu fizer")
      #description = f"*Se tiver algum problema peça ajuda em [url qnd eu fizer]"
      for cog, commands in mapping.items():
        if not cog:
          continue
        filtered = await self.filter_commands(commands, sort = True)
        if filtered:
          value = "\t".join(f"`{i.name}`" for i in commands)
          embed.add_field(name = cog.qualified_name, value = value, inline=False)
      embed.set_footer(text=self.footer())
      await self.get_destination().send(embed=embed)

async def setup(bot):
  bot.help_command = HelpCommand() 