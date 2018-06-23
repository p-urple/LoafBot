import discord
from discord.ext import commands
class Utility:
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def server(self, ctx):
        """sends an invite to the support server"""
        await ctx.send('Join the support server at {}'.format('https://discord.gg/uJR4rcW'))

    @commands.command()
    async def invite(self, ctx):
        """sends the OAuth2 URL used for adding the bot to a server"""
        oauth2 = 'https://discordapp.com/api/oauth2/authorize?client_id=430438798141423617&permissions=334883910&scope=bot'
        await ctx.send('Add the bot to your server using {}'.format(oauth2))


    @commands.command()
    async def roles(self, ctx, user : discord.Member = None):
        """sends the list of roles for the server, or for the specified user, along with their IDs"""
        if user == None:
            user = ctx.author
        umention = user.mention

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

        em = discord.Embed(title = 'Roles for **' + user.display_name + '**:' , description = rolelist, colour = 0x4cff30)
        em.set_author(name=user.display_name, icon_url=user.avatar_url)	
        await ctx.send(embed=em)

def setup(bot):
    bot.add_cog(Utility(bot))
