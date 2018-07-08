import discord
import sqlite3
import datetime
from discord.ext import commands
from utils import *
class Utility:
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def ping(self, ctx):
		f"""returns the ping for **{self.bot.user.display_name}**"""
		await ctx.send(f'<@{ctx.message.author.id}> :ping_pong: ***PONG!*** ({bot.latency * 1000:.of} milliseconds)')

	@commands.command()
	@commands.is_owner()
	async def servers(self, ctx):
		"""a list of all the servers the bot is in"""
		counter = 0
		message = '```'
		wrap = 0
		for server in self.bot.guilds:
			if wrap < 50:
				counter += 1
				message += f'{counter}. {server.name}\n'
				wrap += 1
			elif wrap == 50:
				counter += 1
				message += f'{counter}. {server.name}```'
				wrap = 0
				await ctx.send(message)
		message += '```'
		await ctx.send(message)

	@commands.command()
	async def server(self, ctx):
		"""sends an invite to the support server"""
		await ctx.send('Join the support server at {}'.format('https://discord.gg/uJR4rcW'))

	@commands.command()
	async def invite(self, ctx):
		"""sends the OAuth2 URL used for adding the bot to a server"""
		oauth2 = 'https://discordapp.com/api/oauth2/authorize?client_id=430438798141423617&permissions=334883910&scope=bot'
		await ctx.send(f'Add the bot to your server using {oauth2}')


	@commands.command()
	async def roles(self, ctx, user : discord.Member = None):
		"""sends the list of roles for the server, or for the specified user, along with their IDs"""
		if user == None:
			object = ctx.guild.name
			convoker = ctx.message.author
			rolelist = ''
			counter = 0
			wrap = 0
			for role in ctx.guild.roles:
				if role.name == '@everyone':
					pass
				elif wrap < 21:
					rolelist += str(role.id)
					rolelist += '	---   '
					rolelist += role.name
					rolelist += '\n'
					counter += 1
					wrap += 1
				else:
					em = discord.Embed(title = f'Roles for **{object}**:' , description = rolelist, colour = 0x4cff30)
					em.set_author(name=convoker.display_name, icon_url=convoker.avatar_url)	
					await ctx.send(embed=em)
					wrap = 0

					rolelist = ''

					rolelist += str(role.id)
					rolelist += '	---   '
					rolelist += role.name
					rolelist += '\n'
					counter += 1
					wrap += 1
		else:
			object = user.display_name
			convoker = user
			rolelist = ''
			counter = 0
			wrap = 0
			for role in user.roles:
				if wrap < 21:
					rolelist += str(role.id)
					rolelist += '	---   '
					rolelist += role.name
					rolelist += '\n'
					counter += 1
					wrap += 1
				else:
					em = discord.Embed(title = f'Roles for **{object}**:' , description = rolelist, colour = 0x4cff30)
					em.set_author(name=convoker.display_name, icon_url=convoker.avatar_url)	
					await ctx.send(embed=em)
					wrap = 0

					rolelist = ''

					rolelist += str(role.id)
					rolelist += '	---   '
					rolelist += role.name
					rolelist += '\n'
					counter += 1
					wrap += 1

		rolelist += '\n **'
		rolelist += str(counter)
		rolelist += ' roles**'

		em = discord.Embed(title = f'Roles for **{object}**:' , description = rolelist, colour = 0x4cff30)
		em.set_author(name=convoker.display_name, icon_url=convoker.avatar_url)	
		await ctx.send(embed=em)

	@commands.command()
	async def prefix(self, ctx):
		"""shows the custom prefix for this server"""
		try:
			prefix = self.bot.prefixes[ctx.message.guild.id]
			await ctx.send(f'The custom prefix for this server is `{prefix}`')
		except:
			await ctx.send('The prefix for this server is `>`')

	@commands.command()
	async def uptime(self, ctx):
		"""shows current uptime"""
		em = discord.Embed(title=f'Uptime for **{self.bot.user.name}**', description=str(timedelta_str(datetime.datetime.now() - self.bot.start_time)), colour=0x23272a)
		await ctx.send(embed=em)

	@commands.command()
	async def upvote(self, ctx):
		"""sends the link to upvote the bot on discordbots.org"""
		await ctx.send('Upvote the bot at https://discordbots.org/bot/430438798141423617')

def setup(bot):
    bot.add_cog(Utility(bot))
