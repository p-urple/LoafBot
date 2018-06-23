import discord
import random
from discord.ext import commands

class Fun:
	def __init__(self, bot):
		self.bot = bot
	
	@commands.command()
	async def clap(self, ctx, *, sentence : str = None):
		"""sends a fun message with clap emojis"""
		if sentence is None:
			await ctx.send('You have to put something befor this command works')
			return
		sentencetemp = ':clap:' + sentence.replace(' ', ':clap:') + ':clap:'
		await ctx.send(sentencetemp)

	@commands.command()
	async def smh(self, ctx, *, headshake : str = None):
		"""smh..."""
		if headshake is None:
			await ctx.send('You have to put something befor this command works')
			return
		headshake = headshake.replace('smh', 'smh my head') + ' smh'
		await ctx.send(headshake)

	@commands.command()
	async def mock(self, ctx, *, mocktxt : str = None):
		"""sends a fun message with letters randomly turned uppercase and lowercase"""
		if mocktxt is None:
			await ctx.send('You have to put something befor this command works')
			return
		mockedtxt = ''.join([i.lower() if random.randint(1, 100) < 51 else i.upper() for i in mocktxt])
		await ctx.send(mockedtxt)

	@commands.command()
	async def cointoss(self, ctx, headstails = None):
		"""Pick a side: heads or tails?"""
		if headstails not in ['heads', 'tails', 'h', 't']:
			await ctx.send('Choose a side first')
		else:
			flip = random.choice(['Tails', 'Heads', 'Tails', 'Heads', 'Tails', 'Heads', 'Heads', 'Tails'])
			msg = f'{ctx.message.author.mention} the result was **{flip}**. Sorry, you lost.'
			if headstails == 'heads' or headstails == 'h':
				if flip == 'Heads':
					msg = f'{ctx.message.author.mention} the result was **{flip}**. Congradulations, you won!'
			elif headstails == 'tails' or headstails == 't':
				if flip == 'Tails':
					msg = f'{ctx.message.author.mention} the result was **{flip}**. Congradulations, you won!'
			await ctx.send(msg)

def setup(bot):
	bot.add_cog(Fun(bot))
