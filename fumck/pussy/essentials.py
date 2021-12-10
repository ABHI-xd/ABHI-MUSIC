
import os
import subprocess
import shutil
import re
import sys
import traceback
from inspect import getfullargspec
from io import StringIO
from time import time
from fumck.lumd.DB.queue import (is_active_chat, add_active_chat, remove_active_chat, music_on, is_music_playing, music_off)
from fumck.lumd.DB.onoff import (is_on_off, add_on, add_off)
from fumck.lumd.DB.blchat import (blacklisted_chats, blacklist_chat, whitelist_chat)
from fumck.lumd.DB.gban import (get_gbans_count, is_gbanned_user, add_gban_user, add_gban_user)
from fumck.lumd.DB.theme import (_get_theme, get_theme, save_theme)
from fumck.lumd.DB.assistant import (_get_assistant, get_assistant, save_assistant)
from fumck.config import DURATION_LIMIT
from fumck.lumd.tgcallsrun import (music, clear, get, is_empty, put, task_done)
from fumck.lumd.helpers.decorators import errors
from fumck.lumd.helpers.filters import command
from fumck.lumd.helpers.gets import (get_url, themes, random_assistant)
from fumck.lumd.helpers.logger import LOG_CHAT
from fumck.lumd.helpers.thumbnails import gen_thumb
from fumck.lumd.helpers.chattitle import CHAT_TITLE
from fumck.lumd.helpers.ytdl import ytdl
from fumck.lumd.helpers.inline import (play_keyboard, search_markup)
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from sys import version as pyver
from pyrogram import Client, filters
from pyrogram.types import Message
from fumck import app, SUDOERS, OWNER
from fumck.lumd.helpers.filters import command
from fumck.lumd.helpers.decorators import errors
from fumck.lumd.DB.functions import start_restart_stage

@Client.on_message(command("update") & filters.user(OWNER))
@errors
async def update(_, message: Message):
    m = subprocess.check_output(["git", "pull"]).decode("UTF-8")
    if str(m[0]) != "A":
        x = await message.reply_text("Found Updates! Pushing Now.")
        await start_restart_stage(x.chat.id, x.message_id)
        os.execvp("python3", ["python3", "-m", "Music"])
    else:
        await message.reply_text("Already Upto Date")
        
async def aexec(code, client, message):
    exec(
        "async def __aexec(client, message): "
        + "".join(f"\n {a}" for a in code.split("\n"))
    )
    return await locals()["__aexec"](client, message)


async def edit_or_reply(msg: Message, **kwargs):
    func = msg.edit_text if msg.from_user.is_self else msg.reply
    spec = getfullargspec(func.__wrapped__).args
    await func(**{k: v for k, v in kwargs.items() if k in spec})


@app.on_message(
    filters.user(OWNER)
    & ~filters.forwarded
    & ~filters.via_bot
    & filters.command("eval")
)
async def executor(client, message):
    if len(message.command) < 2:
        return await edit_or_reply(message, text="__Nigga Give me some command to execute.__")
    try:
        cmd = message.text.split(" ", maxsplit=1)[1]
    except IndexError:
        return await message.delete()
    t1 = time()
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    redirected_error = sys.stderr = StringIO()
    stdout, stderr, exc = None, None, None
    try:
        await aexec(cmd, client, message)
    except Exception:
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"
    final_output = f"**OUTPUT**:\n```{evaluation.strip()}```"
    if len(final_output) > 4096:
        filename = "output.txt"
        with open(filename, "w+", encoding="utf8") as out_file:
            out_file.write(str(evaluation.strip()))
        t2 = time()
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="⏳", callback_data=f"runtime {t2-t1} Seconds"
                    )
                ]
            ]
        )
        await message.reply_document(
            document=filename,
            caption=f"**INPUT:**\n`{cmd[0:980]}`\n\n**OUTPUT:**\n`Attached Document`",
            quote=False,
            reply_markup=keyboard,
        )
        await message.delete()
        os.remove(filename)
    else:
        t2 = time()
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="⏳",
                        callback_data=f"runtime {round(t2-t1, 3)} Seconds",
                    )
                ]
            ]
        )
        await edit_or_reply(message, text=final_output, reply_markup=keyboard)


@app.on_callback_query(filters.regex(r"runtime"))
async def runtime_func_cq(_, cq):
    runtime = cq.data.split(None, 1)[1]
    await cq.answer(runtime, show_alert=True)


@app.on_message(
    filters.user(OWNER)
    & ~filters.forwarded
    & ~filters.via_bot
    & filters.command("sh"),
)
async def shellrunner(client, message):
    if len(message.command) < 2:
        return await edit_or_reply(message, text="**Usage:**\n/sh git pull")
    text = message.text.split(None, 1)[1]
    if "\n" in text:
        code = text.split("\n")
        output = ""
        for x in code:
            shell = re.split(""" (?=(?:[^'"]|'[^']*'|"[^"]*")*$)""", x)
            try:
                process = subprocess.Popen(
                    shell,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
            except Exception as err:
                print(err)
                await edit_or_reply(message, text=f"**ERROR:**\n```{err}```")
            output += f"**{code}**\n"
            output += process.stdout.read()[:-1].decode("utf-8")
            output += "\n"
    else:
        shell = re.split(""" (?=(?:[^'"]|'[^']*'|"[^"]*")*$)""", text)
        for a in range(len(shell)):
            shell[a] = shell[a].replace('"', "")
        try:
            process = subprocess.Popen(
                shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except Exception as err:
            print(err)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            errors = traceback.format_exception(
                etype=exc_type,
                value=exc_obj,
                tb=exc_tb,
            )
            return await edit_or_reply(
                message, text=f"**ERROR:**\n```{''.join(errors)}```"
            )
        output = process.stdout.read()[:-1].decode("utf-8")
    if str(output) == "\n":
        output = None
    if output:
        if len(output) > 4096:
            with open("output.txt", "w+") as file:
                file.write(output)
            await app.send_document(
                message.chat.id,
                "output.txt",
                reply_to_message_id=message.message_id,
                caption="`Output`",
            )
            return os.remove("output.txt")
        await edit_or_reply(message, text=f"**OUTPUT:**\n```{output}```")
    else:
        await edit_or_reply(message, text="**OUTPUT: **\n`No output`")
