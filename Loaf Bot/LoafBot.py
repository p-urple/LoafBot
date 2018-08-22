import discord
import asyncio
import sqlite3
import itertools
import re
import inspect
import datetime
from discord.ext import commands
from utils import *

class EmbedHelp(commands.HelpFormatter):
	def shorten(self,text):
		return text #dirty hack, but...
	async def format(self):
		"""Handles the actual behaviour involved with formatting.
		To change the behaviour, this method should be overridden.
		Returns
		--------
		list
		A paginated output of the help command.
		"""
		self._paginator = commands.Paginator(prefix = '', suffix = '')

		# we need a padding of ~80 or so

		description = self.command.description if not self.is_cog() else inspect.getdoc(self.command)

		if description:
			# <description> portion
			self._paginator.add_line(description, empty=True)

		if isinstance(self.command, commands.Command):
			# <signature portion>
			signature = self.get_command_signature()
			self._paginator.add_line(signature, empty=True)

			# <long doc> section
			if self.command.help:
				self._paginator.add_line(self.command.help, empty=True)

			# end it here if it's just a regular command
			if not self.has_subcommands():
				self._paginator.close_page()
				return self._paginator.pages

		max_width = self.max_name_size

		def category(tup):
			cog = tup[1].cog_name
			# we insert the zero width space there to give it approximate
			# last place sorting position.
			return '**' + cog + ':' + '**' if cog is not None else '\u200b**No Category:**'

		filtered = await self.filter_command_list()
		if self.is_bot():
			data = sorted(filtered, key=category)
			for category, cmds in itertools.groupby(data, key=category):
				# there simply is no prettier way of doing this.
				cmds = sorted(cmds)
				if len(cmds) > 0:
					self._paginator.add_line(category)

				self._add_subcommands_to_page(max_width, cmds)
		else:
			filtered = sorted(filtered)
			if filtered:
				self._paginator.add_line('Commands:')
				self._add_subcommands_to_page(max_width, filtered)

		# add the ending note
		self._paginator.add_line()
		ending_note = self.get_ending_note()
		self._paginator.add_line(ending_note)
		return self._paginator.pages

con = sqlite3.connect('discord.db')
c = con.cursor()

try:
	c.execute('''CREATE TABLE prefixes
			 (guildid integer, prefix string)''')
except:
	pass

bot = commands.Bot(command_prefix=get_pre, formatter = EmbedHelp())
bot.message_ids = []
bot.prefixes = dict()
load_prefixes(bot)

bot.remove_command("help")

###########################################################################################################################################################
# helpm = """**FUN COMMANDS:**																  #
# `>clap <message>`: sends a fun message with clap emojis												  #
#	`>mock <message>`: sends a fun message with letters randomly turned uppercase and lowercase							  #
#																			  #
#	**UTILITY COMMANDS:**																  #
#	`>roles [user]`: sends the list of roles for the server, or for the specified user, along with their IDs					  #
#	`>support`: sends an invite to the support server												  #
#	`>invite`: sends the OAuth2 URL used for adding the bot to a server										  #
#																			  #
#	**MODERATION ONLY:**																  #
#	`>mute <user> <s/m/h/d> [reason]`: mutes the user for the specified amount of time								  #
#	`>unmute <user>`: unmutes the specified muted user												  #
#																			  #
#	**CONFIGURATION COMMANDS:**															  #
#	`>muterole <role name>`: used to assign the role given to muted members -- *remember to us the exact role name in quotes. ("Role Name")*	  #
#	`>modlog <channel>`: used to assign the mod log to a channel											  #
#	`>publiclog <channel>`: used to assign an optional second log that shows only mutes for regular users to view					  #
#	`>starboard <channel>`: used to assign the starboard to a channel										  #
#																			  #
#	*<> = necessary		 [] = optional*"""													  #
###########################################################################################################################################################

startup_extensions = ["fun", "utility", "config", "moderation", "logs", "events"]

if __name__ == '__main__':
	for extension in startup_extensions:
		try:
			bot.load_extension(extension)
			print(f'Loaded extension {extension}.')
		except Exception as e:
			print(f'Failed to load extension {extension}.')
			print(e)
