# -*- coding: utf-8 -*-
from typing import List
from typing import Optional
from typing import Union

import disnake

from modules.Confirmation import *


class RoleSelectionView(ConfirmationView):
    def __init__(
        self,
        target: Target,
        embeds: List[disnake.Embed],
        title: str,
        description: str,
        timeout: int,
        size: Union[List[int], int] = None,
        color: disnake.Colour = disnake.Colour.default(),
    ):
        super().__init__(target, embeds, title, description, timeout, color)
        if isinstance(target, disnake.PartialMessageable):
            raise TypeError("RoleSelection cannot be used on DM channel")
        self.size: Union[List[int], int] = size
        self.role.min_values = max(1, size[0]) if type(size) == list else 1
        self.role.max_values = min(25, size[1]) if type(size) == list else (min(25, size) if size != None else 25)
        self.confirm.disabled = True


    @property
    def embed(self) -> disnake.Embed:
        embed = super().embed
        if self.size:
            embed.add_field(
                name="__Number of roles possible :__",
                value=(", ".join(f"**{n}**" for n in self.size) if isinstance(self.size, list) else f"**{self.size}**"),
                inline=False,
            )
        embed.add_field(
            name=f"__**{len(self.role.values)}** Role(s) selected :__",
            value="\n".join(f"> **{role.mention}**" for role in self.role.values)
            if len(self.role.values)
            else "> *No role selected...*",
            inline=False,
        )
        return embed

    
    @disnake.ui.role_select(
        min_values=1,
        max_values=1,
        row=0,
        placeholder="Roles",
    )
    async def role(self, select: disnake.ui.RoleSelect, interaction: disnake.MessageInteraction):
        self.confirm.disabled = False
        await self.update(interaction)


class RoleSelectionReturnData(ConfirmationReturnData):
    def __init__(self, roleSelectionView: RoleSelectionView):
        super().__init__(roleSelectionView)
        if self.is_confirmed:
            self._roles = roleSelectionView.role.values
        else:
            self._roles = None

    @property
    def roles(self) -> Optional[List[disnake.Role]]:
        return self._roles
    
async def roleSelection(
    target: Target,
    embeds: List[disnake.Embed] = [],
    title: str = "Roles selection",
    description: str = "",
    size: Union[int, List[int]] = None,
    timeout: int = None,
    color: disnake.Colour = disnake.Colour.blue(),
) -> RoleSelectionReturnData:
    """|coro|\n
    Send a member selection view linked to the interaction.
    The interaction can be either an `ApplicationCommandInteraction` or a `MessageInteraction`.

    If the interaction of a `ApplicationCommandInteraction` has not been answered yet, the confirmation view is send using `ephemeral=True`.
    If the interaction has already been answered, or in the case of a `MessageInteraction`, the embeds of the original_message are kept and the confirmation view embed is simply added at the end of the list.

    At the end of the selection, the interaction is defer, but the embeds and views are not removed yet and should be explicitly dealt with during a following `"edit_original_message"` (e.g. `"view=None"` to remove the confirmation view).

    Parameters
    ----------
        target (`Target`):
            The interaction for which the confirmation occurs.
        embeds (`List[disnake.Embed]`)
            The embed to send with the view.
        title (`str`, `optional`):
            Title of the confirmation embed.
            Defaults to `"Confirmation"`.
        description (`str`, `optional`):
            Message of the confirmation embed.
            Defaults to `"Confirmer l'action ?"`.
        size (`int`|`List[int]`, `optional`):
            The nombre(s) of selected member required to be able to validate the selection.
            Defaults to `None`.
        timeout (`int`, `optional`):
            The timeout for the user to answer to confirmation.
            Defaults to `None`.
        pre_selection (`List[disnake.Member]`, `optional`):
            The member to include into the selection at the beginning.
            Defaults to `None`.
        check (`func(**kwargs) -> bool`, `optional`):
            A function that can be used to filter if a member can be added to the selection or not.
            Defaults to `None`.
        color (`disnake.Colour`, `optional`):
            The color to use for the embed.
            Defaults to `disnake.Colour.red()`.

    Check function
    --------
    The kwargs passed to the check function are:
        member (`disnake.Member`):
            The member to filter.
        selected_members (`List[disnake.Member]`):
            The list of members that are already selected.
        size (`List[int]`):
            The list of possible nombre(s) of member selected to be able to validate.
        original_interaction (`Target`):
            The original interaction received by the confirmationView at the beginning.


    Returns
    --------
        `MemberSelectionReturnData`
    """
    return RoleSelectionReturnData(
        await process(
            RoleSelectionView(
                target=target,
                embeds=embeds,
                title=title,
                description=description,
                timeout=timeout,
                size=size,
                color=color,
            )
        )
    )

