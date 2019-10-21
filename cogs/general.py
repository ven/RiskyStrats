import discord
from discord.ext import commands
import aiohttp
import humanize
import datetime

class GeneralCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='help',
        help="Displays this help menu."
    )
    async def _help(self, ctx):

        embed = discord.Embed(title='🔖 **Commands**', description='All of the available commands for the bot.', colour=discord.Colour.blue())
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
        
        cog = self.bot.get_cog('GeneralCog')

        for command in cog.get_commands(): # iterate through command objs

            if command.usage:
                usage = command.usage
            else:
                usage = 'None'

            if command.aliases:
                aliases = ", ".join(command.aliases)
            else:
                aliases = 'None'

            embed.add_field(name=f'**{command.name}**', value=f'• **Description**: {command.help}\n• **Usage**: {usage}\n• **Aliases**: {aliases}', inline=False)

        await ctx.send(embed=embed)

    @commands.command(
        name='stats',
        usage='<roblox name>',
        aliases=['risky'],
        help="Displays a player's Risky Strats statistics."
        )
    async def _stats(self, ctx, name: str):

        roblox = f'https://api.roblox.com/users/get-by-username?username={name}'
        riskyURL = None

        async with aiohttp.ClientSession() as session:
            async with session.get(roblox) as resp:
                roblox_data = await resp.json(content_type=None)

                if "success" in roblox_data.keys():
                    embed = discord.Embed(title=f'**User does not exist.**', colour=discord.Colour.red())
                    await ctx.send(embed=embed)
                else:
                    riskyURL = f'https://clv.cloud/risky/getStats?UserId={roblox_data["Id"]}'
            
            if riskyURL:
                embed = discord.Embed(title=f'📊 **{roblox_data["Username"]}\'s Statistics**', description='Risky Strats Metrics', colour=discord.Colour.blue(), timestamp=datetime.datetime.utcnow())
                embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
                embed.set_footer(text='Risky Strats', icon_url=self.bot.user.avatar_url)
                embed.set_thumbnail(url=f'https://www.roblox.com/headshot-thumbnail/image?userId={roblox_data["Id"]}&width=420&height=420&format=png')

                async with session.get(riskyURL) as resp:
                    data = await resp.json(content_type=None)
                    if not data["success"]:
                        embed.add_field(name='**No data available**', value='There are no recorded statistics for this user.', inline=False) 
                    else:
                        data = data["data"]

                        Losses = data["TotalMatches"] - data["Wins"]

                        embed.add_field(name='🏆 **Wins**', value=data["Wins"])
                        embed.add_field(name='🖐 **Losses**', value=Losses)
                        embed.add_field(name='⏳ **Total Matches**', value=data["TotalMatches"])
                        embed.add_field(name='📈 **W/L Ratio**', value=round((data["Wins"] / Losses), 2))
                        embed.add_field(name='🗓 **Last Win**', value=humanize.naturaltime(datetime.datetime.fromtimestamp(data["LastWin"])))
                        embed.add_field(name='💠 **Points**', value=data["Points"])

                    await ctx.send(embed=embed)
    
    @commands.command(
        name='leaderboard',
        usage='<daily/weekly/all time>',
        aliases=['board', 'leader'],
        help="Displays the daily, weekly, or all time leaderboard for Risky Strats."
    )
    async def _leaderboard(self, ctx, *, leader_type: str=None):

        if leader_type:
            leader_type = leader_type.upper()

        if leader_type == 'DAILY':
            select = ['Daily', 'Daily']
        elif leader_type == 'WEEKLY':
            select = ['Weekly', 'Weekly']
        elif leader_type in ['ALL', 'ALL TIME', 'LIFETIME', 'EVERY', 'ALLTIME']:
            select = ['All Time', 'AllTime']
        else:
            select = ['Weekly', 'Weekly']
            name = 'Weekly'

        clvurl = f'https://clv.cloud/risky/getLeaderboard'

        async with aiohttp.ClientSession() as session:
            async with session.get(clvurl) as resp:
                clv_data = await resp.json(content_type=None)
                data = clv_data["data"]
                boards = data["Boards"]

            sortedBoard = sorted(boards[select[1]].items(), key=lambda x: x[1], reverse=True)
            sortedBoard = sortedBoard[:10]

            playerList = []
            
            for player_id, score in sortedBoard:
                robloxurl = f'https://api.roblox.com/users/{player_id}'
                async with session.get(robloxurl) as resp:
                    roblox_data = await resp.json(content_type=None)
                    name = roblox_data["Username"]

                    playerList.append([name, score])

            embed = discord.Embed(title=f'🔖 **Risky Strats Leaderboard - {select[0]}**', description=f'{select[0]} leaderboard of Risky players.', colour=discord.Colour.blue(), timestamp=datetime.datetime.utcnow())
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            embed.set_footer(text='Risky Strats', icon_url=self.bot.user.avatar_url)

            for idx, playerObj in enumerate(playerList):
                idx += 1
                emoji = ''

                if idx == 1:
                    emoji = '🥇'
                elif idx == 2:
                    emoji = '🥈'
                elif idx == 3:
                    emoji = '🥉'
                
                embed.add_field(name=f'{emoji} **{playerObj[0]}**', value=f'{playerObj[1]} wins', inline=False)

            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(GeneralCog(bot))