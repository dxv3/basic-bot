import discord
from discord.ext import commands
from discord.ui import Button, View
from discord import app_commands
import json
import os

# Load token from config.json
with open('config.json') as f:
    config = json.load(f)

TOKEN = config['TOKEN']

# Create intents and bot instance
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

SUPPORT_CHANNEL_NAME = "support"
LOGS_CHANNEL_NAME = "logs"
TICKET_DATA_FILE = 'ticket_data.json'

ticket_categories_names = ["General Support", "Billing Support", "Technical Support"]
ticket_categories = {}
roles_that_can_approve = [123456789012345678, 234567890123456789]
admin_role = 987654321098765432

# Load ticket data if available
if os.path.exists(TICKET_DATA_FILE):
    with open(TICKET_DATA_FILE, 'r') as f:
        ticket_data = json.load(f)
else:
    ticket_data = {
        "user_tickets": {},
        "ticket_embed": None
    }

user_tickets = ticket_data["user_tickets"]


class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        for category_name in ticket_categories_names:
            self.add_item(Button(label=category_name, style=discord.ButtonStyle.primary, custom_id=category_name))


class TicketCloseView(View):
    def __init__(self, ticket_owner: discord.Member):
        super().__init__(timeout=None)
        self.ticket_owner = ticket_owner

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user

        # Fetch all messages in the current channel
        messages = [msg async for msg in interaction.channel.history(limit=None)]  # Use list comprehension

        transcript = "\n".join([f"{msg.author.name}: {msg.content}" for msg in messages])

        # Send transcript to the user
        try:
            await self.ticket_owner.send(f"Here is the transcript of your ticket:\n\n{transcript}")
        except discord.Forbidden:
            pass  # Can't DM the user, likely they have DMs off

        # Send transcript to the logs channel
        logs_channel = discord.utils.get(interaction.guild.channels, name=LOGS_CHANNEL_NAME)
        if logs_channel:
            await logs_channel.send(f"Ticket Transcript for {self.ticket_owner.name}:\n\n{transcript}")

        # Delete the ticket channel and remove the ticket from tracking
        await interaction.channel.delete()
        del user_tickets[self.ticket_owner.id]
        save_ticket_data()


def save_ticket_data():
    # Save user tickets to the file
    ticket_data = {
        "user_tickets": user_tickets,
    }
    with open(TICKET_DATA_FILE, 'w') as f:
        json.dump(ticket_data, f)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")

        # Check if support and logs channels exist, create if not
        guild = bot.guilds[0]
        support_channel = discord.utils.get(guild.channels, name=SUPPORT_CHANNEL_NAME)
        if support_channel is None:
            await guild.create_text_channel(SUPPORT_CHANNEL_NAME)

        logs_channel = discord.utils.get(guild.channels, name=LOGS_CHANNEL_NAME)
        if logs_channel is None:
            await guild.create_text_channel(LOGS_CHANNEL_NAME)
        
        # Load ticket system if needed
        if support_channel:
            if ticket_data.get("ticket_embed"):
                embed = discord.Embed.from_dict(ticket_data["ticket_embed"])
                await support_channel.send(embed=embed, view=TicketView())
                print("Restored the ticket system.")
            else:
                print("No ticket system to restore.")
    
    except Exception as e:
        print(f"Failed to sync commands: {e}")


@bot.tree.command(name="create_ticket_system", description="Create the ticket system with buttons")
async def create_ticket_system(interaction: discord.Interaction):
    support_channel = discord.utils.get(interaction.guild.channels, name=SUPPORT_CHANNEL_NAME)
    if support_channel is None:
        support_channel = await interaction.guild.create_text_channel(SUPPORT_CHANNEL_NAME)

    for category_name in ticket_categories_names:
        category = discord.utils.get(interaction.guild.categories, name=category_name)
        if category is None:
            new_category = await interaction.guild.create_category(category_name)
            ticket_categories[category_name] = new_category.id
        else:
            ticket_categories[category_name] = category.id

    # Create an embed for the ticket message
    embed = discord.Embed(
        title="Support Tickets",
        description="Click on a button below to create a ticket in the respective category.",
        color=discord.Color.dark_grey()
    )
    embed.set_footer(text="You can only have one ticket open at a time.")

    ticket_data["ticket_embed"] = embed.to_dict()
    save_ticket_data()

    await support_channel.send(embed=embed, view=TicketView())
    await interaction.response.send_message(f"Ticket system initialized in {support_channel.mention}", ephemeral=True)


@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        category_name = interaction.data['custom_id']

        if category_name in ticket_categories:
            if interaction.user.id in user_tickets:
                await interaction.response.send_message("You already have a ticket open.", ephemeral=True)
            else:
                category = discord.utils.get(interaction.guild.categories, id=int(ticket_categories[category_name]))
                ticket_channel = await interaction.guild.create_text_channel(
                    f"{interaction.user.name}-ticket",
                    category=category,
                    topic=f"Ticket for {interaction.user.name} in {category_name} category"
                )
                user_tickets[interaction.user.id] = ticket_channel.id  # Store channel ID instead of the object

                # Set private permissions for the ticket (user, staff, and admins only)
                await ticket_channel.set_permissions(interaction.user, read_messages=True, send_messages=True)
                for role_id in roles_that_can_approve:
                    role = discord.utils.get(interaction.guild.roles, id=role_id)
                    if role:
                        await ticket_channel.set_permissions(role, read_messages=True, send_messages=True)
                await ticket_channel.set_permissions(interaction.guild.default_role, read_messages=False)

                # Embed for the ticket
                embed = discord.Embed(
                    title=f"{category_name} Ticket",
                    description=f"Ticket created by {interaction.user.mention}. Staff will be with you shortly.",
                    color=discord.Color.dark_grey()
                )
                embed.set_footer(text="To close this ticket, press the button below.")

                await ticket_channel.send(embed=embed, view=TicketCloseView(interaction.user))
                await interaction.response.send_message(f"Ticket created: {ticket_channel.mention}", ephemeral=True)
                save_ticket_data()  # Save the updated ticket data


@bot.tree.command(name="purge", description="Deletes a specified number of messages.")
@app_commands.checks.has_permissions(manage_messages=True)
async def purge(interaction: discord.Interaction, amount: int):
    await interaction.response.send_message(f"Purging {amount} messages...", ephemeral=False)
    deleted = await interaction.channel.purge(limit=amount + 1)  # +1 to include the purge command itself
    await interaction.followup.send(f"Purged {len(deleted) - 1} messages.")  # -1 to exclude the initial message


@purge.error
async def purge_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
    elif isinstance(error, app_commands.errors.CommandInvokeError):
        await interaction.response.send_message("An error occurred. Please provide a valid number of messages.", ephemeral=True)


bot.run(TOKEN)
