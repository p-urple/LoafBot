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
		dict = {'h':'heads', 't':'tails', 'heads':'heads', 'tails':'tails'}
		headstails = dict[headstails]
		if headstails not in ['heads', 'tails']:
			await ctx.send('Choose a side first')
		else:
			flip = random.choice(['tails', 'heads', 'tails', 'heads', 'tails', 'heads', 'heads', 'tails'])
			msg = f'{ctx.message.author.mention} the result was **{flip}**. Sorry, you lost.'
			if headstails == flip:
				msg = f'{ctx.message.author.mention} the result was **{flip}**. Congratulations, you won!'
			await ctx.send(msg)

	@commands.command()
	async def reverse(self, ctx, *, text : str = None):
		"""reverses any text sent"""
		if str is None:
			await ctx.send('You have to say something before this command works')
		else:
			await ctx.send(text[::-1])

'''	@commands.command()
	async def dice(self, ctx, amount):
		"""rolls some die (1d20+3)"""		
		#try:
		number = ''
		size = ''
		add = ''
		list = [number, size, add]
		x = 0
		for [i] in [amount.split('', '')]:
			if [i] == 'd':
				x = 1
				pass
			if [i] == '+':
				x = 2
				pass
			list[x] += [i]
		except:
			await ctx.send('Please make sure you use the `<amount of die>`d`<size of die>` format')
			return
		message = '('
		total = 0
		number = int(number)
		while number > 0:
			roll += random.randint(1, int(size))
			total += roll
			if int(number) != 1:
				message += f'{str(roll)} + '
			else:
				message += f'{str(roll)} '
				if add != '':
					message += f'+ {int(add)}'
					total += int(add)
			number -= 1
			total += int(add)
			message += f' = **{total}**' 
		await ctx.send(message)'''

def setup(bot):
	bot.add_cog(Fun(bot))
