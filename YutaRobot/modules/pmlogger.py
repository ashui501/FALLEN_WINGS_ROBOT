# Made for shitty purposes by Yash-Sharma-1807


from pyrogram import *
from pyrogram.types import *
from YutaRobot import pbot as app

@app.on_message(filters.command(["start","help"]) & filters.private)
async def shity_af_stuff(client : Client,message : Message) :
    try : 
        await client.send_message(-1001709251588,f"{message.from_user.mention} #Makise_NEW user just started the bot in pm")
    except Exception :
        pass
