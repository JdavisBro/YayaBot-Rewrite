import time
from typing import Optional

import discord
from discord.ext import commands

from . import timehelpers

__all__ = (
    "send_paged",
    "Paged",
)

async def send_paged(ctx: discord.abc.Messageable, embeds, author, selected=0, do_footer=True, expire: Optional[float]=None, delete_button=True):
    if len(embeds) > 1:
        embeds[selected].set_footer(text=f"Page {selected+1} of {len(embeds)}" + (" • Buttons expire after 2 minutes" if expire else ""))
        view = Paged(embeds, author, selected, do_footer, delete_button=delete_button, expire=expire)
        await view.button_checks()
        return await ctx.send(embed=embeds[selected],view=view)
    elif embeds:
        await ctx.send(embed=embeds[0])

class ChoosePageModal(discord.ui.Modal, title="Jump To Page"):
    number = discord.ui.TextInput(label="Page Number:")

    def __init__(self, view):
        self.view = view
        super().__init__()

    async def on_submit(self, interaction):
        try:
            num = int(self.number.value)
        except ValueError:
            await interaction.response.send_message(f"Page `{self.number.value}` doesn't exist.", ephemeral=True)
        else:
            if self.view.selected == num-1:
                await interaction.response.send_message(f"Already on page {num}!", ephemeral=True)
            else:
                await self.view.set_page(num-1, interaction)

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
            for item in (self.filler_one, self.filler_two, self.change_page_two, self.delete):
                self.remove_item(item)
        else:
            self.remove_item(self.change_page_one)

    async def interaction_check(self, interaction):
        if interaction.user == self.author:
            return True
        else:
            await interaction.response.send_message("You're not allowed to do that.", ephemeral=True)
            return False

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
        if page >= len(self.embeds):
            page = len(self.embeds)-1
        elif page < 0:
            page = 0
        if self.selected == page:
            return
        self.selected = page
        await self.button_checks()
        if self.do_footer:
            text = f"Page {self.selected+1} of {len(self.embeds)}"
            if self.expire:
                text += f" • Buttons expire after 2 minutes"
            self.embeds[self.selected].set_footer(text=text)
        self.timeout = self.expireDefault
        await interaction.response.edit_message(embed=self.embeds[self.selected],view=self)

    @discord.ui.button(label="<<", row=0)
    async def begin(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.set_page(0, interaction)

    @discord.ui.button(label="<", row=0)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.set_page(self.selected-1, interaction)

    @discord.ui.button(label=">", row=0)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.set_page(self.selected+1, interaction)

    @discord.ui.button(label=">>", row=0)
    async def last(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.set_page(len(self.embeds)-1, interaction)

    @discord.ui.button(emoji="🔢", row=0)
    async def change_page_one(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ChoosePageModal(self))

    @discord.ui.button(label=" ", row=1, disabled=True)
    async def filler_one(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass

    @discord.ui.button(label=" ", row=1, disabled=True)
    async def filler_two(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass

    @discord.ui.button(emoji="🔢", row=1)
    async def change_page_two(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ChoosePageModal(self))

    @discord.ui.button(label="X", style=discord.ButtonStyle.danger, row=1)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        msg = await interaction.message.delete()
        self.stop()
