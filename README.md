# Basic Bot
 
# Discord Ticket Bot

A simple Discord bot designed to manage support tickets using the latest Discord API features. This bot allows users to create support tickets, log conversations, and ensures a smooth ticket management process for staff.

## Features

- **Ticket Creation**: Users can create tickets in various categories with a simple button interface.
- **Private Channels**: Each ticket is created in a private channel, visible only to the ticket owner and staff members.
- **Ticket Closure**: Users and staff can close tickets, with transcripts sent to the user and logged in a designated channel.
- **Purge Command**: Staff can delete a specified number of messages from a channel.
- **Dynamic Category and Channel Creation**: Categories for tickets and a support channel are created automatically upon bot initialization.

## Requirements

- Python 3.8 or higher
- `discord.py` library (install via pip)
- A Discord bot token (create your bot on the [Discord Developer Portal](https://discord.com/developers/applications))

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/dxv3/basic-bot
   cd basic-bot

2. Install the required packages:
   ```bash
   pip install discord.py

3. Edit config.json n add your bot token:
   ```bash
{
    "TOKEN": "YOUR_BOT_TOKEN"
}

4. Run the bot:
   ```bash
    python main.py