from fumck import app, SUDOERS
from pyrogram import filters, Client
from pyrogram.types import Message
from fumck.lumd.DB.onoff import (is_on_off, add_on, add_off)
from fumck.lumd.helpers.filters import command


@Client.on_message(command("Music") & filters.user(SUDOERS))
async def smex(_, message):
    usage = "**Usage:**\n/Musicp [enable|disable]"
    if len(message.command) != 2:
        return await message.reply_text(usage)
    chat_id = message.chat.id
    state = message.text.split(None, 1)[1].strip()
    state = state.lower()
    if state == "enable":
        user_id = 1
        await add_on(user_id)
        await message.reply_text("Music Enabled for Maintenance")
    elif state == "disable":
        user_id = 1
        await add_off(user_id)
        await message.reply_text("Maintenance Mode Disabled")
    else:
        await message.reply_text(usage)

        
@Client.on_message(command("st") & filters.user(SUDOERS))
async def sls_skfs(_, message):
    usage = "**Usage:**\n/st [enable|disable]"
    if len(message.command) != 2:
        return await message.reply_text(usage)
    chat_id = message.chat.id
    state = message.text.split(None, 1)[1].strip()
    state = state.lower()
    if state == "enable":
        user_id = 2
        await add_on(user_id)
        await message.reply_text("𝗦𝗽𝗲𝗲𝗱𝘁𝗲𝘀𝘆 𝗘𝗻𝗮𝗯𝗹𝗲𝗱")
    elif state == "disable":
        user_id = 2
        await add_off(user_id)
        await message.reply_text("Speedtest 𝗗𝗶𝘀𝗮𝗯𝗹𝗲𝗱")
    else:
        await message.reply_text(usage)
