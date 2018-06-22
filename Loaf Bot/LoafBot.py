import discord
import asyncio
import sqlite3
import itertools
import re
import inspect
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



bot = commands.Bot(command_prefix= '>', formatter = EmbedHelp())
con = sqlite3.connect('discord.db')
con.row_factory = sqlite3.Row

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
	
startup_extensions = ["fun", "utility", "config", "moderation"]

if __name__ == '__main__':
	for extension in startup_extensions:
		try:
			bot.load_extension(extension)
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
	
	em = discord.Embed(title=':white_check_mark: **CONNECTED**', description=lm, colour=0x9b59b6)
	em.set_author(name=bot.user.name, icon_url=bot.user.avatar_url)

	await modlogchannel.send(embed=em)

@bot.event
async def on_guild_join(guild):
	sid = str(guild.id)
	c = con.cursor()
	try:
		c.execute('SELECT * FROM guilds WHERE guildid=(?)', (sid,))
	except:
		guildinfo = (sid, None, None, None, None)
		try:
			c.execute('INSERT INTO guilds VALUES (?, ?, ?, ?, ?)', guildinfo)
		except:
			c.execute('''CREATE TABLE guilds
						 (guildid integer, publiclogs integer, modlogs integer, starboard integer, muterole integer)''')
			c.execute('INSERT INTO guilds VALUES (?, ?, ?, ?, ?)', guildinfo)
	con.commit()

	guild.system_channel.send('Hi! The bot is designed for maximum customizability and therefore has a small (optional) setup in order to use all features.	 Use `>help` to get started.')


	
@bot.event
async def on_member_join(member):
	uid = member.id
	gid = member.guild.id
	c = con.cursor()
	if member.bot == True:
		return

	try:												   
		for i in c.execute('SELECT * FROM users WHERE uid=(?) AND gid=?', (uid, gid)):				     
			addsuccess = []								      
			addfail = []								      
			
			role = discord.utils.get(member.guild.roles, id=i[2])			 
			try:								      
				member.add_roles(role)
				addsuccess.append(role.name)
			except:
				addfail.append(role.name)				      
		message = '**Successfully Restored:** \n'
		for i in addsuccess:
			message += i + '\n'

		message += '\n'
		message += '**Unsuccessfully Restored:** \n'
		for i in addfail:
			message += i + '\n'
		em2 = discord.Embed(title=None, description=message, color=0x23272a)
		em2.set_author(name=member.display_name, icon_url=member.avatar_url)
		c.execute('DELETE FROM users WHERE uid=? AND gid=?', (uid, gid))
		returning = True
	except:
		returning = False
	
	mc = len([x for x in member.guild.members if not x.bot])

	des = '**Member:** '
	des += member.mention + '\n'
	des += '**ID:** '
	des += str(member.id) + '\n'
	des += '**Member Count:** '
	des += str(mc) + '\n'

	em = discord.Embed(title = 'Member Joined: \n \n', description=des, colour=0x51cc72)
	em.set_author(name=member.display_name, icon_url=member.avatar_url)

	await send_modlogs(bot, member.guild, embed = em)
	if returning:
		await send_modlogs(bot, member.guild, embed = em2)
	
	con.commit()

@bot.event
async def on_member_remove(member):
	c = con.cursor()
	uid = member.id
	gid = member.guild.id
	roles = [role.id for role in member.roles] 
	many = [(uid, gid, role) for role in roles]
	try:
		c.executemany("INSERT INTO users VALUES (?, ?, ?)", many)
	except:
		c.execute('''CREATE TABLE users
		(uid integer, gid integer, role integer)''')
		c.executemany("INSERT INTO users VALUES (?, ?, ?)", many)
	if member.bot == True:
		return

	mc = len([x for x in member.guild.members if not x.bot]) #consider refactoring into method

	des = '**Member:** '
	des += member.mention + '\n'
	des += '**ID:** '
	des += str(member.id) + '\n'
	des += '**Member Count:** '
	des += str(mc) + '\n'
	
	em = discord.Embed(title='Member Left: \n \n', description=des, colour=0xe74c3c)
	em.set_author(name=member.display_name, icon_url=member.avatar_url)
	await send_modlogs(bot, member.guild, embed = em)
	con.commit()

@bot.event
async def on_raw_reaction_add(reaction, messageid, channelid, member):
	c = con.cursor()
	reactchannel = bot.get_channel(channelid)
	message = await reactchannel.get_message(messageid)
	if member == bot.user.id or message.author.bot == True:
		return
	if reaction.count is 7 and reaction.name == '⭐' and str(messageid) not in open('bestof.txt').readlines():
		print('bestof')
		em = discord.Embed(title=':ok_hand: Nice :ok_hand:', description=message.content, colour=0xbc52ec)
		em.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
		em.set_footer(text='This meme recieved enough stars to make it into #bestof')
		set_embed_image_to_message_image(em,message)	
		await send_starboard(bot, message.guild, embed = em)
		cache = open("bestof.txt", "a+",encoding="utf8") 
		cache.write(str(messageid) + '\n')
		cache.close()
		con.commit()
		   

@bot.event
async def on_message_delete(message):
	c = con.cursor()
	if message.author.bot is True:
		return
	channel = message.channel.name

	mc = 'Deleted Message in #' + str(channel) + ':'

	em = discord.Embed(title=mc, description=message.content, colour=0xe74c3c)
	em.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
	set_embed_image_to_message_image(em,message)	


	await send_modlogs(bot, message.guild, embed = em)

	con.commit()



@bot.event
async def on_message_edit(message, after):
	c = con.cursor()
	if message.author.bot or message.content == after.content:
		return
	
	channel = message.channel.name

	mc = 'Edited Message in #' + channel + ':'
	
	me = '**Old Message:** \n'
	me += message.content
	me += '\n \n'
	me += '**New Message:** \n'
	me += after.content

	em = discord.Embed(title=mc, description=me, colour=0xFFD700)
	em.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
	set_embed_image_to_message_image(em, message)

	await send_modlogs(bot, message.guild, embed = em)
	con.commit()

@bot.event
async def on_command_error(ctx,error):
	if isinstance(error, commands.errors.MissingPermissions):
		await ctx.send(':x: You do not have permission to use this command!')
	elif isinstance(error, discord.Forbidden):
		await ctx.send(':x: Error 403: You are forbidden from using that command!')
	elif isinstance(error, commands.errors.MissingRequiredArgument):
		await ctx.send(str(error) + " Use >help <command> to see all required arguments.")
	else:
		await ctx.send(error)
	print(error)


@bot.command(name='load', hidden=True)
@commands.is_owner()
async def cog_load(ctx, *, cog: str):
	"""loads a module."""
	bot.load_extension(cog)

@bot.command(name='unload', hidden=True)
@commands.is_owner()
async def cog_unload(ctx, *, cog: str):
	"""unloads a module."""
	bot.unload_extension(cog)


@bot.command(name='reload', hidden=True)
@commands.is_owner()
async def cog_reload(ctx, *, cog: str):
	"""reloads a module."""
	bot.unload_extension(cog)
	bot.load_extension(cog)


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
