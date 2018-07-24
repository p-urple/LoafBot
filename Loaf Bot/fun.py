import discord
import random
import re
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
			await ctx.send('You have to put something before this command works')
			return
		mockedtxt = ''.join([i.lower() if random.randint(1, 100) < 51 else i.upper() for i in mocktxt])
		await ctx.send(mockedtxt)

	@commands.command()
	async def cointoss(self, ctx, headstails = None):
		"""Pick a side: heads or tails?"""
		hdict = {'h':'heads', 't':'tails', 'heads':'heads', 'tails':'tails'}
		headstails = hdict[headstails]
		if headstails not in ['heads', 'tails']:
			await ctx.send('Choose a side first')
		else:
			headstails = headstails == 'heads'
			is_heads = random.randint(0,1)
			result = 'heads' if is_heads else 'tails'
			if headstails == is_heads:
				await ctx.send(f'{ctx.message.author.mention} the result was **{result}**. Congratulations, you won!')
			else:
				await ctx.send(f'{ctx.message.author.mention} the result was **{result}**. Sorry, you lost.')

	@commands.command()
	async def reverse(self, ctx, *, text : str = None):
		"""reverses any text sent"""
		if str is None:
			await ctx.send('You have to say something before this command works')
		else:
			await ctx.send(text[::-1])

	@commands.command()
	async def dice(self, ctx, amount: str):
		"""rolls some die (6d20+3)"""
		regex = re.search(r'(\d*)d(\d+)\+?(\d*)', amount)
		number = int(regex.group(1)) if regex.group(1) != '' else 1
		dicedenom = int(regex.group(2))
		addend = int(regex.group(3)) if regex.group(3) != '' else 0
		rolls = [random.randint(1,dicedenom) for i in range(number)]
		rollsmesg = '(' + ' + '.join([str(i) for i in rolls]) + ')' + ((' + ' + str(addend)) if addend != 0 else '') + ' = '
		if rolls > 1000:
			await ctx.send('Please dont roll more than 1000 die! Bots have limits too, I either will be unable to send it or crash.')
		await ctx.send(rollsmesg + str(sum(rolls)+addend))

def setup(bot):
	bot.add_cog(Fun(bot))
