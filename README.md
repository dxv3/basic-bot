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
   git clone <repository-url>
   cd <repository-directory>
Install the required packages:

bash
Copy code
pip install discord.py
Create a config.json file in the project directory with your bot token:

json
Copy code
{
    "TOKEN": "YOUR_BOT_TOKEN"
}
Run the bot:

bash
Copy code
python main.py