# -*- coding: utf-8 -*-
from enum import Enum
from typing import List
from typing import Union

import disnake


class ViewState(Enum):
    CANCELLED = 0
    CONFIRMED = 1
    TIMEOUT = 2
    UNKOWN = 3


Target = Union[
    disnake.ApplicationCommandInteraction,
    disnake.TextChannel,
    disnake.Message,
    disnake.MessageInteraction,
    disnake.ModalInteraction,
]


class ConfirmationView(disnake.ui.View):
    def __init__(
        self,
        target: Target,
        embeds: List[disnake.Embed],
        title: str,
        description: str,
        timeout: int,
        color: disnake.Colour = disnake.Colour.default(),
        thumbnail: str = None,
    ):
        super().__init__(timeout=timeout)
        self.target: Target = target
        self.message_to_delete: disnake.Message = None
        self.embeds: List[disnake.Embed] = embeds if embeds else []
        self.title: str = title
        self.description: str = description
        self.thumbnail: str = thumbnail if thumbnail else None
        self.color: disnake.Colour = color
        self.interaction: disnake.MessageInteraction = None

        self.state: ViewState = ViewState.UNKOWN

    @property
    def embed(self) -> disnake.Embed:
        embed = disnake.Embed(title=self.title, description=self.description, color=self.color)
        embed.set_thumbnail(self.thumbnail)
        return embed

    async def send(self):
        if isinstance(self.target, disnake.ApplicationCommandInteraction):
            if self.target.response.is_done():
                await self.target.edit_original_message(embeds=self.embeds + [self.embed], view=self)
            else:
                await self.target.response.send_message(embeds=self.embeds + [self.embed], view=self, ephemeral=True)
        elif isinstance(self.target, disnake.MessageInteraction):
            if self.target.response.is_done():
                await self.target.edit_original_message(embeds=self.embeds + [self.embed], view=self)
            else:
                await self.target.response.edit_message(embeds=self.embeds + [self.embed], view=self)
        elif isinstance(self.target, disnake.ModalInteraction):
            if self.target.response.is_done():
                await self.target.edit_original_message(embeds=self.embeds + [self.embed], view=self)
            else:
                await self.target.response.send_message(embeds=self.embeds + [self.embed], view=self, ephemeral=True)
        elif isinstance(self.target, disnake.TextChannel):
            self.message_to_delete = await self.target.send(embeds=self.embeds + [self.embed], view=self)
        elif isinstance(self.target, disnake.Message):
            self.message_to_delete = await self.target.channel.send(embeds=self.embeds + [self.embed], view=self)
        else:
            raise TypeError(f"Type {type(self.target)} is not supported.")

    async def update(self, inter: disnake.MessageInteraction):
        if inter.response.is_done():
            await inter.edit_original_message(embeds=self.embeds + [self.embed], view=self)
        else:
            await inter.response.edit_message(embeds=self.embeds + [self.embed], view=self)

    async def end(self) -> None:
        self.stop()
        if self.message_to_delete:
            await self.message_to_delete.delete()

    @disnake.ui.button(label="Confirmer", emoji="✅", row=4, style=disnake.ButtonStyle.green)
    async def confirm(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.defer()
        self.state = ViewState.CONFIRMED
        self.interaction = interaction
        await self.end()

    @disnake.ui.button(label="Annuler", emoji="❌", row=4, style=disnake.ButtonStyle.danger)
    async def cancel(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.defer()
        self.state = ViewState.CANCELLED
        self.interaction = interaction
        await self.end()

    async def on_timeout(self) -> None:
        self.state = ViewState.TIMEOUT
        await self.end()


class ConfirmationReturnData:
    def __init__(self, confirmationView: ConfirmationView):
        self._state = confirmationView.state
        self._interaction: disnake.MessageInteraction = confirmationView.interaction

    @property
    def interaction(self) -> disnake.MessageInteraction:
        return self._interaction

    @property
    def is_ended(self) -> bool:
        return self._state != ViewState.UNKOWN

    @property
    def is_confirmed(self) -> bool:
        return self._state == ViewState.CONFIRMED

    @property
    def is_cancelled(self) -> bool:
        return self._state == ViewState.CANCELLED

    @property
    def is_timeout(self) -> bool:
        return self._state == ViewState.TIMEOUT

    def __bool__(self) -> bool:
        return self.is_confirmed
    
async def process(confirmationvView: ConfirmationView) -> ConfirmationView:
    await confirmationvView.send()
    await confirmationvView.wait()
    return confirmationvView


async def confirmation(
    target: Target,
    embeds: List[disnake.Embed] = [],
    title: str = "Confirmation",
    description: str = "Confirmer l'action ?",
    thumbnail: str = None,
    timeout: int = None,
    color: disnake.Colour = disnake.Colour.red(),
) -> ConfirmationReturnData:
    """|coro|\n
    Send a confirmation view linked to the interaction.
    The interaction can be either an `ApplicationCommandInteraction` or a `MessageInteraction`.

    If the interaction of a `ApplicationCommandInteraction` has not been answered yet, the confirmation view is send using `ephemeral=True`.
    If the interaction has already been answered, or in the case of a `MessageInteraction`, the embeds of the original_message are kept and the confirmation view embed is simply added at the end of the list.

    At the end of the confirmation, the interaction is defer, but the embeds and views are not removed yet and should be explicitly dealt with during a following `"edit_original_message"` (e.g. `"view=None"` to remove the confirmation view).

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
        timeout (`int`, `optional`):
            The timeout for the user to answer to confirmation.
            Defaults to `None`.
        color (`disnake.Colour`, `optional`):
            The color to use for the embed.
            Defaults to `disnake.Colour.red()`.

    Returns
    --------
        `ConfirmationReturnData`
    """
    return ConfirmationReturnData(
        (
            await process(
                ConfirmationView(
                    target=target,
                    embeds=embeds,
                    title=title,
                    description=description,
                    thumbnail=thumbnail,
                    timeout=timeout,
                    color=color,
                )
            )
        )
    )

