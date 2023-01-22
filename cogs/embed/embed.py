# -*- coding: utf-8 -*-
import ast
from typing import List
import disnake
from disnake.ext import commands

from bot.bot import Bot

from modules.assets import *

        
        #TODO: add limit check !
    
class EmbedEditor(disnake.ui.View):
    
    editorEmbed = disnake.Embed(title="Embed creation", color=disnake.Colour.teal(), description="> TODO")
        
    def __init__(self, interaction: disnake.ApplicationCommandInteraction):
        super().__init__(timeout=None)
        self.current_embed_n: int = None
        self.warning_message: str | None = None
        self.interaction = interaction
        self.cmdEmbeds: List[disnake.Embed] = []
        self.selected_color: disnake.Colour = disnake.Colour.default()
        self.targets: List[disnake.TextChannel | disnake.VoiceChannel | disnake.NewsChannel | disnake.Thread] | List[disnake.User | disnake.Role] = []
        
    @property
    def embeds(self) -> List[disnake.Embed]:
        self.editorEmbed.clear_fields()
        self.editorEmbed.add_field(name="__*Target(s)*__", value=("> "+"\n> ".join([target.mention for target in self.targets]) if self.targets else "*no target*"), inline=False)
        if self.warning_message:
            self.editorEmbed.add_field(name="⚠️", value=self.warning_message, inline=False)
        return [self.editorEmbed]+self.cmdEmbeds
        
    async def send(self):
        await self.interaction.edit_original_response(embeds = self.embeds, view=self)
        
    async def update(self, interaction: disnake.MessageInteraction | disnake.ModalInteraction, warning_message: str | None = None):
        self.warning_message = warning_message
        if self.current_embed_n == None:
            self.up.disabled = True
            self.edit.disabled = True
            self.detail.disabled = True
            self.image.disabled = True
            self.suppr.disabled = True
            self.confirm.disabled = True
            self.add_field.disabled = True
            self.remove_field.disabled = True
        else:
            self.up.disabled = False
            self.edit.disabled = False
            self.detail.disabled = False
            self.image.disabled = False
            self.suppr.disabled = False
            self.confirm.disabled = not self.targets
            if self.current_embed_n == 0:
                self.up.disabled = True
            if self.current_embed_n == len(self.cmdEmbeds)-1:
                self.down.emoji = "🆕"
                self.down.style = disnake.ButtonStyle.green
                if (len(self.cmdEmbeds) >= 8):
                    self.down.disabled = True
                    self.down.label = "Limit reach"
                else:
                    self.down.label = "Embed"
            else:
                self.down.emoji = "⬇️"
                self.down.style = disnake.ButtonStyle.primary
                self.down.label = "Down"
            self.add_field.disabled = not(len(self.cmdEmbeds[self.current_embed_n].fields) < 25 )
            self.remove_field.disabled = (len(self.cmdEmbeds[self.current_embed_n].fields) == 0)
        if self.current_embed_n != None:
            self.up.label = str(self.current_embed_n + 1)
        else:
            self.up.label = "-"
        await interaction.edit_original_message(embeds=self.embeds, view = self)
        
    
    @disnake.ui.button(emoji='⬆️', label="-", style=disnake.ButtonStyle.primary, row=0, disabled=True)
    async def up(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.defer()
        self.current_embed_n -= 1
        await self.update(interaction)
        
    @disnake.ui.button(emoji='🆕', label='Embed', style=disnake.ButtonStyle.green, row=0)
    async def down(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        if self.current_embed_n == None or self.current_embed_n == len(self.cmdEmbeds) -1:
            await interaction.response.send_modal(modal=NewEmbed(self))
        else:
            await interaction.response.defer()
            self.current_embed_n += 1  
            await self.update(interaction)
           
    @disnake.ui.button(label="Embed", emoji='📝', row=0, style=disnake.ButtonStyle.gray, disabled=True)
    async def edit(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_modal(modal=NewEmbed(self, True)) 
        
    @disnake.ui.button(label="Embed", emoji='🧹', row=0, style=disnake.ButtonStyle.red, disabled=True)
    async def suppr(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.defer()
        self.cmdEmbeds.pop(self.current_embed_n)
        if self.current_embed_n == 0:
            self.current_embed_n = None
        elif self.current_embed_n == len(self.cmdEmbeds):
            self.current_embed_n -= 1  
        await self.update(interaction)
        
    @disnake.ui.button(label="Images", emoji='🛤️', row=1, style=disnake.ButtonStyle.gray, disabled=True)
    async def image(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_modal(modal=Image(self))
    
    @disnake.ui.button(label="Details", emoji='👤', row=1, style=disnake.ButtonStyle.gray, disabled=True)
    async def detail(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_modal(modal=Detail(self))
        
    @disnake.ui.button(label="Field", emoji='🆕', row=1, style=disnake.ButtonStyle.green, disabled=True)
    async def add_field(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_modal(modal=Field(self))
        
    @disnake.ui.button(label="Last field", emoji='🧹', row=1, style=disnake.ButtonStyle.red, disabled=True)
    async def remove_field(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.defer()
        current_embed = self.cmdEmbeds[self.current_embed_n]
        current_embed.remove_field(len(current_embed.fields)-1)
        await self.update(interaction)

    @disnake.ui.string_select(placeholder="Color", min_values=1, max_values=1, options=color_dict.keys(), row=2)
    async def color(self, stringSelected: disnake.ui.StringSelect, interaction: disnake.MessageInteraction):
        await interaction.response.defer()
        self.color.placeholder = stringSelected.values[0]
        color = color_dict.get(stringSelected.values[0])
        self.selected_color = color
        if self.cmdEmbeds:
            self.cmdEmbeds[self.current_embed_n].colour = color
        await self.update(interaction)
                  
    @disnake.ui.button(label="Send", emoji='📩', style=disnake.ButtonStyle.green, row=4, disabled=True)
    async def confirm(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.defer()
        for target in self.targets:
            await target.send(embeds=self.cmdEmbeds)
        await self.interaction.edit_original_response(embed=disnake.Embed(description="Embed send !", color=disnake.Colour.green()), view=None)
        await interaction.delete_original_response(delay=3)
        
    @disnake.ui.button(label="Cancel", emoji='❌', style=disnake.ButtonStyle.red, row=4)
    async def clear(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.defer() 
        self.stop()
        await interaction.delete_original_response()
        
class EmbedEditorMentionable(EmbedEditor):
    
    @disnake.ui.mentionable_select(placeholder="User(s)/Role(s)", min_values=1, max_values=25, row=3)
    async def mentionable(self, mentionableSelected: disnake.ui.MentionableSelect, interaction: disnake.MessageInteraction):
        await interaction.response.defer()
        self.targets = mentionableSelected.values
        await self.update(interaction)
        
class EmbedEditorChannel(EmbedEditor):
    
    @disnake.ui.channel_select(placeholder="Channels", min_values=1, max_values=25, row=3, channel_types=[disnake.ChannelType.text,disnake.ChannelType.voice,disnake.ChannelType.news,disnake.ChannelType.public_thread, disnake.ChannelType.private_thread, disnake.ChannelType.news_thread])
    async def channel(self, channelSelected: disnake.ui.ChannelSelect, interaction: disnake.MessageInteraction):
        await interaction.response.defer()
        self.targets = channelSelected.values
        await self.update(interaction)
                
class NewEmbed(disnake.ui.Modal):
    
    def __init__(self, embedEditor: EmbedEditor, edit: bool = False) -> None:
        self.embedEditor = embedEditor
        self.edit = edit
        super().__init__(title="Embed creation", components=[
            disnake.ui.TextInput(label='Title (required if "Description" is empty)', custom_id='title', value=self.embedEditor.cmdEmbeds[self.embedEditor.current_embed_n].title if edit else None, required=False, min_length=0, max_length=256),
            disnake.ui.TextInput(label='Description (required if "Title" is empty)', custom_id='description', value=self.embedEditor.cmdEmbeds[self.embedEditor.current_embed_n].description if edit else None, required=False, min_length=0, max_length=4000, style=disnake.TextInputStyle.paragraph),
            disnake.ui.TextInput(label="Json import (overwrite the entire embed!)", custom_id='json', required=False, style=disnake.TextInputStyle.paragraph)
            ])
       
    async def callback(self, interaction: disnake.ModalInteraction) -> None:
        await interaction.response.defer(with_message=False)
        if interaction.text_values.get('json'):
            try:
                embed_dict = ast.literal_eval(interaction.text_values.get('json'))
            except (ValueError, SyntaxError):
                await self.embedEditor.update(interaction, warning_message="Invalide json format...")
                return
            else:
                new_embed = disnake.Embed.from_dict(embed_dict)
                if self.edit:
                    self.embedEditor.cmdEmbeds[self.embedEditor.current_embed_n] = new_embed  
                else:
                    self.embedEditor.cmdEmbeds.append(new_embed)
                    self.embedEditor.current_embed_n = len(self.embedEditor.cmdEmbeds) -1
                await self.embedEditor.update(interaction)
        elif interaction.text_values.get('title') or interaction.text_values.get('description'):
            if self.edit:
                self.embedEditor.cmdEmbeds[self.embedEditor.current_embed_n].title = interaction.text_values.get('title')
                self.embedEditor.cmdEmbeds[self.embedEditor.current_embed_n].description = interaction.text_values.get('description')
            else:
                new_embed = disnake.Embed(title=interaction.text_values.get('title'), description=interaction.text_values.get('description'), color=self.embedEditor.selected_color)
                self.embedEditor.cmdEmbeds.append(new_embed)
                self.embedEditor.current_embed_n = len(self.embedEditor.cmdEmbeds) -1
            await self.embedEditor.update(interaction)
        else:
            await self.embedEditor.update(interaction, warning_message='Embed creation require at least `Title` or `Description`.')
            
class Image(disnake.ui.Modal):
    
    def __init__(self, embedEditor: EmbedEditor) -> None:
        self.embedEditor = embedEditor
        super().__init__(title="Embed creation", components=[
            disnake.ui.TextInput(label='Image (require "Title" or "Description")', custom_id='image', placeholder="The embed's image URL", required=False, value=self.embedEditor.cmdEmbeds[self.embedEditor.current_embed_n].image.url if self.embedEditor.cmdEmbeds[self.embedEditor.current_embed_n].image else None),
            disnake.ui.TextInput(label='Thumbnail (require "Title" or "Description")', custom_id='thumbnail', placeholder="The thumbnail's url", required=False, value=self.embedEditor.cmdEmbeds[self.embedEditor.current_embed_n].thumbnail.url if self.embedEditor.cmdEmbeds[self.embedEditor.current_embed_n].thumbnail else None)
            ])
       
    async def callback(self, interaction: disnake.ModalInteraction) -> None:
        await interaction.response.defer(with_message=False)
        self.embedEditor.cmdEmbeds[self.embedEditor.current_embed_n].set_image(url=interaction.text_values.get('image'))
        self.embedEditor.cmdEmbeds[self.embedEditor.current_embed_n].set_thumbnail(url=interaction.text_values.get('thumbnail'))
        await self.embedEditor.update(interaction)
        
         
class Detail(disnake.ui.Modal):
    
    def __init__(self, embedEditor: EmbedEditor) -> None:
        self.embedEditor = embedEditor
        super().__init__(title="Embed details", components=[
            disnake.ui.TextInput(label="Author name", custom_id='author', placeholder="The embed's author name", value=self.embedEditor.cmdEmbeds[self.embedEditor.current_embed_n].author.name, required=False, max_length=256),
            disnake.ui.TextInput(label="Author URL (require author's name)", custom_id='author_url', placeholder="The author's URL", value=self.embedEditor.cmdEmbeds[self.embedEditor.current_embed_n].author.url, required=False),
            disnake.ui.TextInput(label="Author icon (require author's name)", custom_id='author_icon', placeholder="The author's icon URL", value=self.embedEditor.cmdEmbeds[self.embedEditor.current_embed_n].author.icon_url, required=False),
            disnake.ui.TextInput(label="Footer text", custom_id='footer_text', placeholder="The footer's text", value=self.embedEditor.cmdEmbeds[self.embedEditor.current_embed_n].footer.text, required=False, max_length=2048),
            disnake.ui.TextInput(label="Footer icon (require Footer's text)", custom_id='footer_icon', placeholder="The footer's icon URL", value=self.embedEditor.cmdEmbeds[self.embedEditor.current_embed_n].footer.icon_url, required=False)
            ])
       
    async def callback(self, interaction: disnake.ModalInteraction) -> None:
        await interaction.response.defer(with_message=False)
        warning_message = None
        if interaction.text_values.get('author'):
            self.embedEditor.cmdEmbeds[self.embedEditor.current_embed_n].set_author(
                name=interaction.text_values.get('author'),
                url=interaction.text_values.get('author_url'),
                icon_url=interaction.text_values.get('author_icon')
            )
        elif interaction.text_values.get('author_url') or interaction.text_values.get('author_icon'):
            warning_message = '`Author name` is require to use `Author URL` and `Author icon`'
        if interaction.text_values.get('footer_text'):
            self.embedEditor.cmdEmbeds[self.embedEditor.current_embed_n].set_footer(
                text=interaction.text_values.get('footer_text'),
                icon_url=interaction.text_values.get('footer_icon')
            )
        elif interaction.text_values.get('footer_icon'):
            if warning_message:
                warning_message += '\n`Footer text` is require to use `Footer icon`'
            else:
                warning_message = '`Footer text` is require to use `Footer icon`'
        await self.embedEditor.update(interaction, warning_message=warning_message)       
        
class Field(disnake.ui.Modal):
    
    def __init__(self, embedEditor: EmbedEditor) -> None:
        self.embedEditor = embedEditor
        super().__init__(title="Field creation", components=[
            disnake.ui.TextInput(label="Title", custom_id='name', placeholder="The field title", max_length=256),
            disnake.ui.TextInput(label="Text", custom_id='text', placeholder="The field text", style=disnake.TextInputStyle.paragraph, max_length=1024),
            disnake.ui.TextInput(label="Inline", custom_id='inline', placeholder="True", value='True'),
            ])
       
    async def callback(self, interaction: disnake.ModalInteraction) -> None:
        await interaction.response.defer(with_message=False)
        inline = False if interaction.text_values.get('inline').lower() in ["false","0","no","n","non"] else True
        if interaction.text_values.get('name') and interaction.text_values.get('text'):
            self.embedEditor.cmdEmbeds[self.embedEditor.current_embed_n].add_field(interaction.text_values.get('name'), interaction.text_values.get('text'), inline=inline)
        await self.embedEditor.update(interaction)   
          
class Embed(commands.Cog):
    def __init__(self, bot):
        """Initialize the cog"""
        self.bot: Bot = bot

    @commands.slash_command(
        name="embed",
        default_member_permissions=disnake.Permissions.all(),
    )
    async def embed(self, inter: disnake.ApplicationCommandInteraction):
        pass
        
        
    @embed.sub_command(
        name="channel",
        description="Send an embed in one/multiple channels"
    )
    async def embed_channel(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer(ephemeral=True)
        EM = EmbedEditorChannel(inter)
        await EM.send()
        
    @embed.sub_command(
        name="user",
        description="Send an embed to users in DM"
    )
    async def embed_user(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer(ephemeral=True)
        EM = EmbedEditorMentionable(inter)
        await EM.send()
        
    @commands.message_command(
        name="embed_export"
    )
    async def embed_export(self, interaction: disnake.MessageCommandInteraction):
        await interaction.response.defer(ephemeral=True)
        jsons_embed: List[disnake.Embed] = []
        for embed in interaction.target.embeds:
            jsons_embed.append(disnake.Embed(description=f"```{embed.to_dict()}```"))
        if jsons_embed:
            await interaction.edit_original_response(embeds=jsons_embed)
        else:
            await interaction.edit_original_response(embed=disnake.Embed(description=f"*No embed to export in [this message]({interaction.target.jump_url})*"))

def setup(bot: commands.InteractionBot):
    bot.add_cog(Embed(bot))
