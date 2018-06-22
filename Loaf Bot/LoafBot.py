import discord
import asyncio
import sqlite3
from discord.ext import commands
from utils import *

bot = commands.Bot(command_prefix= '>')
con = sqlite3.connect('discord.db')
con.row_factory = sqlite3.Row


###########################################################################################################################################################
# helpm = """**FUN COMMANDS:**                                                                                                                            #
# `>clap <message>`: sends a fun message with clap emojis                                                                                                 #
# 	`>mock <message>`: sends a fun message with letters randomly turned uppercase and lowercase                                                       #
# 	                                                                                                                                                  #
# 	**UTILITY COMMANDS:**                                                                                                                             #
# 	`>roles [user]`: sends the list of roles for the server, or for the specified user, along with their IDs                                          #
# 	`>support`: sends an invite to the support server                                                                                                 #
# 	`>invite`: sends the OAuth2 URL used for adding the bot to a server                                                                               #
# 	                                                                                                                                                  #
# 	**MODERATION ONLY:**                                                                                                                              #
# 	`>mute <user> <s/m/h/d> [reason]`: mutes the user for the specified amount of time                                                                #
# 	`>unmute <user>`: unmutes the specified muted user                                                                                                #
# 	                                                                                                                                                  #
# 	**CONFIGURATION COMMANDS:**                                                                                                                       #
# 	`>muterole <role name>`: used to assign the role given to muted members -- *remember to us the exact role name in quotes. ("Role Name")*          #
# 	`>modlog <channel>`: used to assign the mod log to a channel                                                                                      #
# 	`>publiclog <channel>`: used to assign an optional second log that shows only mutes for regular users to view                                     #
# 	`>starboard <channel>`: used to assign the starboard to a channel                                                                                 #
# 	                                                                                                                                                  #
# 	*<> = necessary		 [] = optional*"""                                                                                                        #
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
				if role.id == 430437006787608577:
					pass
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


######################################################################################
# @bot.command(pass_context=True)                                                    #
# async def help(ctx):                                                               #
# 	helpt = "Commands for {}:\n\n".format(bot.user.display_name)                 #
# 	#edit the help message at top of file                                        #
# 	                                                                             #
# 	em = discord.Embed(title=helpt, description=helpm, colour=0x9b59b6)          #
# 	em.set_author(name=bot.user.name, icon_url=bot.user.avatar_url)              #
#                                                                                    #
# 	await ctx.send(embed=em)                                                     #
######################################################################################


@bot.event
async def on_command_error(ctx,error):
	if isinstance(error, commands.errors.MissingPermissions):
		await ctx.send(':x: You do not have permission to use this command!')
	elif isinstance(error, discord.Forbidden):
		await ctx.send(':x: Error 403: You are forbidden from using that command!')
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

bot.run(open('token.txt','r').read())
