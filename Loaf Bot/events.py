import discord
from discord.ext import commands
from utils import *

con = sqlite3.connect('discord.db')
con.row_factory = sqlite3.Row

class Events:
	def __init__(self,bot):
		self.bot = bot
		
	async def on_guild_join(self, guild):
		sid = str(guild.id)
		c = con.cursor()
		try:
			c.execute('SELECT count(1) FROM guilds WHERE guildid=(?)', (sid,))
			exists = c.fetchone()[0]
			if not exists:
				c.execute('INSERT INTO guilds VALUES (?, ?, ?, ?, ?)', (sid, None, None, None, None))
		except:
			c.execute('''CREATE TABLE guilds
				     (guildid integer, publiclogs integer, modlogs integer, starboard integer, muterole integer)''')
			c.execute('INSERT INTO guilds VALUES (?, ?, ?, ?, ?)', (sid, None, None, None, None))
		con.commit()

		guild.system_channel.send('Hi! The bot is designed for maximum customizability and therefore has a small (optional) setup in order to use all features.	 Use `>help` to get started.')

	async def on_member_join(self, member):
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
					await member.add_roles(role)
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

	async def on_member_remove(self, member):
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

	async def on_raw_reaction_add(self,reaction, messageid, channelid, member):
		c = con.cursor()
		reactchannel = self.bot.get_channel(channelid)
		message = await reactchannel.get_message(messageid)
		truereaction = discord.utils.get(message.reactions, emoji = '⭐')
		if member == self.bot.user.id or message.author.bot == True:
			return
		if truereaction.count == 5 and reaction.name == '⭐' and str(messageid) not in open('bestof.txt').readlines():
			print('bestof')
			em = discord.Embed(title=':ok_hand: Nice :ok_hand:', description=message.content, colour=0xbc52ec)
			em.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
			set_embed_image_to_message_image(em,message)	
			await send_starboard(self.bot, message.guild, embed = em)
			cache = open("bestof.txt", "a+",encoding="utf8") 
			cache.write(str(messageid) + '\n')
			cache.close()
			con.commit()

def setup(bot):
	bot.add_cog(Events(bot))