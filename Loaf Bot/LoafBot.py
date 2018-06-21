import discord
import random
import asyncio
import sqlite3
from discord.ext import commands

bot = commands.Bot(command_prefix= '>')
con = sqlite3.connect('discord.db')
con.row_factory = sqlite3.Row

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

async def send_modlogs(guild, *args, **kwargs):
	c = con.cursor()
	c.execute("SELECT * FROM guilds WHERE guildid=?", (guild.id,))
	row = c.fetchone()
	if row['modlogs'] is not None:
		await bot.get_channel(row['modlogs']).send(*args, **kwargs)

async def send_publiclogs(guild, *args, **kwargs):
	c = con.cursor()
	c.execute("SELECT * FROM guilds WHERE guildid=?", (guild.id,))
	row = c.fetchone()
	if row['modlogs'] is not None:
		await bot.get_channel(row['modlogs']).send(*args, **kwargs)
	if row['publiclogs'] is not None:
		await bot.get_channel(row['publiclogs']).send(*args, **kwargs)

async def send_starboard(guild, *args, **kwargs):
	c = con.cursor()
	c.execute("SELECT * FROM guilds WHERE guildid=?", (guild.id,))
	row = c.fetchone()
	if row['starboard'] is not None:
		await bot.get_channel(row['starboard']).send(*args, **kwargs)

def get_muterole(guild):
	c = con.cursor()
	c.execute("SELECT * FROM guilds WHERE guildid=?", (guild.id,))
	row = c.fetchone()
	return discord.utils.get(guild.roles, id=row['muterole'])

def get_field(guild, field):
	c = con.cursor()
	c.execute("SELECT * FROM guilds WHERE guildid=?", (guild.id,))
	row = c.fetchone()
	return row[field]

		
	
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
			
			role = discord.utils.get(ctx.guild.roles, id=i[2])			 
			try:								      
				if role.id == 430437006787608577:
					pass
				member.add_roles(role)
				addsuccess.append(role.name)
			except:
				addfail.append(role.name)				      
			user = discord.utils.get(user, id=uid)					      
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

	await send_modlogs(member.guild, embed = em)
	if returning:
		await send_modlogs(member.guild, embed = em2)
	
	con.commit()

@bot.event
async def on_member_remove(member):
	c = con.cursor()
	uid = member.id
	gid = member.guild.id
	roles = [role for role in member.roles] #needed?
	many = [(uid, gid, role) for role in roles]
	try:
		c.executemany("INSERT INTO users VALUES (uid, gid, roles)", many)
	except:
		c.execute('''CREATE TABLE users
		(uid, gid, role)''')
		c.executemany("INSERT INTO users VALUES (uid, gid, roles)", many)

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
	await send_modlogs(member.guild, embed = em)
	con.commit()

@bot.event
async def on_raw_reaction_add(reaction, messageid, channelid, member):
	c = con.cursor()
	reactchannel = bot.get_channel(channelid)
	message = await reactchannel.get_message(messageid)
	if member == bot.user.id or message.author.bot == True:
		return
	if reaction.count is 7 and reaction.name == '⭐':
		if str(messageid) in open('bestof.txt').readlines():
			pass
		else:
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

			await send_starboard(message.guild, embed = em)
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

	mc = 'Deleted Message in #'
	mc += str(channel) 
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

	await send_modlogs(message.guild, embed = em)

	con.commit()



