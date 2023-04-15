import discord
import asyncio
import speech_recognition
import functools

client = discord.Client()

@client.event
async def on_ready(message):
  print("BOT READY!")

@client.event
  async def on_message(message):
    # "message.flags.value >> 13" == True should be replacable with "message.flags.voice" when VM support comes to discord.py, I think.
    if message.flags.value >> 13 == True and len(message.attachments) == 1:
      msg = await message.reply("✨ Transcribing...")
      
      recognizer = speech_recognition.Recognizer()
      voice_file = await message.attachments[0].read()
      voice_file = io.BytesIO(voice_file)
      
      x = await client.loop.run_in_executor(None, pydub.AudioSegment.from_file, voice_file)
      
      new = io.BytesIO()
      await client.loop.run_in_executor(None, functools.partial(x.export, new, format='wav'))
      
      with speech_recognition.AudioFile(new) as source:
          audio = await client.loop.run_in_executor(None, r.record, source)

      await msg.edit(content="**Audio Message Transcription: ** ```" + (await client.loop.run_in_executor(None, r.recognize_whisper, audio)) + "```")
      
client.run("BOT TOKEN HERE")
