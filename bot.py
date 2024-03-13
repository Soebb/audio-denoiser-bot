import os, wave

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton



Bot = Client(
    "audioBot",
    bot_token = os.environ["BOT_TOKEN"],
    api_id = int(os.environ["API_ID"]),
    api_hash = os.environ["API_HASH"]
)


START_TXT = """
Hi {}, I'm audio denoiser Bot.

Just send me an audio file.
"""

START_BTN = InlineKeyboardMarkup(
        [[
        InlineKeyboardButton('Source Code', url='https://github.com/soebb'),
        ]]
    )


@Bot.on_message(filters.command(["start"]))
async def start(bot, update):
    text = START_TXT.format(update.from_user.mention)
    reply_markup = START_BTN
    await update.reply_text(
        text=text,
        disable_web_page_preview=True,
        reply_markup=reply_markup
)


@Bot.on_message(filters.private & filters.audio)
async def t2s(bot, m):
    msg = await m.reply("Processing..")
    input = await bot.download_media(message=m)
    wav = "output.wav"
    
    await msg.edit_text("`Converting to wave...`")
    os.system(f'ffmpeg -i "{input}" -vn -y {wav}')
    await msg.edit_text("`Now Processing...`")

    await m.reply_audio(den)
    await msg.delete()
    os.remove(input)

Bot.run()
