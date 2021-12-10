import os
import speedtest
import wget
from fumck.lumd.helpers.gets import bytes
from fumck import app, SUDOERS, BOT_ID
from pyrogram import filters, Client
from fumck.lumd.database.onoff import (is_on_off, add_on, add_off)
from pyrogram.types import Message

@app.on_message(filters.command("speedtest") & ~filters.edited)
async def gstats(_, message):
    userid = message.from_user.id
    if await is_on_off(2):
        if userid in SUDOERS:
            pass
        else:
            return
    m = await message.reply_text("𝗥𝘂𝗻𝗻𝗶𝗻𝗴 𝗦𝗽𝗲𝗲𝗱𝘁𝗲𝘀𝘁😏")
    try:
        test = speedtest.Speedtest()
        test.get_best_server()
        m = await m.edit("𝗥𝘂𝗻𝗻𝗶𝗻𝗴 𝗗𝗼𝘄𝗻𝗹𝗼𝗮𝗱 𝗦𝗽𝗲𝗲𝗱𝘁𝗲𝘀𝘁😏")
        test.download()
        m = await m.edit("𝗥𝘂𝗻𝗻𝗶𝗻𝗴 𝗨𝗽𝗹𝗼𝗮𝗱 𝗦𝗽𝗲𝗲𝗱𝘁𝗲𝘀𝘁😏")
        test.upload()
        test.results.share()
        result = test.results.dict()
    except Exception as e:
        await message.err(text=e)
        return 
    m = await m.edit("𝗗𝗘𝗞𝗛𝗔 𝗟𝗢 𝗦𝗣𝗘𝗘𝗗 𝗧𝗘𝗦𝗧😏")
    path = wget.download(result["share"])
    output = f"""**𝗦𝗽𝗲𝗲𝗱𝘁𝗲𝘀𝘁 𝗥𝗲𝘀𝘂𝗹𝘁𝘀😏**
    
<u>**Client:**</u>
**__ISP:__** {result['client']['isp']}
**__Country:__** {result['client']['country']}
  
<u>**Server:**</u>
**__Name:__** {result['server']['name']}
**__Country:__** {result['server']['country']}, {result['server']['cc']}
**__Sponsor:__** {result['server']['sponsor']}
**__Latency:__** {result['server']['latency']}  
**__Ping:__** {result['ping']}"""
    msg = await app.send_photo(
        chat_id=message.chat.id, photo=path, caption=output
    )
    os.remove(path)
    await m.delete()
