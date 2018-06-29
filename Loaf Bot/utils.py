import discord
import asyncio
import sqlite3
from discord.ext import commands

con = sqlite3.connect('discord.db')
con.row_factory = sqlite3.Row

def __init__(self, bot):
	self.bot = bot

async def send_modlogs(bot, guild, *args, **kwargs):
	c = con.cursor()
	c.execute("SELECT * FROM guilds WHERE guildid=?", (guild.id,))
	row = c.fetchone()
	if row['modlogs'] is not None:
		await bot.get_channel(row['modlogs']).send(*args, **kwargs)

async def send_publiclogs(bot, guild, *args, **kwargs):
	c = con.cursor()
	c.execute("SELECT * FROM guilds WHERE guildid=?", (guild.id,))
	row = c.fetchone()
	if row['modlogs'] is not None:
		await bot.get_channel(row['modlogs']).send(*args, **kwargs)
	if row['publiclogs'] is not None:
		await bot.get_channel(row['publiclogs']).send(*args, **kwargs)

async def send_starboard(bot, guild, *args, **kwargs):
	c = con.cursor()
	c.execute("SELECT * FROM guilds WHERE guildid=?", (guild.id,))
	row = c.fetchone()
	if row['starboard'] is not None:
		await bot.get_channel(row['starboard']).send(*args, **kwargs)

def load_prefixes(bot):
	c = con.cursor()
	for row in c.execute("SELECT * FROM prefixes WHERE guildid"):
		bot.prefixes[row['guildid']] = row['prefix']

def get_pre(bot, message):
	if message.content.startswith('>'):
		return '>'
	if message.content.startswith(f'{bot.user.mention} '):
		return f'{bot.user.mention} '
	else:
		try:
			return bot.prefixes[message.guild.id]
		except:
			return '>'
		
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

def set_embed_image_to_message_image(em, message):
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
