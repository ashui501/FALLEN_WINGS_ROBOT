# # # Thanks to @infinity_bots - MizukiBot
import os

#Saavn 

import requests
import wget
from pyrogram import filters

from YutaRobot import pbot as gabi 
from YutaRobot.pyrogramee.dark import get_arg


@gabi.on_message(filters.command("saavn"))
async def song(client, message):
    message.chat.id
    message.from_user["id"]
    args = get_arg(message) + " " + "song"
    if args.startswith(" "):
        await message.reply("<b>Enter song name❗</b>")
        return ""
    m = await message.reply_text(
        "Downloading your song,\nPlz wait ⏳️"
    )
    try:
        r = requests.get(f"https://jostapi.herokuapp.com/saavn?query={args}")
    except Exception as e:
        await m.edit(str(e))
        return
    sname = r.json()[0]["song"]
    slink = r.json()[0]["media_url"]
    ssingers = r.json()[0]["singers"]
    file = wget.download(slink)
    ffile = file.replace("mp4", "m4a")
    os.rename(file, ffile)
    await message.reply_audio(audio=ffile, title=sname, performer=ssingers)
    os.remove(ffile)
    await m.delete()
