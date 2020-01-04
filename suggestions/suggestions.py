import discord
from redbot.core import commands
from redbot.core import Config
from copy import deepcopy
from redbot.core import checks
import asyncio
import json
import os

client = discord.Client()
notified = False

class Suggestions(commands.Cog):
    """The suggestions cog that controls user suggestions."""
    
    def __init__(self):
        self.config = Config.get_conf(self, identifier=3302120966)
        default_guild = { "channels": [] }
        self.config.register_guild(**default_guild)
        
    async def getAvailableChannelIDs(self, _guild):
        return await self.config.guild(_guild).channels()
    
    @commands.command(pass_context=True, aliases=['s'])
    async def suggest(self, ctx):
        """Suggest an idea for the server."""

        msg = ctx.message
        
        if "!s " in msg.content:
            embedDescription = msg.content[3:]
        else:
            embedDescription = msg.content[9:]
        channel = ctx.channel
        user = msg.author
        guild = ctx.guild
        hasPerms = True

        try:
            await msg.delete()
        except discord.errors.Forbidden:
            global notified
            notified = notified
            if not notified:
                await ctx.send("I require permissions to delete messages. This doesn't allow me to delete users suggesting in a non-suggestion channel.")
                notified = True
                hasPerms = False
        
        # get list of channels in this guild in self.config
        channelIDs = await self.getAvailableChannelIDs(guild)
        
        if not channel.id in channelIDs:
            if len(channelIDs) < 1:
                await self.concludeFunction(ctx, "No channel has been set to receive suggestions. Have a moderator+ run `!suggestChannel`" \
                                   " in a channel that should accept suggestions.")
                return
            firstAvailableChannel = guild.get_channel(channelIDs[0])
            print(firstAvailableChannel)
            await self.concludeFunction(ctx, "Wrong channel; use {}.".format(firstAvailableChannel.mention))
            return
        else:
            channelToPostTo = channel.id

        embedTitle = "**Suggestion by {}**".format(user.name)
        embedColor = 0x0C60E4
        embed = discord.Embed(title=embedTitle, description=embedDescription, color=embedColor)

        postedMsg = await ctx.send(embed=embed)
        await postedMsg.add_reaction("👍")
        await postedMsg.add_reaction("😑")
        await postedMsg.add_reaction("👎")
        return

    @commands.command(pass_context=True, aliases=['sugc'])
    @checks.admin_or_permissions(manage_guild=True)
    async def suggestChannel(self, ctx):
        """Toggles what channels accept and post suggestions."""

        user = ctx.author
        channel = ctx.channel
        guild = channel.guild
        msg = ctx.message
 
        try:
            await msg.delete()
        except discord.errors.Forbidden:
            global notified
            notified = notified
            if not notified:
                await ctx.send("I require permissions to delete messages. This won't stop the function, but allows me to automatically delete messages.")
                notified = True

        channelIDs = await self.getAvailableChannelIDs(guild)
        if not channel.id in channelIDs:
            channel_values = self.config.guild(guild)
            async with channel_values.channels() as channels:
                channels.append(channel.id)
            await self.concludeFunction(ctx, "This channel now accepts `!suggest`ions.")
        else:
            channel_values = self.config.guild(guild)
            async with channel_values.channels() as channels:
                channels.remove(channel.id)
            await self.concludeFunction(ctx, "This channel no longer accepts `!suggest`ions.")
        return
    
    async def concludeFunction(self, ctx, msgString, delay:int=10):
        msg = await ctx.send(msgString)
        await self.killMsg(msg, delay)
        return
    
    async def killMsg(self, msg, delay:int=10):
        await asyncio.sleep(delay)
        await msg.delete()
        return