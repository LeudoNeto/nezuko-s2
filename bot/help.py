import discord
from discord.ext import commands
from discord.ui import Select,View
from config import bot_prefix

class HelpCommand(commands.HelpCommand):
    
    async def send_cog_help(self, cog):
        embed = discord.Embed(title=f"__**Comandos {cog.qualified_name}**__", color = discord.Color.from_rgb(244,127,255))
        if cog.description:
            embed.description = cog.description
      
        filtered = await self.filter_commands(cog.get_commands(), sort=True)
        for command in filtered:
            if cog.qualified_name == 'music':
                embed.add_field(name=f'{command.qualified_name}/{command.aliases[-1]}', value=command.short_doc or "Sem descrição")
            else:
                embed.add_field(name=command.qualified_name, value=command.short_doc or "Sem descrição")
        
        embed.set_footer(text=f"{bot_prefix}{self.invoked_with}[comando] para informações específicas.")
        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command):
        embed = discord.Embed(title=command.qualified_name, color = discord.Color.from_rgb(244,127,255))
        if command.help:
            embed.description = command.help
        
        embed.add_field(name="Uso:", value=f"```fix\n{bot_prefix}{command.qualified_name} {command.signature}\n```")
        embed.add_field(name="Alternativos:", value = "\t".join(f"`{bot_prefix}{aliase}`" for aliase in command.aliases), inline=False)

        await self.get_destination().send(embed=embed)

    async def send_bot_help(self, mapping):

        view = View()
        selection = Select(placeholder='Escolha uma categoria', options=[discord.SelectOption(label='Music',emoji='🎵',description='Comandos de música'),discord.SelectOption(label='Funny',emoji='😂',description='Comandos divertidos'),discord.SelectOption(label='Others',emoji='⚙',description='Comandos diversos')])

        view.add_item(selection)

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
                value = ""
                if cog.qualified_name == 'music':
                    value = "em inglês:\n"
                value += "\t".join(f"`{i.name}`" for i in commands)
                if cog.qualified_name == 'music':
                    value += '\n em português:\n' + "\t".join(f"`{i.aliases[-1]}`" for i in commands)
                embed.add_field(name = cog.qualified_name, value = value, inline=False)
        embed.set_footer(text=f"{bot_prefix}{self.invoked_with}[comando] para informações específicas.\n\n{bot_prefix}{self.invoked_with}[categoria] para informações da categoria, ou\nselecione-a abaixo:")
        
        await self.get_destination().send(embed=embed, view=view)

        async def select_callback(interaction):
            if selection.values[0] == 'Music':
                cog = list(mapping.keys())[0]

                embed = discord.Embed(title=f"__**Comandos {cog.qualified_name}**__", color = discord.Color.from_rgb(244,127,255))
                if cog.description:
                    embed.description = cog.description
            
                filtered = await self.filter_commands(cog.get_commands(), sort=True)
                for command in filtered:
                    embed.add_field(name=f'{command.qualified_name}/{command.aliases[-1]}', value=command.short_doc or "Sem descrição")

                await interaction.response.edit_message(embed=embed)

            if selection.values[0] == 'Funny':
                cog = list(mapping.keys())[1]

                embed = discord.Embed(title=f"__**Comandos {cog.qualified_name}**__", color = discord.Color.from_rgb(244,127,255))
                if cog.description:
                    embed.description = cog.description
            
                filtered = await self.filter_commands(cog.get_commands(), sort=True)
                for command in filtered:
                    embed.add_field(name=command.qualified_name, value=command.short_doc or "Sem descrição")

                await interaction.response.edit_message(embed=embed)

            if selection.values[0] == 'Others':
                cog = list(mapping.keys())[2]

                embed = discord.Embed(title=f"__**Comandos {cog.qualified_name}**__", color = discord.Color.from_rgb(244,127,255))
                if cog.description:
                    embed.description = cog.description
            
                filtered = await self.filter_commands(cog.get_commands(), sort=True)
                for command in filtered:
                    embed.add_field(name=command.qualified_name, value=command.short_doc or "Sem descrição")

                await interaction.response.edit_message(embed=embed)

        selection.callback = select_callback

async def setup(bot):
    bot.help_command = HelpCommand() 