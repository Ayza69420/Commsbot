import discord
from discord.ext import commands

BOT_TOKEN = ""

intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, presences=True)
client = commands.Bot(command_prefix = '=', intents = intents)

queue = []
ids = {}

packets = {}

@client.event
async def on_ready():
    print('Bot is ready.')

@client.command()
async def call(ctx):
    channel = ctx.channel.id

    if channel not in ids and channel not in queue:
        await ctx.channel.send("Waiting for an available connection.")
        queue.append(channel)
    elif channel in ids:
        await ctx.channel.send("You are already in a connection.")
    else:
        await ctx.channel.send("You are already waiting for a connection.")

    await create_connection()

@client.command()
async def hangup(ctx):
    channel = ctx.channel.id
    communicating_to = ids[channel]

    del ids[channel]
    del ids[communicating_to]

    await client.get_channel(channel).send("Connection has been closed.")
    await client.get_channel(communicating_to).send("The other party hanged up.")

async def transmit(channel):
    data = packets[channel]

    await client.get_channel(channel).send(data)
    del packets[channel]

async def create_connection():
    if len(queue) % 2 == 0 and len(queue) > 0:
        id1, id2 = queue[0], queue[1]
        
        await client.get_channel(id1).send("A connection was made!")
        await client.get_channel(id2).send("A connection was made!")

        ids[id1], ids[id2] = id2, id1

        queue.remove(id1)
        queue.remove(id2)
    
@client.event
async def on_message(ctx):
    channel = ctx.channel.id
    author = ctx.author

    if channel in ids and author.id != client.user.id:
        if ctx.content != "=hangup":
            packets[ids[channel]] = f"**[{author}]:** {ctx.content}"
        
            await transmit(ids[channel])

    await client.process_commands(ctx)

client.run(BOT_TOKEN)
