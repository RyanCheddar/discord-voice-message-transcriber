# discord-voice-message-transcriber
Discord.py bot that transcribes voice messages using OpenAI Whisper

<img width="618" alt="Screenshot 2023-04-15 at 11 38 56 PM" src="https://user-images.githubusercontent.com/44641166/232242082-af33cc32-e479-4bf8-aef6-80e6f3453226.png">

# Get Started

To use the bot, you will need to install the needed dependencies (listed in requirements.txt). There are tutorials on how to use pip to do this online.

You will also need a bot token (attainable at the [Discord Developer Portal](https://discord.com/developers/applications), which can be added at the bottom of main.py at the client.run spot. Make sure your bot has the Message Content intent, or it won't be able to read any voice messages.

Finally, at the top of main.py, you can change some settings that alter how the bot works. You will also need to add your User ID in the bot_managers variable, just so you can control the bot via commands later.

Once you have successfully started the bot, send "!synctree" in a channel the bot can see in order to get context menu functionality + slash commands working.

# Contribute & Other Stuff

Sorry for the spaghetti code, I frankly have no idea how to do voice recognition efficiently.

Feel free to make pull requests to improve stuff for the next person.

If you encounter any issues with the code, leave them in the issue tracker and someone might fix it for you.

The code is licensed under the MIT license, which probably means you can do whatever with it, so have fun :)
