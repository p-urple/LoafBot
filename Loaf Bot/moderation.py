import discord
from discord.ext import commands
import datetime
import asyncio
from utils import *

class Moderation:
	def __init__(self, bot):
		self.bot = bot				

	@commands.command()
	@commands.has_permissions(kick_members=True)
	async def kick(self, ctx, user : discord.Member, *, reason = None):
		"""kicks the user"""
		if user.id == 430438798141423617 or user.id == 459174398889295882:
			await ctx.send("Please don't hurt me...")
			return
		if ctx.message.author == user:
			await ctx.send("Why are you hitting yourself?")
			return
		await ctx.guild.kick(user, reason=reason)

		title = f'{ctx.message.author.display_name} kicked {user.name} ({user.id})'
		message = ''
		if reason != None:
			message += f'\n{reason}'

		em = discord.Embed(title=title, description=message, colour=0x0012d8)
		em.set_author(name=user.display_name, icon_url=user.avatar_url)
		await send_publiclogs(self.bot, ctx.guild, embed=em)

	@commands.command()
	@commands.has_permissions(kick_members=True)
	async def softban(self, ctx, user : discord.Member, *, reason = None):
		"""bans then unbans the user, deleting all their recent messges"""
		if user.id == 430438798141423617:
			await ctx.send("Please don't hurt me...")
			return
		if ctx.message.author == user:
			await ctx.send("Why are you hitting yourself?")
			return
		self.bot.banned = user.id
		await ctx.guild.ban(user, reason=reason)
		await ctx.guild.unban(user, reason=reason)

		title = f'{ctx.message.author.display_name} softbanned {user.name} ({str(user.id)})'
		message = ''
		if reason != None:
			message += f'\n{reason}'

		em = discord.Embed(title=title, description=message, colour=0x2454a0)
		em.set_author(name=user.display_name, icon_url=user.avatar_url)
		await send_publiclogs(self.bot, ctx.guild, embed=em)

	@commands.command()
	@commands.has_permissions(ban_members=True)
	async def ban(self, ctx, user : discord.Member, *, reason = None):
		"""bans the user"""
		if user.id == 430438798141423617:
			await ctx.send("Please don't hurt me...")
			return
		if ctx.message.author == user:
			await ctx.send("Why are you hitting yourself?")
			return
		self.bot.banned = user.id
		await ctx.guild.ban(user, reason=reason)

		title = f'{ctx.message.author.display_name} banned {user.name} ({str(user.id)})'
		message = ''
		if reason != None:
			message += f'\n{reason}'

		em = discord.Embed(title=title, description=message, colour=0x00086b)
		em.set_author(name=user.display_name, icon_url=user.avatar_url)
		await send_publiclogs(self.bot, ctx.guild, embed=em)

	@commands.command(pass_context=True)
	@commands.has_permissions(manage_messages=True)
	async def mute(self, ctx, user : discord.Member, time : int, denomination : str, *, reason : str = None):
		"""mutes the user for the specified amount of time"""
		if denomination in ['s', 'm', 'h', 'd', 'second', 'minute', 'hour', 'day', 'seconds', 'minutes', 'hours', 'days']:
			if denomination in ['second', 'seconds']:
				denomination = 's'
			if denomination in ['minute', 'minutes']:
				denomination = 'm'
			if denomination in ['hour', 'hours']:
				denomination = 'h'
			if denomination in ['day', 'days']:
				denomination = 'd'
			role = get_muterole(ctx.guild)
			if role in user.roles:
				umention = user.mention
				already = umention
				already += ' has already been muted'
				await ctx.send(already)
			else:
				await user.add_roles(role)
				umention = user.mention
				if reason is None:
					muted = umention
					muted += ' was muted for '
					muted += str(time)
					muted += denomination
				else:
					muted = umention
					muted += ' was muted for '
					muted += str(time)
					muted += denomination
					muted += ' (`'
					muted += reason
					muted += '`)'

				await ctx.send(muted)
				await send_publiclogs(self.bot, ctx.guild, muted)
				timedenoms = {'s':1, 'm':60, 'h':3600, 'd':86400}
				t = time * timedenoms[denomination]
				await asyncio.sleep(t)
				if role in user.roles:
					await user.remove_roles(role)
					await send_publiclogs(self.bot, ctx.guild, f'{user.mention} is no longer muted.')

		else:
			await ctx.send('Correct usage is: >mute <user> <time integer> <s/m/h/d> [reason]')

	@commands.command()
	@commands.has_permissions(manage_messages=True)
	async def unmute(self, ctx, user: discord.Member):
		"""unmutes the specified muted user"""
		role = get_muterole(ctx.guild)
		umention = user.mention
		if role in user.roles:
			await user.remove_roles(role)
			await ctx.send(umention + ' is no longer muted.')
			await send_publiclogs(self.bot, ctx.guild, user.mention + ' is no longer muted.')
		else:
			await ctx.send(umention + ' is not muted.')

	@commands.command()
	@commands.has_permissions(manage_messages=True)
	async def purge(self, ctx, amount : int = None):
		"""purges the specified amount of messages in the channel it is used"""
		if amount is None:
			await ctx.send('Please give an amount')
		elif amount == 1:
			await ctx.send('Just delete it yourself, silly')
		else:
			message_limit = amount + 1
			self.bot.messages = []
			async for message in ctx.message.channel.history(limit=message_limit):
				self.bot.messages.append(message.id)
			await ctx.message.channel.purge(limit=message_limit, bulk=True)
			message = await ctx.send(f':white_check_mark: **{str(amount)}** messages deleted', delete_after=5)

			em=discord.Embed(title=f'{amount} messages were purged in #{ctx.message.channel.name}', colour=0x878b91)
			em.set_author(name=ctx.message.author.display_name, icon_url=ctx.message.author.avatar_url)

			await send_modlogs(self.bot, ctx.guild, embed=em)

def setup(bot):
	bot.add_cog(Moderation(bot))
