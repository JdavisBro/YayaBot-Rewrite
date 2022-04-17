
import discord
from discord.ext import commands

from . import embed as yayaembed
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
        return yayaembed.Embed(self.context.guild.id, bot=self.context.bot, title="YayaBot Help!", description=f"Say `{self.context.clean_prefix}help <command>` for more info on a command!", emoji="❔", timestamp=False)

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
        await paged.send_paged(self.get_destination(), embeds, self.context.author, expire=120)

    async def send_command_help(self,command):
        if not isinstance(command,commands.Cog):
            try:
                if not await command.can_run(self.context):
                    return
            except commands.CommandError:
                return

        emoji = (getattr(command, "emoji", False) or getattr(command, 'brief', '⚙️')) + " "
        title = f"Help for +EMOJIHERE+{command.qualified_name}" + (" cog" if isinstance(command,commands.Cog) else ' command')
        desc = f"Aliases: {', '.join(list(command.aliases))}" if command.aliases else ""
        embed = yayaembed.Embed(self.context.guild.id, bot=self.context.bot, title=title, description=desc, auto_timestamp=False)
        embed.title = title.replace("+EMOJIHERE+", emoji if embed.emojis else "")
        
        if not isinstance(command,commands.Cog):
            value = f"`{self.context.clean_prefix}{command.qualified_name}{(' ' + command.signature.replace('_',' ')    ) if command.signature else ' <subcommand>' if isinstance(command,commands.Group) else ''}`"
            embed.add_field(name="Usage",value=value, emoji=":screwdriver:")
        
        value = command.help.replace("[p]", self.context.clean_prefix) if command.help else '...'
        embed.add_field(name="Description", value=value, emoji=":scroll:", inline=False)
        
        if isinstance(command,commands.Group) or isinstance(command,commands.Cog):
            value = "**Subcommands**" if isinstance(command,commands.Group) else "**Commands**"
            embed.add_field(name="_ _", value=value, emoji="✴️", inline=False)
            for subcommand in await self.filter_commands(command.commands, sort=True): # This breaks if there are too many subcommands
                await self.create_help_field(self.context,embed,subcommand)
        
        await self.get_destination().send(embed=embed)

    async def send_group_help(self,group):
        await self.send_command_help(group)

    async def send_cog_help(self,cog):
        cog.aliases = None
        cog.help = cog.description
        cog.commands = cog.get_commands()
        await self.send_command_help(cog)
