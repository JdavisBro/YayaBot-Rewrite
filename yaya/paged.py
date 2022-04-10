import time
from typing import Optional

import discord
from discord.ext import commands

from . import timehelpers

__all__ = (
    "send_paged",
    "Paged",
)

async def send_paged(ctx: discord.abc.Messageable, embeds, author, selected=0, do_footer=True, expire: Optional[float]=None):
    embeds[selected].set_footer(footer_text=f"Page {selected+1} of {len(embeds)}")
    view = Paged(embeds, author, selected, do_footer, expire=expire)
    await view.button_checks()
    return await ctx.send(embed=embeds[selected],view=view)

class Paged(discord.ui.View):
    def __init__(self, embeds, author, selected=0, do_footer=True, delete_button=True, expire: Optional[float]=None):
        super().__init__(timeout=expire)
        self.embeds = embeds
        self.selected = selected
        self.do_footer = do_footer
        self.author = author
        if expire:
            self.expire = True
        else:
            self.expire = False
        self.expireDefault = expire
        if not delete_button:
            self.remove_item(delete)

    async def button_checks(self):
        if self.selected == 0:
            self.begin.disabled = self.previous.disabled = True
        else:
            self.begin.disabled = self.previous.disabled = False
        if self.selected == len(self.embeds)-1:
            self.last.disabled = self.next.disabled = True
        else:
            self.last.disabled = self.next.disabled = False

    async def set_page(self, page, interaction):
        if interaction.user != self.author:
            return
        if page >= len(self.embeds):
            page = len(self.embeds)-1
        elif page < 0:
            page = 0
        if self.selected == page:
            return
        self.selected = page
        await self.button_checks()
        text = f"Page {self.selected+1} of {len(self.embeds)}"
        if self.expire:
            text += f" • Buttons expire after 2 minutes"
        self.embeds[self.selected].set_footer(footer_text=text)
        self.timeout = self.expireDefault
        await interaction.response.edit_message(embed=self.embeds[self.selected],view=self)

    @discord.ui.button(label="<<")
    async def begin(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.set_page(0, interaction)

    @discord.ui.button(label="<")
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.set_page(self.selected-1, interaction)

    @discord.ui.button(label=">")
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.set_page(self.selected+1, interaction)

    @discord.ui.button(label=">>")
    async def last(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.set_page(len(self.embeds)-1, interaction)

    @discord.ui.button(label="X", style=discord.ButtonStyle.red)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        msg = await interaction.message.delete()
        self.stop()
