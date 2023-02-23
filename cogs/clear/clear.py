import asyncio
from typing import List
import disnake
from disnake.ext import commands

from bot.bot import Bot

from modules.assets import *
from modules.Confirmation import *
from modules.RoleSelection import *


class Clear(commands.Cog):
    def __init__(self, bot):
        """Initialize the cog"""
        self.bot: Bot = bot
        
    @commands.message_command(
        name="Clear up to this",
        default_member_permissions=disnake.Permissions.all(),
        dm_permission=False,
    ) 
    async def clear_msg(self, inter: disnake.MessageCommandInteraction):
        await inter.response.defer(ephemeral=True)
        n = 0
        async for message in inter.channel.history(limit=None):
            n += 1
            if message == inter.target:
                break
            
        confirm: ConfirmationReturnData = await confirmation(
            inter,
            title=f"__**Suppression de {n} message(s)**__",
            description=f"Êtes-vous sûr de vouloir supprimer les {n} dernier(s) message(s) de ce channel ?\nCeci supprimera tout les messages jusqu'à [celui-ci]({message.jump_url})\nCette action est irréversible !",
            timeout=30,
        )
        if confirm:
            await inter.edit_original_message(
                embed=disnake.Embed(
                    description=f"Suppression de {n} message(s) en cours... ⌛", color=disnake.Colour.green()
                ),
                view=None,
            )
            await inter.channel.purge(limit=n)
            await inter.edit_original_message(
                embed=disnake.Embed(
                    description=f":broom: {n} messages supprimés ! :broom:", color=disnake.Colour.green()
                )
            )
        elif confirm.is_cancelled:
            await inter.edit_original_message(
                embed=disnake.Embed(
                    description=f":o: Suppresion de {n} message(s) annulée", color=disnake.Colour.dark_grey()
                ),
                view=None,
            )
        else:
            await inter.edit_original_message(
                embed=disnake.Embed(
                    description=f":o: Suppresion de {n} message(s) timeout", color=disnake.Colour.dark_grey()
                ),
                view=None,
            )
        await inter.delete_original_response(delay=2)
        

    @commands.slash_command(
        name="clear",
        default_member_permissions=disnake.Permissions.all(),
        dm_permission=False,
    )
    async def clear(self, inter):
        pass

    @clear.sub_command(name="message", description="Delete the last messages of this channel")
    async def clearMessage(
        self,
        inter: disnake.ApplicationCommandInteraction,
        nombre: int = commands.Param(description="le nombre de message à supprimer", gt=0),
    ):
        last_message = (await inter.channel.history(limit=nombre).flatten())[-1]
        confirm: ConfirmationReturnData = await confirmation(
            inter,
            title=f"__**Suppression of {nombre} message(s)**__",
            description=f"Are you sure to delete the {nombre} last message(s) of this channel ?\nThis will delete all messages up to [this one]({last_message.jump_url})",
            timeout=30,
        )
        if confirm:
            await inter.edit_original_message(
                embed=disnake.Embed(
                    description=f"Suppression of {nombre} message(s)... ⌛", color=disnake.Colour.green()
                ),
                view=None,
            )
            await inter.channel.purge(limit=nombre)
            await inter.edit_original_message(
                embed=disnake.Embed(
                    description=f":broom: {nombre} messages deleted ! :broom:", color=disnake.Colour.green()
                )
            )
        elif confirm.is_cancelled:
            await inter.edit_original_message(
                embed=disnake.Embed(
                    description=f":o: Message suppression cancelled", color=disnake.Colour.dark_grey()
                ),
                view=None,
            )
        else:
            await inter.edit_original_message(
                embed=disnake.Embed(
                    description=f":o: Message suppression timeout", color=disnake.Colour.dark_grey()
                ),
                view=None,
            )
        await inter.delete_original_response(delay=2)

    @clear.sub_command(name="category", description="Delete a category and the channels in it")
    async def clearCat(
        self,
        inter: disnake.ApplicationCommandInteraction,
        categorie: disnake.CategoryChannel = commands.Param(description="Categoey to delete"),
    ):

        if await confirmation(
            inter,
            title=f"__**Category *{categorie.name}* suppression**__",
            description=f"Are you sure to delete the category ***{categorie.mention}*** ?\nThis will also delete the {len(categorie.channels)} channels in it:\n"
            + "\n".join(channel.mention for channel in categorie.channels)
        ):
            await inter.edit_original_message(
                embed=disnake.Embed(
                    description=f"Suppression of the category *{categorie.name}*... ⌛",
                    color=disnake.Colour.green(),
                ),
                view=None,
            )
            for channel in categorie.channels:
                await channel.delete()
            await categorie.delete()
            try:
                await inter.edit_original_message(
                    embed=disnake.Embed(
                        description=f":broom: **Category** *{categorie.name}* **deleted** ! :broom:",
                        color=disnake.Colour.green(),
                    )
                )
            except disnake.NotFound:
                pass
        else:
            await inter.edit_original_message(
                embed=disnake.Embed(
                    description=f":o: Suppression of the category {categorie.mention} cancelled !",
                    color=disnake.Colour.green(),
                ),
                view=None,
            )
        await inter.delete_original_response(delay=2)
        
    @clear.sub_command(name="roles", description="Delete some roles")
    async def clearRole(
        self,
        inter: disnake.ApplicationCommandInteraction,
    ):
        rolesData = await roleSelection(
            inter,
            title=f"__**Roles suppression**__",
            description=f"Select roles to delete"
        )
        if rolesData:
            await inter.edit_original_message(
                embed=disnake.Embed(
                    description=f"Suppression of {len(rolesData.roles)} role(s)... ⌛",
                    color=disnake.Colour.green(),
                ),
                view=None,
            )
            rolesRemaining: List[disnake.Role] = []
            for role in rolesData.roles:
                try:
                    await role.delete()
                except (disnake.Forbidden, disnake.HTTPException):
                    rolesRemaining.append(role) 
            if len(rolesRemaining) == 0:
                await inter.edit_original_message(
                    embed=disnake.Embed(
                        description=f":broom: {len(rolesData.roles)} role(s) deleted ! :broom:",
                        color=disnake.Colour.green(),
                    )
                )
            else:
                embed=disnake.Embed(
                    description=f":broom: {len(rolesData.roles) - len(rolesRemaining)} role(s) deleted ! :broom:",
                    color=disnake.Colour.orange(),
                )
                embed.add_field(name="⚠️", value="Some roles could not be deleted because I don't have the permission or because there are bot roles:\n"+"\n".join([role.mention for role in rolesRemaining]))
                await inter.edit_original_message(
                    embed=embed
                )
                await asyncio.sleep(5)
        else:
            await inter.edit_original_message(
                embed=disnake.Embed(
                    description=f":o: Suppression of role(s) cancelled !",
                    color=disnake.Colour.green(),
                ),
                view=None,
            )
        await inter.delete_original_response(delay=2)
            
def setup(bot: commands.InteractionBot):
    bot.add_cog(Clear(bot))
