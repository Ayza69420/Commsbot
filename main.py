import discord
from discord.ext import commands

BOT_TOKEN = ""

intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, presences=True)
client = commands.Bot(command_prefix = '=', intents = intents)

queue = []
sessions = {}

msgs = {}

@client.event
async def on_ready():
    print('Bot is ready.')

@client.command()
async def call(ctx):
    channel = ctx.channel.id

    if channel not in sessions and channel not in queue:
        await ctx.channel.send("Waiting for an available connection.")
        queue.append(channel)
    elif channel in sessions:
        await ctx.channel.send("You are already in a connection.")
    else:
        await ctx.channel.send("You are already waiting for a connection.")

    await start_session()

@client.command()
async def hangup(ctx):
    channel = ctx.channel.id
    communicating_with = sessions[channel]

    del sessions[channel]
    del sessions[communicating_with]

    await client.get_channel(channel).send("Connection has been closed.")
    await client.get_channel(communicating_with).send("The other party hanged up.")

async def transmit(channel):
    data = msgs[channel]

    await client.get_channel(channel).send(data)
    del msgs[channel]

async def start_session():
    if len(queue) % 2 == 0 and len(queue) > 0:
        id1, id2 = queue[0], queue[1]
        
        await client.get_channel(id1).send("A connection was made!")
        await client.get_channel(id2).send("A connection was made!")

        sessions[id1], sessions[id2] = id2, id1

        queue.remove(id1)
        queue.remove(id2)
    
@client.event
async def on_message(ctx):
    channel = ctx.channel.id
    author = ctx.author

    if channel in sessions and author.id != client.user.id:
        if ctx.content != "=hangup":
            msgs[sessions[channel]] = f"**[{author}]:** {ctx.content}"
        
            await transmit(sessions[channel])

    await client.process_commands(ctx)

client.run(BOT_TOKEN)
