import discord
import random
import asyncio
import sqlite3
from discord.ext import commands

bot = commands.Bot(command_prefix= '>')

bot.remove_command('help')

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
	
	em = discord.Embed(title=':white_check_mark: **CONECTED**', description=lm, colour=0x9b59b6)
	em.set_author(name=bot.user.name, icon_url=bot.user.avatar_url)

	await modlogchannel.send(embed=em)

@bot.event
async def on_guild_join(guild):
	sid = str(guild.id)
	con = sqlite3.connect('discord.db')
	c = con.cursor()
	try:
		c.execute('SELECT * FROM guilds WHERE symbol=(?)', (sid,))
	except:
		id = None
		try:
			guildinfo = [(sid, 'public logs', id), (sid, 'mod logs', id), (sid, 'starboard', id), (sid, 'mutedrole', id)]
			c.executemany('INSERT INTO guilds VALUES (?, ?, ?)', guildinfo)
		except:
			c.execute('''CREATE TABLE guilds
						 (guildid, type, id)''')
			guildinfo = [(sid, 'public logs', id), (sid, 'mod logs', id), (sid, 'starboard', id), (sid, 'mutedrole', id)]
			c.executemany('INSERT INTO guilds VALUES (?, ?, ?)', guildinfo)
	con.commit()
	con.close()

	guild.send('Hi! The bot is designed for maximum customizability and therefore has a small (optional) setup in order to use all features.  Use `>help` to get started.)

@bot.event
async def on_member_join(member):
	con = sqlite3.connect('discord.db')
	c = con.cursor()
	uid = member.id
	gid = member.guild.id
	if member.bot == True:
		return
	try:
		for i in c.execute('SELECT * FROM users WHERE id=(?)', (uid,)):
			if i[1] == gid:
				addsuccess = []
				addfail = []
				for r in i[2]:
					role = discord.utils.get(ctx.guild.roles, id=r)
					try:
						member.add_roles(role)
						addsuccess += role.name
					except:
						addfail += role.name
				user = discord.utils.get(user, id=uid)
				await user.edit(nick(i[3]))
				message = '**Succsessfully Restored:** \n'
				for i in addsuccsess:
					message += i
					message += '\n'
				message += '\n'
				message += '**Unsuccsessfully Restored:** \n'
				for i in addfail:
					message += i
					message += '\n'
				em2 = discord.Embed(title=None, description=message, color=0x23272a)
				em2.set_author(name=member.display_name, icon_url=member.avatar_url)
				c.execute('DELETE FROM users WHERE symbol=? AND symbol=?', uid, gid)

	mc = 0
	for x in member.guild.members:
		if x.bot == False:
			mc += 1

	emt = 'Member Joined: \n \n'

	umention = member.mention
	des = '**Member:** '
	des += umention
	des += '\n'
	des += '**ID:** '
	des += str(member.id)
	des += '\n'
	des += '**Member Count:** '
	des += str(mc)
	des += '\n'

	em = discord.Embed(title=emt, description=des, colour=0x51cc72)
	em.set_author(name=member.display_name, icon_url=member.avatar_url)

	i = c.execute("SELECT * FROM guilds WHERE symbol=(?)", (ctx.guild.id,))
	modlog = i[1]

	modlogchannel = bot.get_channel(modlog)
	await modlogchannel.send(embed = em)
	await modlogchannel.send(embed = em2)
	
	con.commit()
	con.close()

@bot.event
async def on_member_remove(member):
	con = sqlite3.connect('discord.db')
	c = con.cursor()
	uid = member.id
	gid = member.guild.id
	roles = []
	for i in member.roles:
		roles += i.id
	nick = member.display_name
	try:
		c.execute("INSERT INTO users VALUES (uid, gid, roles, nick)")
	except:
		c.execute('''CREATE TABLE users
		(userid, guildid, roleids, nickname)''')
		c.execute("INSERT INTO users VALUES (uid, gid, roles, nick)")

	if member.bot == True:
		return

	mc = 0
	for x in member.guild.members:
		if x.bot == False:
			mc += 1

	emt = 'Member Left: \n \n'

	umention = member.mention
	des = '**Member:** '
	des += umention
	des += '\n'
	des += '**ID:** '
	des += str(member.id)
	des += '\n'
	des += '**Member Count:** '
	des += str(mc)
	des += '\n' 
	
	em = discord.Embed(title=emt, description=des, colour=0xe74c3c)
	em.set_author(name=member.display_name, icon_url=member.avatar_url)

	for i in c.execute("SELECT * FROM guilds WHERE id=(?)", (ctx.guild.id,)):
		if i[1] == 'mod logs':
			modlog = i[2]

	modlogchannel = bot.get_channel(modlog)
	await modlogchannel.send(embed = em)
	con.commit()
	con.close()

@bot.event
async def on_raw_reaction_add(reaction, messageid, channelid, member):
	reactchannel = bot.get_channel(channelid)
	message = await reactchannel.get_message(messageid)
	if member == bot.user.id:
		return
	if message.author.bot == True:
		return
	bestofc = bot.get_channel(bestof)
	worstofc = bot.get_channel(worstof)
	if reaction.count is 7:
		if reaction.name == '⭐':
			if str(messageid) in open('bestof.txt').read():
				pass
			else:
				con = sqlite3.connect('discord.db')
				c = con.cursor()
				print('bestof')
				mc = ':ok_hand: Nice :ok_hand:'

				em = discord.Embed(title=mc, description=message.content, colour=0xbc52ec)
				em.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
				em.set_footer(text='This meme recieved enough stars to make it into #bestof')
				try:
					if message.content.startswith('https://'):
						em.set_image(url=message.content)
				except:
					pass
				try:
					attach = message.attachments
					em.set_image(url = attach[0].url)
				except:
					pass

				for i in c.execute("SELECT * FROM guilds WHERE id=(?)", (ctx.guild.id,)):
					if i[1] == 'starboard':
						bestofc = i[2]

				await bestofc.send(embed = em)
				cache = open("bestof.txt", "a+",encoding="utf8")
				cache.write(str(messageid) + " ")
				cache.close()
				con.commit()
				con.close()

@bot.event
async def on_message_delete(message):
	if message.author.bot is True:
		return
	con = sqlite3.connect('discord.db')
	c = con.cursor()
	modlogchannel = bot.get_channel(modlog)
	channel = message.channel.name

	mc = 'Deleted Message in #'
	mc += channel
	mc += ':'

	em = discord.Embed(title=mc, description=message.content, colour=0xe74c3c)
	em.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
	try:
		if message.content.startswith('https://'):
			em.set_image(url=message.content)
	except:
		pass
	try:
		attach = message.attachments
		em.set_image(url = attach[0].url)
	except:
		pass
	for i in c.execute("SELECT * FROM guilds WHERE symbol=?", (ctx.guild.id,)):
		if i[1] == 'mod logs':
			modlog = i[2]

	modlogchannel = bot.get_channel(modlog)
	await modlogchannel.send(embed = em)
	con.commit()
	con.close()


@bot.event
async def on_message_edit(message, after):
	if message.author.bot is True:
		return
	elif message == after:
		return
	else:
		con = sqlite3.connect('discord.db')
		c = con.cursor()
		channel = message.channel.name

		mc = 'Edited Message in #'
		mc += channel
		mc += ':'

		me = '**Old Message:** \n'
		me += message.content
		me += '\n \n'
		me += '**New Message:** \n'
		me += after.content

		em = discord.Embed(title=mc, description=me, colour=0xFFD700)
		em.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
		try:
			if message.content.startswith('https://'):
				em.set_image(url=message.content)
		except:
			pass
		try:
			attach = message.attachments
			em.set_image(url = attach[0].url)
		except:
			pass

		for i in c.execute("SELECT * FROM guilds WHERE symbol=?", (ctx.guild.id,)):
			if i[1] == 'mod logs':
				modlog = i[2]

		modlogchannel = bot.get_channel(modlog)
		await modlogchannel.send(embed = em)
		con.commit()
		con.close()


@bot.command(pass_context=True)
async def help(ctx):
	b = bot.user.display_name
	helpt = "Commands for "
	helpt += b
	helpt += ": \n \n"

	helpm = """**FUN COMMANDS:**
	`>clap <message>`: sends a fun message with clap emojis
	`>mock <message>`: sends a fun message with letters randomly turned uppercase and lowercase
	
	**UTILITY COMMANDS:**
	`>setup`: the command used to configure the bot. Use the command for more information.
	`>roles [user]`: sends the list of roles for the server, or for the specified user, along with their IDs \n
	`>support`: sends an invite to the support server
	`>invite`: sends the OAuth2 URL used for adding the bot to a server
	
	**MODERATION ONLY:**
	`>mute <user> <s/m/h/d> [reason]`: mutes the user for the specified amount of time
	`>unmute <user>`: unmutes the specified muted user
	
	**CONFIGURATION COMMANDS:**
	`>muterole <role name>`: used to assign the role given to muted members -- *remember to us the exact role name in quotes. ("Role Name")*
	`>modlog <channel>`: used to assign the mod log to a channel
	`>publiclog <channel>`: used to assign an optional second log that shows only mutes for regular users to view
	`>starboard <channel>`: used to assign the starboard to a channel
	
	*<> = necessary          [] = optional*"""

	em = discord.Embed(title=helpt, description=helpm, colour=0x9b59b6)
	em.set_author(name=bot.user.name, icon_url=bot.user.avatar_url)

	await ctx.send(embed=em)

@bot.event()
async def on_mention(ctx):
	b = bot.user.display_name
	helpt = "Commands for {}:\n\n".format(b)

	helpm = """**FUN COMMANDS:**
	`>clap <message>`: sends a fun message with clap emojis
	`>mock <message>`: sends a fun message with letters randomly turned uppercase and lowercase
	
	**UTILITY COMMANDS:**
	`>setup`: the command used to configure the bot. Use the command for more information.
	`>roles [user]`: sends the list of roles for the server, or for the specified user, along with their IDs \n
	`>support`: sends an invite to the support server
	`>invite`: sends the OAuth2 URL used for adding the bot to a server
	
	**MODERATION ONLY:**
	`>mute <user> <s/m/h/d> [reason]`: mutes the user for the specified amount of time
	`>unmute <user>`: unmutes the specified muted user
	
	**CONFIGURATION COMMANDS:**
	`>muterole <role name>`: used to assign the role given to muted members -- *remember to us the exact role name in quotes. ("Role Name")*
	`>modlog <channel>`: used to assign the mod log to a channel
	`>publiclog <channel>`: used to assign an optional second log that shows only mutes for regular users to view
	`>starboard <channel>`: used to assign the starboard to a channel
	
	*<> = necessary          [] = optional*"""

	em = discord.Embed(title=helpt, description=helpm, colour=0x9b59b6)
	em.set_author(name=bot.user.name, icon_url=bot.user.avatar_url)

	await ctx.send(embed=em)

@bot.command()
async def muterole(ctx, rolename : discord.Role):
	if rolename == None:
		await ctx.send('Please provide a role. Remember to put the role in quotes and make sure it is the exact name. ("Role name")')
	else:
		try:
			role = discord.utils.get(ctx.guild.roles, name=rolename)
			con = sqlite3.connect('discord.db')
			c = con.cursor()
			c.execute("UPDATE guilds SET id=(?) WHERE guildid=(?) AND type='mutedrole'", (role.id, ctx.guild.id))
		except:
			await ctx.send('The provided role could not be found. Please put the role name in quotes, and make sure the name is *exact*. Remember that the bot is case sensitive. ("Role name")')

@bot.command()
async def modlog(ctx, channel : discord.TextChannel):
	if channel == None:
		await ctx.send('Please provide a channel')
	else:
		try:
			con = sqlite3.connect('discord.db')
			c = con.cursor()
			c.execute("UPDATE guilds SET id=(?) WHERE guildid=(?) AND type='mod logs'", (channel.id, ctx.guild.id))
		except:
			await ctx.send('The provided channel could not be found.')

@bot.command()
async def publiclog(ctx, channel : discord.TextChannel):
	if channel == None:
		await ctx.send('Please provide a channel')
	else:
		try:
			con = sqlite3.connect('discord.db')
			c = con.cursor()
			c.execute("UPDATE guilds SET id=(?) WHERE guildid=(?) AND type='public logs'", (channel.id, ctx.guild.id))
		except:
			await ctx.send('The provided channel could not be found.')

@bot.command()
async def starboard(ctx, channel : discord.TextChannel):
	if channel == None:
		await ctx.send('Please provide a channel')
	else:
		try:
			con = sqlite3.connect('discord.db')
			c = con.cursor()
			c.execute("UPDATE guilds SET id=(?) WHERE guildid=(?) AND type='starboard'", (channel.id, ctx.guild.id))
		except:
			await ctx.send('The provided channel could not be found.')

@bot.command()
async def support(ctx):
	await ctx.send('Join the support sever using {}'.format('https://discord.gg/uJR4rcW'))

@bot.command()
async def invite(ctx):
	oauth2 = 'https://discordapp.com/api/oauth2/authorize?client_id=430438798141423617&permissions=469093376&scope=bot'
	await ctx.send('Add the bot to your server using {}'.format(oauth2))

@bot.command()
async def clap(ctx, *, sentence : str = None):
	if sentence is None:
		await ctx.send('You have to say something before this command works')
	else:
		sentencetemp = sentence.replace(' ', ':clap:')
		sentence = ':clap:'
		sentence += sentencetemp
		sentence += ':clap:'
		await ctx.send(sentence)

@bot.command()
async def smh(ctx, *, headshake : str = None):
	if headshake is None:
		await ctx.send('You have to say something before this command works')
	else:
		headshake = headshake.replace('smh', 'smh my head')
		headshake += ' smh'
		await ctx.send(headshake)

@bot.command()
async def mock(ctx, *, mocktxt : str = None):
	if mocktxt == None:
		await ctx.send('You have to say something before this command works')
	else:
		list = []
		for i in mocktxt:
			list += i
			for i in range(len(list)):
				p = random.randint(1, 100)
				if p < 51:
					list[i] = list[i].lower()
				else:
					list[i] = list[i].upper()
		mocktxtnew = ''
		for i in list:
			mocktxtnew += i
		await ctx.send(mocktxtnew)

@bot.command()
async def roles(ctx, user : discord.Member = None):
	if user == None:
		rolelist = ''
		counter = 0
		for role in ctx.guild.roles:
			rolelist += str(role.id)
			rolelist += '   ---   '
			rolelist += role.name
			rolelist += '\n'
			counter += 1
	
		title = 'Roles in **'
		title += ctx.guild.name
		title += '**:'

		rolelist += '\n **'
		rolelist += str(counter)
		rolelist += ' roles**'

		em = discord.Embed(title=title, description=rolelist, colour=0x4cff30)
		await ctx.send(embed=em)

	else:
		umention = user.mention
		
		title = 'Roles for **'
		title += user.display_name
		title += '**:'
		
		rolelist = ''
		counter = 0
		for role in user.roles:
			rolelist += str(role.id)
			rolelist += '   ---   '
			rolelist += role.name
			rolelist += '\n'
			counter += 1
			
		rolelist += '\n **'
		rolelist += str(counter)
		rolelist += ' roles**'
		
		em = discord.Embed(title=title, description=rolelist, colour=0x4cff30)
		em.set_author(name=user.display_name, icon_url=user.avatar_url)	
		await ctx.send(embed=em)


@bot.command(pass_context=True)
@commands.has_permissions(manage_messages=True)
async def mute(ctx, user : discord.Member, tint :int = None, tdenom :str = None, *, reason : str = None):
	con = sqlite3.connect('discord.db')
	c = con.cursor()
	if tdenom in ['s', 'm', 'h', 'd']:
		if user is ' ':
			await ctx.send('Correct usage is: >mute <@person> <time integer> <s/m/h/d> <reason(optional)>')
		elif tint is ' ':
			await ctx.send('Correct usage is: >mute <@person> <time integer> <s/m/h/d> <reason(optional)>')
		elif tdenom is ' ':
			await ctx.send('Correct usage is: >mute <@person> <time integer> <s/m/h/d> <reason(optional)>')
		else:
			for i in c.execute("SELECT * FROM guilds WHERE name=(?)", ('mutedrole',)):
				if i[0] == ctx.guild.id:
					mutedid = i[2]
			role = discord.utils.get(ctx.guild.roles, id=muteid)
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
					muted += str(tint)
					muted += tdenom
				else:
					muted = umention
					muted += ' was muted for '
					muted += str(tint)
					muted += tdenom
					muted += ' (`'
					muted += reason
					muted += '`)'

				for i in c.execute("SELECT * FROM guilds WHERE symbol=(?)", (ctx.guild.id,)):
					if i[1] == 'mod logs':
						modlog = i[2]
					if i[1] == 'public logs':
						report = i[2]

				modlogchannel = bot.get_channel(modlog)
				mchannel = bot.get_channel(report)
				await modlogchannel.send(muted)
				await ctx.send(muted)
				await mchannel.send(muted)
				if tdenom is 's':
					time = 1
				elif tdenom is 'm':
					time = 60
				elif tdenom is 'h':
					time = 3600
				elif tdenom is 'd':
					time = 86400
				t = tint * time
				await asyncio.sleep(t)
				if role in user.roles:
					await user.remove_roles(role)

	else:
		await ctx.send('Correct usage is: >mute <@person> <time integer> <s/m/h/d> <reason(optional)>')
	
@mute.error
async def mute_error(ctx, error):
	if isinstance(error, commands.errors.MissingPermissions):
		await ctx.send(':x: You do not have permission to use this command')
	elif isinstance(error, discord.Forbidden):
		await ctx.send(':x: Error 403: You are forbidden from using that command. Please visit the support server for more information.')
	else:
		await ctx.send(error)
		print(error)
		
@bot.command()
@commands.has_permissions(manage_messages=True)
async def unmute(ctx, user: discord.Member):
	for i in c.execute("SELECT * FROM guilds WHERE name=(?)", ('mutedrole',)):
		if i[0] == ctx.guild.id:
			mutedid = i[2]
	role = discord.utils.get(ctx.guild.roles, id=muteid)
	umention = user.mention
	if role in user.roles:
		await user.remove_roles(role)
		m = umention
		m += ' is no longer muted'
		await ctx.send(m)
	else:
		m = umention
		m += ' is not muted'
		await ctx.send(m)

@unmute.error
async def unmute_error(ctx, error):
	if isinstance(error, commands.errors.MissingPermissions):
		await ctx.send(':x: You do not have permission to use this command!')
	elif isinstance(error, discord.Forbidden):
		await ctx.send(':x: Error 403: You are forbidden from using that command!')
	else:
		await ctx.send(error)
		print(error)


bot.run("<bot token>")