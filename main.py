import io
import os
import re
import sys
import functools
import configparser

import discord
import speech_recognition
import pydub
from discord import app_commands

from dotenv import load_dotenv

load_dotenv(".env")
BOT_TOKEN = os.getenv("BOT_TOKEN")

config = configparser.ConfigParser()
config.read("config.ini")

if "transcribe" not in config and "admins" not in config:
	print("Something is wrong with your config.ini file.")
	sys.exit(1)

try:
	TRANSCRIBE_AUTOMATICALLY = config.getboolean("transcribe", "automatically")
	TRANSCRIBE_VMS_ONLY = config.getboolean("transcribe", "voice_messages_only")
	ADMIN_USERS = [int(i) for i in re.split(", |,", config["admins"]["users"])]
	ADMIN_ROLE = config.getint("admins", "role")

except (configparser.NoOptionError, ValueError):
	print("Something is wrong with your config.ini file.")
	sys.exit(1)

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True  # Change to False if not using the "ADMIN_ROLE" variable

# Create a new client and specify intents
client = discord.Client(command_prefix='!', intents=intents)

# Define the CommandTree instance for registering commands
tree = app_commands.CommandTree(client)

# Create a new SlashCommand instance
# slash = SlashCommand(client, sync_commands=True)

@client.event
async def on_ready():
	print("BOT READY!")
	await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='listening to your voice messages'))

async def transcribe_message(message):
	if len(message.attachments) == 0 or message.attachments[0].content_type != "audio/ogg":
		await message.reply("Transcription failed! (No Voice Message)", mention_author=False)
		return
	
	msg = await message.reply("✨ Transcribing...", mention_author=False)
	
	# Read voice file and converts it into something pydub can work with
	voice_file = io.BytesIO(await message.attachments[0].read())

	
	# Convert original .ogg file into a .wav file
	x = await client.loop.run_in_executor(None, pydub.AudioSegment.from_file, voice_file)
	new = io.BytesIO()
	await client.loop.run_in_executor(None, functools.partial(x.export, new, format='wav'))

	""" 
	audio_segment = await client.loop.run_in_executor(None, pydub.AudioSegment.from_file, voice_file, format="ogg")
	wav_bytes = io.BytesIO()
	export_func = lambda: audio_segment.export(wav_bytes, format='wav')
	await client.loop.run_in_executor(None, export_func)
 	"""
	
	# Convert .wav file into speech_recognition's AudioFile format or whatever idrk
	recognizer = speech_recognition.Recognizer()
	with speech_recognition.AudioFile(new) as source:
		audio = await client.loop.run_in_executor(None, recognizer.record, source)
	
	# Runs the file through OpenAI Whisper
	result = await client.loop.run_in_executor(None, recognizer.recognize_whisper, audio)
	if result == "":
		result = "*nothing*"
		
	# Send results + truncate in case the transcript is longer than 1900 characters
	if len(result) <= 1900:
		content = "✨**Audio Message Transcription:\n** ```" + result + "```"
   		await msg.edit(content=content)
	else:
		content = "✨**Audio Message Transcription (1 of 2):\n** ```" + result[:1900] + "...```"
    		await msg.edit(content=content)
		
		content = "✨**Audio Message Transcription (2 of 2):\n** ```" + result[1900:] + "```"
   		await message.channel.send(content)

def is_manager(input: discord.Interaction or discord.message) -> bool:
	if type(input) is discord.Interaction:
		user = input.user
	else:
		user = input.author
	
	if user.id in ADMIN_USERS:
		return True
	
	if ADMIN_ROLE != 0:
		admin = input.guild.get_role(ADMIN_ROLE)

		if user in admin.members:
			return True

	return False


@client.event
async def on_message(message):
	# "message.flags.value >> 13" should be replacable with "message.flags.voice" when VM support comes to discord.py, I think.
	if TRANSCRIBE_AUTOMATICALLY and message.flags.value >> 13 and len(message.attachments) == 1:
		await transcribe_message(message)

	if message.content == "!synctree" and is_manager(message):
		await tree.sync(guild=message.guild)
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
	if not is_manager(interaction):
		await interaction.response.send_message(content="You are not a Bot Manager!")
		return

	await tree.sync(guild=None)
	await interaction.response.send_message(content="Synced!")
    
@tree.context_menu(name="Transcribe VM")
async def transcribe_contextmenu(interaction: discord.Interaction, message: discord.Message):
	await interaction.response.send_message(content="Transcription started!", ephemeral=True)
	await transcribe_message(message)


if __name__ == "__main__":
	client.run(BOT_TOKEN)