@bot.event
async def on_message_edit(message, after):
	c = con.cursor()
	if message.author.bot is True or message.content == after.content:
		return
	else:
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

		await send_modlogs(message.guild, embed = em)
		con.commit()


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
	
	*<> = necessary		 [] = optional*""" #refactor out into *actual framework-provided help function*

	em = discord.Embed(title=helpt, description=helpm, colour=0x9b59b6)
	em.set_author(name=bot.user.name, icon_url=bot.user.avatar_url)

	await ctx.send(embed=em)

@bot.event
async def on_mention(ctx):
	b = bot.user.display_name
	helpt = "Commands for {}:\n\n".format(b)

	helpm = """**FUN COMMANDS:**
	`>clap <message>`: sends a fun message with clap emojis
	`>mock <message>`: sends a fun message with letters randomly turned uppercase and lowercase
	
	**UTILITY COMMANDS:**
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
	
	*<> = necessary		 [] = optional*"""

	em = discord.Embed(title=helpt, description=helpm, colour=0x9b59b6)
	em.set_author(name=bot.user.name, icon_url=bot.user.avatar_url)

	await ctx.send(embed=em)

@bot.command()
@commands.has_permissions(manage_server=True)
async def muterole(ctx, rolename : discord.Role):
	c = con.cursor()
	if rolename == None:
		await ctx.send('Please provide a role. Remember to put the role in quotes and make sure it is the exact name. ("Role name")')
	else:
		try:
			c.execute("UPDATE guilds SET muterole=(?) WHERE guildid=(?)", (rolename.id, ctx.guild.id))
			await ctx.send('Mute role set.')
		except Exception as e:
			print(e)
			await ctx.send('The provided role could not be found. Please put the role name in quotes, and make sure the name is *exact*. Remember that the bot is case sensitive. ("Role name")')
	con.commit()

@bot.command()
@commands.has_permissions(manage_server=True)
async def modlog(ctx, channel : discord.TextChannel):
	c = con.cursor()

	if channel == None:
		await ctx.send('Please provide a channel')
	else:
		try:
			c.execute("UPDATE guilds SET modlogs=(?) WHERE guildid=(?)", (channel.id, ctx.guild.id))
			await ctx.send("Mod log channel set.")
		except Exception as e:
			await ctx.send('The provided channel could not be found.') #unneeded? caught by converter
	con.commit()

@bot.command()
@commands.has_permissions(manage_server=True)
async def publiclog(ctx, channel : discord.TextChannel):
	c = con.cursor()

	if channel == None:
		await ctx.send('Please provide a channel')
	else:
		try:
			c.execute("UPDATE guilds SET publiclogs=(?) WHERE guildid=(?)", (channel.id, ctx.guild.id))
			await ctx.send("Public log channel set.")
		except:
			await ctx.send('The provided channel could not be found.')
	con.commit()

@bot.command()
@commands.has_permissions(manage_server=True)
async def starboard(ctx, channel : discord.TextChannel):
	c = con.cursor()
	if channel == None:
		await ctx.send('Please provide a channel')
	else:
		try:
			c.execute("UPDATE guilds SET starboard=(?) WHERE guildid=(?)", (channel.id, ctx.guild.id))
			await ctx.send("Starboard channel set.")
		except:
			await ctx.send('The provided channel could not be found.')
	con.commit()

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
		sentencetemp = ':clap:' + sentence.replace(' ', ':clap:') + ':clap:'
		await ctx.send(sentencetemp)

@bot.command()
async def smh(ctx, *, headshake : str = None):
	if headshake is None:
		await ctx.send('You have to say something before this command works')
	else:
		headshake = headshake.replace('smh', 'smh my head') + ' smh'
		await ctx.send(headshake)

@bot.command()
async def mock(ctx, *, mocktxt : str = None):
	if mocktxt == None:
		await ctx.send('You have to say something before this command works')
	else:
		mockedtxt = ''
		for i in mocktxt:
			mockedtxt += i.lower() if random.randint(1, 100) < 51 else i.upper()
		await ctx.send(mockedtxt)

@bot.command()
async def roles(ctx, user : discord.Member = None):
	if user == None:
		rolelist = ''
		counter = 0
		for role in ctx.guild.roles:
			rolelist += str(role.id)
			rolelist += '	---   '
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
			rolelist += '	---   '
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
	c = con.cursor()
	if tdenom in ['s', 'm', 'h', 'd']:
		if user is ' ':
			await ctx.send('Correct usage is: >mute <@person> <time integer> <s/m/h/d> <reason (optional)>')
		elif tint is ' ':
			await ctx.send('Correct usage is: >mute <@person> <time integer> <s/m/h/d> <reason (optional)>')
		elif tdenom is ' ':
			await ctx.send('Correct usage is: >mute <@person> <time integer> <s/m/h/d> <reason (optional)>')
		else:
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


				await ctx.send(muted)
				await send_publiclogs(ctx.guild, muted)
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
					await send_publiclogs(ctx.guild, user.mention + ' is no longer muted.')


	else:
		await ctx.send('Correct usage is: >mute <@person> <time integer> <s/m/h/d> <reason(optional)>')
	
@mute.error
async def mute_error(ctx, error):
	if isinstance(error, commands.errors.MissingPermissions):
		await ctx.send(':x: You do not have permission to use this command')
	elif isinstance(error, discord.Forbidden):
		await ctx.send(':x: Error 403: You are forbidden from using that command. Please visit the support server for more information.')
	else:
		await ctx.send(str(error))
		print(error)
		
@bot.command()
@commands.has_permissions(manage_messages=True)
async def unmute(ctx, user: discord.Member):
	role = get_muterole(ctx.guild)
	umention = user.mention
	if role in user.roles:
		await user.remove_roles(role)
		await ctx.send(umention + ' is no longer muted.')
		await send_publiclogs(ctx.guild, user.mention + ' is no longer muted.')
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


bot.run(open('.token','r').read())
