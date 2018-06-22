import discord
import random
from discord.ext import commands

class Fun:
    def __init__(self, bot):
        self.bot = bot
	
    @commands.command()
    async def clap(self, ctx, *, sentence : str = None):
        """sends a fun message with clap emojis"""
        sentencetemp = ':clap:' + sentence.replace(' ', ':clap:') + ':clap:'
        await ctx.send(sentencetemp)

    @commands.command()
    async def smh(self, ctx, *, headshake : str = None):
        """smh..."""
        headshake = headshake.replace('smh', 'smh my head') + ' smh'
        await ctx.send(headshake)

    @commands.command()
    async def mock(self, ctx, *, mocktxt : str = None):
        """sends a fun message with letters randomly turned uppercase and lowercase"""
        mockedtxt = ''.join([i.lower() if random.randint(1, 100) < 51 else i.upper() for i in mocktxt])
        await ctx.send(mockedtxt)

def setup(bot):
    bot.add_cog(Fun(bot))
