import os, wave
import torch
import torchaudio
from denoisers import WaveUNetModel
from tqdm import tqdm
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

    model = WaveUNetModel.from_pretrained("wrice/waveunet-vctk-24khz")
    audio, sr = torchaudio.load("output.wav")
    if sr != model.config.sample_rate:
        audio = torchaudio.functional.resample(audio, sr, model.config.sample_rate)
    if audio.size(0) > 1:
        audio = audio.mean(0, keepdim=True)
    chunk_size = model.config.max_length
    padding = abs(audio.size(-1) % chunk_size - chunk_size)
    padded = torch.nn.functional.pad(audio, (0, padding))
    clean = []
    for i in tqdm(range(0, padded.shape[-1], chunk_size)):
        audio_chunk = padded[:, i:i + chunk_size]
        with torch.no_grad():
            clean_chunk = model(audio_chunk[None]).audio
    clean.append(clean_chunk.squeeze(0))

    denoised = torch.concat(clean, 1)[:, :audio.shape[-1]]
    await m.reply_audio(denoised)
    await msg.delete()
    os.remove(input)
    os.remove(denoised)

Bot.run()
