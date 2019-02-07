import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
import discord
from discord.ext import commands
from classes import JsonFileObject
import message_strings as mstr

class Reverb:
    def __init__(self, bot):
        self.bot = bot
        self.links = JsonFileObject('links.json')
    async def on_message(self, ctx):
        try:
            if ctx.author.id in self.links[ctx.server.id][ctx.channel.id]:
                for channel in self.links[ctx.server.id][ctx.channel.id][ctx.author.id]:
                    embedable = discord.Embed(description = ctx.content)#, timestamp = ctx.timestamp)
                    embedable.set_footer(text = 'from #' + ctx.channel.name)
                    embedable.set_author(name= ctx.author.name, icon_url= ctx.author.avatar_url if not ctx.author.avatar_url == '' else ctx.author.default_avatar_url)
                    await self.bot.send_message(self.bot.get_channel(channel), embed = embedable)
            elif 'all' in self.links[ctx.server.id][ctx.channel.id]:
                for channel in self.links[ctx.server.id][ctx.channel.id]['all']:
                    embedable = discord.Embed(description = ctx.content)#, timestamp = ctx.timestamp)
                    embedable.set_author(name= ctx.author.name, icon_url= ctx.author.avatar_url if ctx.author.avatar_url != '' else ctx.author.default_avatar_url)
                    await self.bot.send_message(self.bot.get_channel(channel), embed = embedable)
                    break
        except KeyError: #Raised when Server or Channel is not in self.links
            pass
    def add_link(self, server, channel_src, user, channel_dest):
        '''Adds a chat-mirror link to the links file.'''
        try:
            if server not in self.links: self.links.update({server : {}})
            if channel_src not in self.links[server]: self.links[server].update({channel_src : {}})
            if user not in self.links[server][channel_src]: self.links[server][channel_src].update({user : []})

            entry = self.links[server][channel_src][user]

            if channel_dest not in entry:
                entry.append(channel_dest)
                self.links.save()
                return mstr.UPDATE_SUCCESS
            else:
                return mstr.UPDATE_DUPLICATE
        except:
            return mstr.UPDATE_ERROR
    def remove_link(self, server,channel_src,user,channel_dest):
        '''Removes a chat-mirror link in the links file.'''
        try:
            if channel_dest in self.links[server][channel_src][user]:
                self.links[server][channel_src][user].remove(channel_dest)
                self.links.save()
                return mstr.UPDATE_SUCCESS
            else:
                return mstr.UPDATE_NOT_FOUND
        except:
            return mstr.UPDATE_ERROR
    @commands.command()
    @commands.has_permissions(admin = True)
    async def link(self, ctx, user, channel):
        '''Copy messages from @tag in this channel to #destination channel. \'all\' may be used to echo all messages'''
        if user.lower() == 'all':
            s = self.add_link(ctx.server.id, ctx.channel.id, 'all', channel)

            print(s)
            
            if s is mstr.UPDATE_SUCCESS:
                return '{0} Now forwarding all messages in {1} to {2}'.format(s, ctx.channel.name, user)
            else:
                return s
        else:
            s = self.add_link(ctx.server.id, ctx.channel.id, user.strip('<@>'), channel.strip('<#>'))
            if s is mstr.UPDATE_SUCCESS:
                return '{0} Forwarding all messages in {1} from {2} to {3}'.format(s, ctx.channel.name, user, channel)
            else:
                await ctx.send(s)
            return

def setup(bot):
    bot.add_cog(Reverb(bot))
    print('Reverb extension loaded!')