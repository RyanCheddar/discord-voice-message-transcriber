import discord
import speech_recognition
import functools
import pydub
import io
from discord import app_commands

# This controls if all voice messages should be transcribed automatically
# Change False to True if you want this behavior, not recommended for public bots!
transcribe_everything = False

# Enter the User IDs of people who you want to have control over the bot's configs
# Currently, these people just have the ability to sync the bot's command tree.
bot_managers = [396545298069061642]



intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(command_prefix='!', intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
	print("BOT READY!")

async def transcribe_message(message):
	if len(message.attachments) == 0:
		await message.reply("Transcription failed! (No Voice Message)", mention_author=False)
		return
	if message.attachments[0].content_type != "audio/ogg":
		await message.reply("Transcription failed! (Attachment not a Voice Message)", mention_author=False)
		return
	
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
	await msg.edit(content="**Audio Message Transcription:\n** ```" + result + "```")

@client.event
async def on_message(message):
	# "message.flags.value >> 13" should be replacable with "message.flags.voice" when VM support comes to discord.py, I think.
	if transcribe_everything and message.flags.value >> 13 and len(message.attachments) == 1:
		await transcribe_message(message)

	if message.content == "!synctree" and message.author.id in bot_managers:
		await tree.sync(guild=None)
		await message.reply("Synced!")
		return


# Slash Command / Context Menu Handlers
@tree.command(name="opensource")
async def open_source(interaction: discord.Interaction):
	embed = discord.Embed(
    	title="Open Source",
    	description="This bot is open source! You can find the source code "
                    "[here](https://https://github.com/RyanCheddar/discord-voice-message-transcriber)",
    	color=0x00ff00
	)
	await interaction.response.send_message(embed=embed)
    
@tree.command(name="synctree", description="Syncs the bot's command tree.")
async def synctree(interaction: discord.Interaction):
	if interaction.user.id not in bot_managers:
		await interaction.response.send_message(content="You are not a Bot Manager!")
		return

	await tree.sync(guild=None)
	await interaction.response.send_message(content="Synced!")
    
@tree.context_menu(name="Transcribe VM")
async def transcribe_contextmenu(interaction: discord.Interaction, message: discord.Message):
    await interaction.response.send_message(content="Transcription started!", ephemeral=True)
    await transcribe_message(message)
	  
client.run("BOT TOKEN HERE")
