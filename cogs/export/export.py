# -*- coding: utf-8 -*-
from typing import List, Tuple
import disnake
from disnake.ext import commands

from bot.bot import Bot


from modules.Confirmation import *
from modules.RoleSelection import *
from modules.MemberSelection import *

class RoleFromABC(disnake.ui.View):
    
    def __init__(self):
        super().__init__(timeout=None)
        self.members: List[disnake.Member] = None
        
    @property
    def embed(self) -> disnake.Embed:
        pass

    def add_field(self, embed: disnake.Embed) -> disnake.Embed:
        return embed.add_field(name="__Members:__", value="> "+"\n> ".join([member.mention for member in self.members]))
        
    @disnake.ui.button(label="New role", emoji="🆕")
    async def new(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_modal(RoleCreationModal(self.members, self.end_embed))
        
    @disnake.ui.button(label="Existing role", emoji="➡️")
    async def add(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.defer()
        rolesData = await roleSelection(interaction, size=1)
        if rolesData:
            role = rolesData.roles[0]
            for member in self.members:
                if role not in member.roles:
                    await member.add_roles(role)
            await self.end_embed(role,interaction)
        else:
            await interaction.delete_original_response()
            
    async def end_embed(self, role: disnake.Role, interaction: disnake.MessageInteraction):
        pass

class RoleFromRoles(RoleFromABC):
    
    def __init__(self, roles: List[disnake.Role]):
        super().__init__()
        self.roles = roles
        for role in self.roles:
            for member in role.members:
                if member not in self.members:
                    self.members.append(member)
                    
    @property
    def embed(self) -> disnake.Embed:
        return super().add_field(disnake.Embed(title="__**Role from roles Export**__", description="__Roles source: __\n> "+"\n> ".join([role.mention for role in self.roles])))          
        
   
    async def end_embed(self, role: disnake.Role, interaction: disnake.MessageInteraction):
        await interaction.edit_original_response(embed=super().add_field(disnake.Embed(description="Role(s) "+", ".join([role.mention for role in self.roles])+f" members added to role {role.mention}")), view=None)
        await interaction.delete_original_response(delay=5)
        
class RoleFromEvent(RoleFromABC):
    
    def __init__(self, event: disnake.GuildScheduledEvent):
        super().__init__()
        self.event = event
        self.members: List[disnake.Member] = None
        
    async def fetch_members(self):
        self.members = []
        async for member in self.event.fetch_users():
            self.members.append(member)
            
    @property
    def embed(self) -> disnake.Embed:
        return super().add_field(disnake.Embed(title="__**Role from event Export**__", description=f"__Event source: __\n> {self.event.name}")) 
        
    
            
    async def end_embed(self, role: disnake.Role, interaction: disnake.MessageInteraction):
        await interaction.edit_original_response(embed=super().add_field(disnake.Embed(description=f"Event's **{self.event.name}** participant(s) added to role {role.mention}")), view=None)
        await interaction.delete_original_response(delay=5)
            
class RoleCreationModal(disnake.ui.Modal):
    
    def __init__(self, members: List[disnake.Member], call_back) -> None:
        super().__init__(title="Role creation", components=[
            disnake.ui.TextInput(label="Role's name", placeholder="Name of the role to create", custom_id='name')
        ])
        self.members = members
        self.call_back = call_back
        
    async def callback(self, interaction: disnake.ModalInteraction) -> None:
        await interaction.response.defer(with_message=False)
        role = await interaction.guild.create_role(name=interaction.text_values.get('name'))
        for member in self.members:
            await member.add_roles(role)
        await self.call_back(role,interaction)
        
        
    
   
class Export(commands.Cog):
    
    def __init__(self, bot):
        """Initialize the cog"""
        self.bot: Bot = bot
        
    @commands.slash_command(
        name="role",
        description="Create role"
    )
    async def role(self, inter: disnake.ApplicationCommandInteraction):
        pass

    @role.sub_command_group(
        name="from"
    )
    async def role_from(self, inter: disnake.ApplicationCommandInteraction):
        pass
    
    @role_from.sub_command(
        name="roles"
    )
    async def role_from_roles(self, inter: disnake.ApplicationCommandInteraction):
        rolesData = await roleSelection(inter)
        if rolesData:
            RFR = RoleFromRoles(rolesData.roles)
            await inter.edit_original_response(embed=RFR, view=RFR)
        else:
            await inter.delete_original_response()
            
    @role_from.sub_command(
        name="event"
    )
    async def role_from_event(self,
        inter: disnake.ApplicationCommandInteraction,
        event: str = commands.Param(description="L'évennement depuis lequel exporter les membres"),
    ):
        await inter.response.defer(ephemeral=True)
        events = await inter.guild.fetch_scheduled_events()
        event: disnake.GuildScheduledEvent = next((e for e in events if e.name == event), None)
        RFE = RoleFromEvent(event)
        await RFE.fetch_members()
        await inter.edit_original_message(embed=RFE.embed, view=RFE)

    @role_from_event.autocomplete("event")
    async def autocomp_event(self, inter: disnake.ApplicationCommandInteraction, user_input: str):
        events = []
        for event in inter.guild.scheduled_events:
            if event.name.lower().startswith(user_input.lower()):
                events.append(event.name)
        return events
            

    
        
def setup(bot: commands.InteractionBot):
    bot.add_cog(Export(bot))
