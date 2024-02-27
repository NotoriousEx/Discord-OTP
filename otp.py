import os
import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from twilio.rest import Client
import requests
import asyncio

# Initialize Discord bot
bot = commands.Bot(command_prefix='!')
slash = SlashCommand(bot, sync_commands=True)

# Initialize Twilio client
twilio_client = Client("TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN")

# Sellix API endpoint and API key
SELLIX_API_ENDPOINT = "https://api.sellix.io/v1"
SELLIX_API_KEY = "YOUR_SELLIX_API_KEY"

# Mapping of keys to roles
KEY_ROLE_MAPPING = {
    "KEY1": 123456789012345678,  # Role ID for Key1
    "KEY2": 123456789012345679,  # Role ID for Key2
    # Add more key-role mappings as needed
}

# Function to initiate a call
async def initiate_call(cell_phone):
    call = twilio_client.calls.create(
        url="YOUR_NGROK_URL/voice",
        to=cell_phone,
        from_="YOUR_TWILIO_PHONE_NUMBER"
    )
    return call.sid

# Function to handle OTP verification
async def handle_otp(call_sid):
    # Wait for OTP retrieval logic (You need to implement this logic)
    await asyncio.sleep(5)  # Simulated delay for OTP retrieval
    otp = "123456"  # Simulated OTP
    return otp

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@slash.slash(
    name='redeem',
    description='Redeem a key to access the bot',
    guild_ids=[YOUR_SERVER_ID],  # Replace with your server ID
    options=[
        {
            "name": "key",
            "description": "The key to redeem",
            "type": 3,
            "required": True
        }
    ]
)
async def redeem_key(ctx, key: str):
    # Verify key validity via Sellix API
    response = requests.get(f"{SELLIX_API_ENDPOINT}/products/keys/{key}", headers={"Authorization": f"Bearer {SELLIX_API_KEY}"})
    if response.status_code == 200:
        # Key is valid, grant role to user
        role_id = KEY_ROLE_MAPPING.get(key.upper())
        if role_id:
            role = ctx.guild.get_role(role_id)
            if role:
                await ctx.author.add_roles(role)
                await ctx.send(f"Key redeemed successfully! You now have access to the bot.")
            else:
                await ctx.send("Error: Role not found.")
        else:
            await ctx.send("Error: Role not mapped for this key.")
    elif response.status_code == 404:
        await ctx.send("Error: Invalid key.")
    else:
        await ctx.send("Error: Unable to validate key.")

@slash.slash(
    name='call',
    description='Initiate a call',
    guild_ids=[YOUR_SERVER_ID],  # Replace with your server ID
    options=[
        {
            "name": "cell_phone",
            "description": "The cell phone number to call",
            "type": 3,
            "required": True
        }
    ]
)
async def call(ctx, cell_phone: str):
    await ctx.send(f'Initiating call to {cell_phone}...')
    call_sid = await initiate_call(cell_phone)
    await ctx.send('Call initiated. Waiting for OTP...')
    otp = await handle_otp(call_sid)
    if otp:
        await ctx.send(f'OTP retrieved: {otp}')
    else:
        await ctx.send('Failed to retrieve OTP.')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandNotFound):
        await ctx.send("Error: Command not found.")
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send("Error: Missing required argument.")
    else:
        await ctx.send(f"An error occurred: {error}")

bot.run("YOUR_DISCORD_BOT_TOKEN")