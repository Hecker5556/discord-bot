import os, signal
import discord
from discord import Webhook, File, app_commands, Status
from discord.ext import commands, tasks
from discord.ext.commands import Context
import requests
import json
import asyncio
import subprocess
import json
import re
import sys
from dotenv import load_dotenv
from PIL import Image, ImageSequence
import traceback
from datetime import datetime, timedelta
import time
import random
import aiohttp
import aiofiles
# import ffmpeg
import openai
from yt_dlp import YoutubeDL
import psycopg2
# from commands import Bot
load_dotenv()
process = None
a = subprocess.check_output('hostname').decode().strip()
if "bleh in a:
   shardid = [0]
elif "blurghhh" in a:
    shardid = [0, 1]
else:
    shardid = [1]
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.voice_states = True
intents.presences = True
def prefix1():
     return '$'
bot = commands.AutoShardedBot(shard_count = 2,shard_ids = shardid,command_prefix='$', intents=intents, help_command = None, application_id=os.getenv("APP_ID"), heartbeat_timeout=120, owner_ids=[69])


        
token = os.getenv("TOKEN")
@bot.event
async def on_ready():
        activity = discord.Activity(
        type=discord.ActivityType.competing,
        name="getting ripped"
        )
        if sys.platform.startswith('linux'):
            process = subprocess.Popen(['apt-get', 'update'], stdin=subprocess.PIPE)
            stdout, _ = process.communicate(input=b'y\n')
            process2 = subprocess.Popen(['apt', 'install', 'ffmpeg'], stdin=subprocess.PIPE)
            stdout, _ = process2.communicate(input=b'\n')
        await bot.change_presence(activity=activity)
        await bot.user.edit()
        # await bot.tree.sync()
        channel = await bot.fetch_channel(949000882853400699)
        await channel.send(f"ready! {bot.shard_ids}")
        print("Ready!")


@bot.event
async def on_error(event, *args, **kwargs):
    print(f"Error occurred in event {event}")
    traceback.print_exception(type(event), event, event.__traceback__)


@bot.event
async def on_command_error(ctx, error):
    print(f"Error occurred while executing command: {error}")
    traceback.print_exception(type(error), error, error.__traceback__)


@bot.command()
async def ping(ctx: Context):
     latencies = []
     for i in bot.latencies:
          latencies.append((f"{round(i[1] * 1000)}ms ping", f"shard: {i[0]}"))
     print(latencies)
     await ctx.send('\n'.join(' '.join(i) for i in latencies))

@bot.command()
async def reload(ctx: Context):
     if ctx.author.id in bot.owner_ids:
          await bot.reload_extension('cogs.commands')
          await bot.reload_extension('cogs.postgresql')
          await ctx.send("reloaded")


@bot.tree.command()
async def getfile( ctx: discord.Interaction, attach: discord.Attachment):
    if ctx.user.id in bot.owner_ids:
        try:
            await ctx.response.defer()
            print(attach.filename, attach.url)
            await ctx.followup.send(f"{attach.filename}, {attach.url}")
            filelist = os.listdir("cogs/")
            print(filelist)
            await ctx.followup.send(filelist)
            if attach.filename not in filelist:
                await ctx.followup.send("not a file")
                return
            else:
                for i in filelist:
                    print(i)
                    if attach.filename in i:
                        directory = i
                        print(directory)
                        await ctx.followup.send(directory)

            with open(f"cogs/{directory}", "wb") as f2:
                f2.write(await attach.read())
                await ctx.followup.send("written file")
                
                await ctx.followup.send("done!, now editing database")
        except Exception as e:
                await ctx.followup.send(''.join(traceback.format_exception(type(e), e, e.__traceback__)))
        try:
            connection = psycopg2.connect(db_url)
            cursor = connection.cursor()
            hostname = subprocess.check_output('hostname').decode().strip()
            query = f"INSERT INTO fileedits (rand, host, url, file) VALUES ('{1}', '{hostname}', '{attach.url}', '{attach.filename}')"
            cursor.execute(query)
            connection.commit()
            cursor.close()
            connection.close()
            await bot.reload_extension(f"cogs.{directory.replace('.py', '')}")
        except Exception as e:
            await ctx.followup.send(f"{e}, {''.join(traceback.format_exception(type(e), e, e.__traceback__))}")

    else:
        await ctx.response.send_message("youre not allowed.")


db_url = os.environ['DATABASE_URL']
@tasks.loop(seconds=5)
async def check_database_edits():
    print("checking database")
    try:
        # Establish a connection to the PostgreSQL database
        connection = psycopg2.connect(db_url)
        cursor = connection.cursor()

        # Execute a query to check for edits
        query = "SELECT host, url, file FROM fileedits WHERE rand = 1"
        cursor.execute(query)
        result = cursor.fetchone()
        if result:
            host, url, file = result
            print(result)
        else:
            # channel = bot.get_channel(949000882853400699)
            print("no result")
        
        current = f"{host}{url}{file}" if result else ""
        async with aiofiles.open('previous.txt', 'r') as f1:
            previous = await f1.read()

        try:
            if current != previous:
                print("Database has been edited")
                channel = bot.get_channel(949000882853400699)
                await channel.send("database edited!!")
                hostname = subprocess.check_output('hostname').decode().strip()
                if host != hostname:
                    r = requests.get(url)
                    print(url)
                    with open(f"cogs/{file}", "wb") as f1:
                        f1.write(r.content)
                await bot.reload_extension(f'cogs.{file.replace(".py", "")}')
                print(f'cogs.{file.replace(".py", "")}')
                channel = bot.get_channel(949000882853400699)
                await channel.send("successfully reloaded!!!")
                cursor.execute("DELETE FROM fileedits WHERE rand = 1")
                connection.commit()
            else:
                previous = f"{host}{url}{file}" if result else ""
        except Exception as e:
            print(traceback.print_exception(type(e), e, e.__traceback__))
            channel = bot.get_channel(949000882853400699)
            await channel.send(traceback.format_exception(type(e), e, e.__traceback__))

        cursor.close()
        connection.close()

    except Exception as e:
        print(f"An error occurred while checking the database: {str(e)}")

async def main():
    await bot.load_extension('cogs.commands')
    await bot.load_extension('cogs.postgresql')
    async with bot:
        check_database_edits.start()
        await bot.start(token)
asyncio.run(main()) 
