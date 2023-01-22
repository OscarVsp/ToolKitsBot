# -*- coding: utf-8 -*-
from typing import List, Tuple
import disnake
from disnake.ext import commands
from deep_translator import GoogleTranslator

from bot.bot import Bot

translator_en = GoogleTranslator(source="auto", target="en")
translator_sv = GoogleTranslator(source="auto", target="sv")
translator_fr = GoogleTranslator(source="auto", target="fr")

def translate(text: str, translator: GoogleTranslator = translator_en) -> str:
    if text != None and text != None:
        return_text = ""
        i = (0, 4999)
        while i[1] < len(text):
            tr_text = translator.translate(text[i[0] : i[1]])
            if tr_text:
                return_text += tr_text
            else:
                return_text += text[i[0] : i[1]]
            i[0] += 5000
            i[1] += 5000
        tr_text = translator.translate(text[i[0] :])
        if tr_text:
            return_text += tr_text
        else:
            return_text += text[i[0] :]
        return return_text
    else:
        return ""
    
def translate_msg(message:disnake.Message, transaltor: GoogleTranslator = translator_en) -> Tuple[str, List[disnake.Embed]]:
    content = translate(message.content, transaltor)
    embeds = []
    for embed in message.embeds:
        if embed.title != None:
            embed.title = translate(embed.title, transaltor)
        if embed.description != None:
            embed.description = translate(embed.description, transaltor)
        if embed.footer.text:
            embed.set_footer(text=translate(embed.footer.text,transaltor), icon_url=embed.footer.icon_url)
        if embed.author.name:
            embed.set_author(
                name=translate(embed.author.name,transaltor), url=embed.author.url, icon_url=embed.author.icon_url
            )
        fields = embed.fields.copy()
        embed.clear_fields()
        for field in fields:
            embed.add_field(name=translate(field.name,transaltor), value=translate(field.value,transaltor), inline=field.inline)
        embeds.append(embed)
    return (content, embeds)


   
class Translator(commands.Cog):
    def __init__(self, bot):
        """Initialize the cog"""
        self.bot: Bot = bot

    @commands.message_command(
        name="translate_en"
    )
    async def translate_en(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer(ephemeral=True)
        content,embeds = translate_msg(inter.target)
        await inter.edit_original_message(
            content=content,
            embeds=embeds,
        )
        
    @commands.message_command(
        name="translate_sv"
    )
    async def translate_sv(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer(ephemeral=True)
        content,embeds = translate_msg(inter.target, translator_sv)
        await inter.edit_original_message(
            content=content,
            embeds=embeds,
        )
        
    @commands.message_command(
        name="translate_fr"
    )
    async def translate_fr(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer(ephemeral=True)
        content,embeds = translate_msg(inter.target, translator_fr)
        await inter.edit_original_message(
            content=content,
            embeds=embeds,
        )
        
def setup(bot: commands.InteractionBot):
    bot.add_cog(Translator(bot))