@bot.event
async def on_ready():
	print('Logged in...')
	print(discord.__version__)
	print('-----')

	modlogchannel = bot.get_channel(437263769832259618)
	lm = 'Logged in as: \n **'
	lm += bot.user.display_name
	lm += '** \n **'
	lm += str(bot.user.id)
	lm += '** \n \n Using: \n `'
	lm += 'discord.py version '
	lm += discord.__version__
	lm += '`'

	bot.start_time = datetime.datetime.now()
	await bot.change_presence(activity=discord.Game(name='>help'))

	em = discord.Embed(title=':white_check_mark: **CONNECTED**', description=lm, colour=0x9b59b6)
	em.set_author(name=bot.user.name, icon_url=bot.user.avatar_url)

	await modlogchannel.send(embed=em)

@bot.command(hidden=True)
@commands.is_owner()
async def reboot(ctx):
	"""reboots the bot"""
	try:
		await ctx.send('Bot is being rebooted')
		await bot.clear()
		await bot.connect(reconnect=True)
	except:
		await ctx.send('Reboot failed')

@bot.command(name='load', hidden=True)
@commands.is_owner()
async def cog_load(ctx, *, cog: str):
	"""loads a module."""
	bot.load_extension(cog)
	await ctx.send(f'Loaded the `{cog}` cog')
	print(f'Loaded extenstion {cog}')

@bot.command(name='unload', hidden=True)
@commands.is_owner()
async def cog_unload(ctx, *, cog: str):
	"""unloads a module."""
	bot.unload_extension(cog)
	await ctx.send(f'Unloaded the `{cog}` cog')
	print(f'Unloaded extension {cog}')

@bot.command(name='reload', hidden=True)
@commands.is_owner()
async def cog_reload(ctx, *, cog: str):
	"""reloads a module."""
	bot.unload_extension(cog)
	bot.load_extension(cog)
	await ctx.send(f'Reloaded the `{cog}` cog')
	print(f'Reloaded extension {cog}')

@bot.event
async def on_command_error(ctx,error):
	if isinstance(error, commands.errors.MissingPermissions):
		await ctx.send(':x: You do not have permission to use this command!')
	elif isinstance(error, discord.Forbidden):
		await ctx.send(':x: Error 403: You or the bot may be forbidden from using that command!')
	elif isinstance(error, commands.errors.MissingRequiredArgument):
		await ctx.send(str(error) + " Use >help <command> to see all required arguments.")
	elif isinstance(error, commands.errors.CommandNotFound):
		return
	else:
		await ctx.send(f'{error}')
	print(f'''In {ctx.guild.name} ({ctx.guild.id}):
	{error}''')

_mentions_transforms = {
    '@everyone': '@\u200beveryone',
    '@here': '@\u200bhere'
}
_mention_pattern = re.compile('|'.join(_mentions_transforms.keys()))

@bot.command(name='help')
async def help(ctx, *cmds : str):
	"""shows this message."""
	bot = ctx.bot
	destination = ctx.message.author if bot.pm_help else ctx.message.channel

	def repl(obj):
		return _mentions_transforms.get(obj.group(0), '')

	# help by itself just lists our own commands.
	if len(cmds) == 0:
		pages = await bot.formatter.format_help_for(ctx, bot)
	elif len(cmds) == 1:
		# try to see if it is a cog name
		name = _mention_pattern.sub(repl, cmds[0])
		command = None
		if name in bot.cogs:
			command = bot.cogs[name]
		else:
			command = bot.all_commands.get(name)
			if command is None:
				await destination.send(bot.command_not_found.format(name))
				return

		pages = await bot.formatter.format_help_for(ctx, command)
	else:
		name = _mention_pattern.sub(repl, cmds[0])
		command = bot.all_commands.get(name)
		if command is None:
			await destination.send(bot.command_not_found.format(name))
			return

		for key in cmds[1:]:
			try:
				key = commands._mention_pattern.sub(repl, key)
				command = command.all_commands.get(key)
				if command is None:
					await destination.send(bot.command_not_found.format(key))
					return
			except AttributeError:
				await destination.send(bot.command_has_no_subcommands.format(command, key))
				return

		pages = await bot.formatter.format_help_for(ctx, command)

	if bot.pm_help is None:
		characters = sum(map(lambda l: len(l), pages))
		# modify destination based on length of pages.
		if characters > 1000:
			destination = ctx.message.author

	for page in pages:
		em = discord.Embed(title = (", ".join(cmds) if len(cmds) != 0 else "Help"), description = page, colour=0x9b59b6)
		em.set_author(name=bot.user.name, icon_url=bot.user.avatar_url)
		await destination.send(embed = em)


bot.run(open('token.txt','r').read())
