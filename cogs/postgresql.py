import os, signal
import discord
from discord import Webhook, File, app_commands, Status
from discord.ext import commands
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
load_dotenv()
a = subprocess.check_output('hostname').decode().strip()
if "blehh" in a:
   shardid = [0]
elif "blurggg" in a:
    shardid = [0, 1]
else:
    shardid = [1]
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.voice_states = True
intents.presences = True
bot = commands.AutoShardedBot(shard_count = 2,shard_ids = shardid,command_prefix='$', intents=intents, help_command = None, application_id=os.getenv("APP_ID"), heartbeat_timeout=120, owner_ids=[69])
db_url = os.environ['DATABASE_URL']

class databasestuff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def geturl(self, ctx: Context):
        if ctx.author.id in bot.owner_ids:
            await ctx.send(db_url)
    @commands.hybrid_command(description="INSERT INTO table (column values) VALUES ('values')")
    @commands.is_owner()
    async def write(self, ctx: Context, *, args: str):
        try:
            await ctx.defer()
            connection = psycopg2.connect(db_url)
            cursor = connection.cursor()
            query = args.strip()
            cursor.execute(query)
            connection.commit()
            cursor.close()
            connection.close()
            await ctx.send("done")
        except Exception as e:
            await ctx.send(f"{e}, {''.join(traceback.format_exception(type(e), e, e.__traceback__))}")

    @commands.hybrid_command()
    @commands.is_owner()
    async def read(self, ctx: Context, *, args: str):
        try:
            await ctx.defer()
            connection = psycopg2.connect(db_url)
            cursor = connection.cursor()
            query = args.strip()
            cursor.execute(query)
            result = cursor.fetchall()
            for row in result:
                await ctx.send(f"`{row}`")
            cursor.close()
            connection.close()
        except Exception as e:
            await ctx.send(f"{e}, {''.join(traceback.format_exception(type(e), e, e.__traceback__))}")
    
async def setup(bot):
    await bot.add_cog(databasestuff(bot))
