# -*- coding: utf-8 -*-
from typing import List
import disnake
from disnake.ext import commands

from bot.bot import Bot

from modules.assets import *

class PollOption:
    
    def __init__(self, text: str, emoji: str) -> None:
        self.text = text
        self.emoji = emoji
        
    def __str__(self) -> str:
        return f"{self.emoji} {self.text}"


class PollEditor(disnake.ui.View):
    
    def __init__(self, intercation: disnake.ApplicationCommandInteraction):
        super().__init__(timeout=None)
        self.interaction = intercation
        self.editorEmbed = disnake.Embed(title="__**Poll creator**__")
        self.editorEmbed.add_field(name="__Target channel__",value="*Not selected yet*")
        self.poolEmbed: disnake.Embed = disnake.Embed(title="**__*Title*__**", description="*Message*")
        self.poolEmbed.add_field(name="__Options:__",value="*Not options yet*")
        self.options: List[PollOption] = []
        self.target: disnake.TextChannel | disnake.VoiceChannel | disnake.NewsChannel | disnake.Thread = None
        
    async def send(self):
        await self.interaction.edit_original_response(embeds = [self.editorEmbed, self.poolEmbed], view = self)
        
    async def update(self, interaction: disnake.MessageInteraction | disnake.ModalInteraction):
        self.image.disabled = False
        self.author.disabled = False
        self.footer.disabled = False
        self.confirm.disabled = (self.options == [] or self.target == None)
        await interaction.edit_original_response(embeds = [self.editorEmbed, self.poolEmbed], view = self)
        
    @disnake.ui.button(label="Set title and message", emoji="🔖", style=disnake.ButtonStyle.primary)
    async def set_title(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_modal(Embed(self))
        
    @disnake.ui.button(label="Set options", emoji="📑", style=disnake.ButtonStyle.primary)
    async def set_options(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_modal(Option(self))
        
    @disnake.ui.button(label="Images", emoji='🛤️', row=1, style=disnake.ButtonStyle.gray, disabled=True)
    async def image(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_modal(modal=Image(self))
        
    @disnake.ui.button(label="Author", emoji='👤', row=1, style=disnake.ButtonStyle.gray, disabled=True)
    async def author(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_modal(modal=Author(self))
    
    @disnake.ui.button(label="Footer", emoji='👤', row=1, style=disnake.ButtonStyle.gray, disabled=True)
    async def footer(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_modal(modal=Footer(self))
        
        
    @disnake.ui.string_select(placeholder="Color", min_values=1, max_values=1, options=color_dict.keys(), row=2)
    async def color(self, stringSelected: disnake.ui.StringSelect, interaction: disnake.MessageInteraction):
        await interaction.response.defer()
        self.color.placeholder = stringSelected.values[0]
        self.poolEmbed.color = color_dict.get(stringSelected.values[0])
        await self.update(interaction)
        
    @disnake.ui.channel_select(placeholder="Channels", min_values=1, max_values=1, row=3, channel_types=[disnake.ChannelType.text,disnake.ChannelType.voice,disnake.ChannelType.news,disnake.ChannelType.public_thread, disnake.ChannelType.private_thread, disnake.ChannelType.news_thread])
    async def channel(self, channelSelected: disnake.ui.ChannelSelect, interaction: disnake.MessageInteraction):
        await interaction.response.defer()
        self.target = channelSelected.values[0]
        self.editorEmbed.set_field_at(0, name="__Target channel__",value=self.target.mention, inline=False)
        await self.update(interaction)
        
    @disnake.ui.button(label="Send", emoji='📩', style=disnake.ButtonStyle.green, row=4, disabled=True)
    async def confirm(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.defer()
        msg = await self.target.send(embed=self.poolEmbed)
        for option in self.options:
            await msg.add_reaction(option.emoji)
        await self.interaction.edit_original_response(embed=disnake.Embed(description=f"Poll send [here]({msg.jump_url})!", color=disnake.Colour.green()), view=None)
        await interaction.delete_original_response(delay=3)
        
    @disnake.ui.button(label="Cancel", emoji='❌', style=disnake.ButtonStyle.red, row=4)
    async def clear(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.defer() 
        self.stop()
        await interaction.delete_original_response()
        
class Embed(disnake.ui.Modal):
    
    def __init__(self, pollEditor: PollEditor) -> None:
        self.pollEditor = pollEditor
        super().__init__(title="Poll creator", components=[
            disnake.ui.TextInput(label="Title", custom_id="title", placeholder="The poll's title", value=pollEditor.poolEmbed.title if pollEditor.poolEmbed else None, max_length="50"),
            disnake.ui.TextInput(label="Message", custom_id="msg", placeholder="The poll's message", value=pollEditor.poolEmbed.description if pollEditor.poolEmbed else None, required=False, style=disnake.TextInputStyle.paragraph),
        ])
   
    async def callback(self, interaction: disnake.ModalInteraction) -> None:
        await interaction.response.defer(with_message=False)
        if self.pollEditor.poolEmbed:  
            self.pollEditor.poolEmbed.title = interaction.text_values.get('title')
            self.pollEditor.poolEmbed.description = interaction.text_values.get('msg')
        else:
            self.pollEditor.poolEmbed = disnake.Embed(title=interaction.text_values.get('title'), description=interaction.text_values.get('title'))
        await self.pollEditor.update(interaction)
        
class Image(disnake.ui.Modal):
    
    def __init__(self, pollEditor: PollEditor) -> None:
        self.pollEditor = pollEditor
        super().__init__(title="Embed creation", components=[
            disnake.ui.TextInput(label='Image', custom_id='image', placeholder="The poll's image URL", required=False, value=self.pollEditor.poolEmbed.image.url if self.pollEditor.poolEmbed.image else None),
            disnake.ui.TextInput(label='Thumbnail', custom_id='thumbnail', placeholder="The poll's thumbnail url", required=False, value=self.pollEditor.poolEmbed.thumbnail.url if self.pollEditor.poolEmbed.thumbnail else None)
            ])
       
    async def callback(self, interaction: disnake.ModalInteraction) -> None:
        await interaction.response.defer(with_message=False)
        self.pollEditor.poolEmbed.set_image(interaction.text_values.get('image'))
        self.pollEditor.poolEmbed.set_thumbnail(interaction.text_values.get('thumbnail'))
        await self.pollEditor.update(interaction)
        
         
class Author(disnake.ui.Modal):
    
    def __init__(self, pollEditor: PollEditor) -> None:
        self.pollEditor = pollEditor
        super().__init__(title="Embed details", components=[
            disnake.ui.TextInput(label="Author name", custom_id='author', placeholder="The embed's author name", value=self.pollEditor.poolEmbed.author.name if self.pollEditor.poolEmbed.author else None, max_length=256),
            disnake.ui.TextInput(label="Author URL", custom_id='author_url', placeholder="The author's URL", value=self.pollEditor.poolEmbed.author.url if self.pollEditor.poolEmbed.author else None, required=False),
            disnake.ui.TextInput(label="Author icon", custom_id='author_icon', placeholder="The author's icon URL", value=self.pollEditor.poolEmbed.author.icon_url if self.pollEditor.poolEmbed.author else None, required=False),
            ])
       
    async def callback(self, interaction: disnake.ModalInteraction) -> None:
        await interaction.response.defer(with_message=False)
        self.pollEditor.poolEmbed.set_author(
            name = interaction.text_values.get('author'),
            url = interaction.text_values.get('author_url'),
            icon_url = interaction.text_values.get('author_icon')
        )
        await self.pollEditor.update(interaction)  
        
class Footer(disnake.ui.Modal):
    
    def __init__(self, pollEditor: PollEditor) -> None:
        self.pollEditor = pollEditor
        super().__init__(title="Embed details", components=[
            disnake.ui.TextInput(label="Footer text", custom_id='footer_text', placeholder="The footer's text", value=self.pollEditor.poolEmbed.footer.text if self.pollEditor.poolEmbed.footer else None, max_length=2048),
            disnake.ui.TextInput(label="Footer icon", custom_id='footer_icon', placeholder="The footer's icon URL", value=self.pollEditor.poolEmbed.footer.icon_url if self.pollEditor.poolEmbed.footer else None, required=False)
            ])
       
    async def callback(self, interaction: disnake.ModalInteraction) -> None:
        await interaction.response.defer(with_message=False)
        self.pollEditor.poolEmbed.set_footer(
            text = interaction.text_values.get('footer_text'),
            icon_url = interaction.text_values.get('footer_icon')
        )
        await self.pollEditor.update(interaction)  
        
class Option(disnake.ui.Modal):
    
    def __init__(self, pollEditor: PollEditor) -> None:
        self.pollEditor = pollEditor
        super().__init__(title="Poll creator", components=[
            disnake.ui.TextInput(label="Options (one by line, max 26)",custom_id="options", placeholder="Option n°1\nOption n°2\n...", value="\n".join([option.text for option in pollEditor.options]) if pollEditor.options else None,style=disnake.TextInputStyle.paragraph)
        ])
   
    async def callback(self, interaction: disnake.ModalInteraction) -> None:
        await interaction.response.defer(with_message=False)
        for i,option in enumerate(interaction.text_values.get('options').splitlines()):
            if i >= 26:
                break
            self.pollEditor.options.append(PollOption(option, alphabet[i]))
        self.pollEditor.poolEmbed.set_field_at(0, name="__Options:__",value="\n".join([str(option) for option in self.pollEditor.options]))
        await self.pollEditor.update(interaction)
        

   
class Poll(commands.Cog):
    def __init__(self, bot):
        """Initialize the cog"""
        self.bot: Bot = bot

    @commands.slash_command(
        name="poll",
        description="Create a reaction poll to be sent in a channel",
        dm_permission=False,
    )
    async def embed(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer(ephemeral=True)
        PC = PollEditor(inter)
        await PC.send()
        
def setup(bot: commands.InteractionBot):
    bot.add_cog(Poll(bot))
