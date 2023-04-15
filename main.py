import discord
import asyncio
import speech_recognition
import functools
import pydub


client = discord.Client()

@client.event
async def on_ready(message):
  print("BOT READY!")

@client.event
  async def on_message(message):
    # "message.flags.value >> 13" should be replacable with "message.flags.voice" when VM support comes to discord.py, I think.
    if message.flags.value >> 13 and len(message.attachments) == 1:
      msg = await message.reply("✨ Transcribing...", mention_author=False)
      
      # Read voice file and converts it into something pydub can work with
      voice_file = await message.attachments[0].read()
      voice_file = io.BytesIO(voice_file)
      
      # Convert original .ogg file into a .wav file
      x = await client.loop.run_in_executor(None, pydub.AudioSegment.from_file, voice_file)
      new = io.BytesIO()
      await client.loop.run_in_executor(None, functools.partial(x.export, new, format='wav'))
      
      # Convert .wav file into speech_recognition's AudioFile format or whatever idrk
      recognizer = speech_recognition.Recognizer()
      with speech_recognition.AudioFile(new) as source:
          audio = await client.loop.run_in_executor(None, recognizer.record, source)
      
      # Runs the file through OpenAI Whisper
      result = await client.loop.run_in_executor(None, recognizer.recognize_whisper, audio)
      await msg.edit(content="**Audio Message Transcription: ** ```" + result + "```")
      
client.run("BOT TOKEN HERE")
