import discord
from discord.ext import commands
import sys, traceback
import datetime
import config
from config import *

def get_prefix(bot, message):
    prefix = '!'
    return commands.when_mentioned_or(prefix)(bot, message)

initial_extensions = [
    'cogs.general', 
    ]

bot = commands.AutoShardedBot(command_prefix=get_prefix, case_insensitive=True)

bot.remove_command('help')
bot.load_extension("jishaku")

if __name__ == '__main__':
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            traceback.print_exc()

@bot.event
async def on_ready():

    print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\nBot Version: {config.VERSION}\n')

    await bot.change_presence(status = discord.Status.online, activity=discord.Activity(type=discord.ActivityType.playing, name=f"Risky Strats"))
    print(f'Successfully logged in and booted...!')

bot.run(TOKEN, bot=True, reconnect=True)