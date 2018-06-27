import discord
from discord.ext import commands
import sqlite3
con = sqlite3.connect('discord.db')
con.row_factory = sqlite3.Row

class Config:
	"""Configuration"""
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	@commands.has_permissions(manage_channels=True)
	async def muterole(self, ctx, *, rolename : discord.Role):
		"""used to assign the role given to muted members -- *remember to use the exact role name*"""
		c = con.cursor()
		c.execute("UPDATE guilds SET muterole=(?) WHERE guildid=(?)", (rolename.id, ctx.guild.id))
		await ctx.send('Mute role set.')
		con.commit()

	@commands.command()
	@commands.has_permissions(manage_channels=True)
	async def modlog(self, ctx, channel : discord.TextChannel):
		"""used to assign the mod log to a channel"""
		c = con.cursor()
		c.execute("UPDATE guilds SET modlogs=(?) WHERE guildid=(?)", (channel.id, ctx.guild.id))
		await ctx.send("Mod log channel set.")
		con.commit()

	@commands.command()
	@commands.has_permissions(manage_channels=True)
	async def publiclog(self, ctx, channel : discord.TextChannel):
		"""used to assign an optional second log that shows only mutes for regular users to view"""
		c = con.cursor()
		c.execute("UPDATE guilds SET publiclogs=(?) WHERE guildid=(?)", (channel.id, ctx.guild.id))
		await ctx.send("Public log channel set.")
		con.commit()

	@commands.command()
	@commands.has_permissions(manage_channels=True)
	async def starboard(self, ctx, channel : discord.TextChannel):
		"""used to assign the starboard to a channel"""
		c = con.cursor()
		c.execute("UPDATE guilds SET starboard=(?) WHERE guildid=(?)", (channel.id, ctx.guild.id))
		await ctx.send("Starboard channel set.")
		con.commit()

	@commands.command()
	@commands.has_permissions(administrator=True)
	async def setprefix(self, ctx, *, prefix = None):
		"""sets the custom prefix for this server"""
		c = con.cursor()
		if prefix is not None:
			c.execute('SELECT count(1) FROM prefixes WHERE guildid=(?)', (ctx.message.guild.id,))
			exists = c.fetchone()[0]
			if not exists:
				c.execute('INSERT INTO prefixes VALUES (?, ?)', (ctx.message.guild.id, prefix))
			else:
				c.execute('UPDATE prefixes SET prefix=(?) WHERE guildid=(?)', (prefix, ctx.message.guild.id))
			self.bot.prefixes[ctx.message.guild.id] = prefix
			await ctx.send(f'The custom prefix for this server is now `{prefix}`')
			con.commit()
		else:
			await ctx.send('Please provide a prefix')


def setup(bot):
	bot.add_cog(Config(bot))
