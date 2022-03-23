
import discord
from discord.ext import commands

from . import embed
from . import paged

__all__ = (
    "HelpCommand",
)

class HelpCommand(commands.HelpCommand):
    async def create_help_field(self, ctx, embed, command):
        if command.help:
            description = (command.help[:command.help.find("\n")+1] if '\n' in command.help else command.help)
            if len(description) > 200:
                description = description[:197] + "..."
        else:
            description = "..."
        if command.brief:
            emote = command.brief
        elif command.name == "help":
            emote = ":question:"
        else:
            emote = None
        embed.add_field(name=command.name, value=description, emoji=emote, inline=True)

    async def new_help_page(self):
        return embed.Embed(self.context.guild.id, bot=self.context.bot, title="YayaBot Help!", description=f"Say `{self.context.prefix}help <command>` for more info on a command!", emoji="❔")

    async def send_bot_help(self, mapping):
        embeds = []
        page = await self.new_help_page()
        for cog, commands in mapping.items():
            commands = await self.filter_commands(commands)
            if not commands:
                continue
            if len(page.fields) >= 24: # If no space for commands or no space at all
                embeds.append(page)
                page = await self.new_help_page()
            cogName = getattr(cog, 'qualified_name', 'Other')
            cogDesc = '\n> '+ getattr(cog, "description", '...') if not cogName == "Other" else "> Other commands that don't fit into a category."
            cogEmoji = "> " + getattr(cog, 'emoji', "⚙️")
            page.add_field(name=f"**{cogName}**", value=cogDesc, emoji=cogEmoji, inline=False) # Add cog field
            for command in commands:
                await self.create_help_field(self.context, page, command)
                if command != commands[-1] and len(page.fields) == 25: # If not the last command and new page is required
                    embeds.append(page)
                    page = await self.new_help_page()
                    page.add_field(name=f"**{cogName}**", value=cogDesc, emoji=cogEmoji, inline=False) # Add cog field
        embeds.append(page)
        await paged.send_paged(self.get_destination(), embeds, self.context.author)

    async def send_command_help(self,command):
        style = fEmbeds.fancyEmbeds.getActiveStyle(self, self.context.guild.id)
        useEmoji = fEmbeds.fancyEmbeds.getStyleValue(self, self.context.guild.id, style, "emoji")

        if not useEmoji:
            emojia = ""
            emojib = ""
        else:
            emojia = ":screwdriver: "
            emojib = ":scroll: "

        if not isinstance(command,commands.Cog):
            try:
                await command.can_run(self.context)
            except:
                return
        embed = fEmbeds.fancyEmbeds.makeEmbed(self, self.context.guild.id, embTitle=f"Help for {command.qualified_name}" + (" cog" if isinstance(command,commands.Cog) else ' command'), desc=(f"Aliases: {', '.join(list(command.aliases))}" if command.aliases else ""), useColor=1, b=bot)
        if not isinstance(command,commands.Cog):
            embed.add_field(name=f"{emojia}Usage",value=f"`{self.clean_prefix}{command.qualified_name}{(' ' + command.signature.replace('_',' ')    ) if command.signature else ' <subcommand>' if isinstance(command,commands.Group) else ''}`")
        embed.add_field(name=f"{emojib}Description",value=(command.help.replace("[p]",self.clean_prefix) if command.help else '...'),inline=False)
        if isinstance(command,commands.Group) or isinstance(command,commands.Cog):
            embed.add_field(name="———————",value="**Subcommands**" if isinstance(command,commands.Group) else "**Commands**",inline=False)
            for subcommand in await self.filter_commands(command.commands, sort=True):
                embed = await self.create_help_field(self.context,embed,subcommand,useEmoji)
        await self.get_destination().send(embed=embed)

    async def send_group_help(self,group):
        await self.send_command_help(group)

    async def send_cog_help(self,cog):
        cog.aliases = None
        cog.help = cog.description
        cog.commands = cog.get_commands()
        await self.send_command_help(cog)
