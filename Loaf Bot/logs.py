import discord
import asyncio
from discord.ext import commands
from utils import *

class Logging:
	def __init__(self, bot):
		self.bot = bot

        
	async def on_bulk_message_delete(self, payload):
		self.bot.message_ids = payload.message_ids

        
	async def on_message_delete(self, message):
		if message.author.bot is True:
			return
		await asyncio.sleep(1)
		if self.bot.banned == message.author.id:
			return
		if self.bot.messages > 0:
			self.bot.messages -= 1
			return
			
		channel = message.channel.name

		mc = 'Deleted Message in #' + str(channel) + ':'

		em = discord.Embed(title=mc, description=message.content, colour=0xe74c3c)
		em.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
		set_embed_image_to_message_image(em,message)	


		await send_modlogs(self.bot, message.guild, embed = em)

		con.commit()

        
	async def on_message_edit(self, message, after):
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

		await send_modlogs(self.bot, message.guild, embed = em)
    
def setup(bot):
	bot.add_cog(Logging(bot))
