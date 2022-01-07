import os
import re
from platform import python_version as kontol
from telethon import events, Button
from telegram import __version__ as telever
from telethon import __version__ as tlhver
from pyrogram import __version__ as pyrover
from Tanji.events import register
from Tanji import telethn as tbot


PHOTO = "https://telegra.ph/file/a6b73cd9e8c2b6e22f9bc.mp4"

@register(pattern=("/alive"))
async def awake(event):
  TEXT = f"**Hi [{event.sender.first_name}](tg://user?id={event.sender.id}), I'm Tanjirou Kamado.** \n\n"
  TEXT += "🌟 **I'm Working Properly** \n\n"
  TEXT += f"🌟 **My Master : [Tanjirou](https://t.me/Lynncept_iz_here)** \n\n"
  TEXT += f"🌟 **Library Version :** `{telever}` \n\n"
  TEXT += f"🌟 **Telethon Version :** `{tlhver}` \n\n"
  TEXT += f"🌟 **Pyrogram Version :** `{pyrover}` \n\n"
  TEXT += "**Thanks For Adding Me Here ❤️**"
  BUTTON = [[Button.url("Help", "https://t.me/Tanji_kamado_bot?start=help"), Button.url("Support", "https://t.me/Tanji_kamado_support")]]
  await tbot.send_file(event.chat_id, PHOTO, caption=TEXT,  buttons=BUTTON)
