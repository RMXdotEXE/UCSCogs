import discord
from discord.ext import commands
from cogs.utils.dataIO import dataIO
from copy import deepcopy
from .utils import checks
import asyncio
import json
import os

class Suggestions:
    """The suggestions cog that controls user suggestions."""

    def __init__(self, bot):
        self.bot = bot
        self.filePath = "data/suggestions/channelData.json"
        self.suggestData = dataIO.load_json(self.filePath)
        
    def getEligibleSuggestionChannels(self, server):
        return self.suggestData[server.id]

    @commands.command(pass_context=True)
    async def suggest(self, ctx):
        """Suggest an idea for the server."""

        msg = ctx.message
        channel = ctx.message.channel
        user = msg.author
        hasPerms = True

        try:
            await self.bot.delete_message(ctx.message)
        except discord.errors.Forbidden:
            deletePermMsg = await self.bot.say("I require permissions to delete messages so I can delete user messages in this channel (to clean it a little).")
            hasPerms = False
        
        channelIDs = self.getEligibleSuggestionChannels(ctx.message.channel.server)
        if not channel.id in channelIDs:
            if len(channelIDs) < 1:
                await self.bot.say("No channel has been set to receive suggestions. Have a moderator+ run `!suggestChannel`" \
                                   " in a channel that should accept suggestions.")
                return
            firstAvailableChannel = self.bot.get_channel(id=channelIDs[0]).mention
            deleteChannMsg = await self.bot.say("Wrong channel; use {}.".format(firstAvailableChannel))
            await asyncio.sleep(5)
            if not hasPerms:
                await self.bot.delete_message(deletePermMsg)
            await self.bot.delete_message(deleteChannMsg)
            return
        else:
            channelToPostTo = channel.id

        embedTitle = "**Suggestion by {}**".format(user.name)
        embedDescription = msg.content[9:]
        embedColor = 0x0C60E4
        embed = discord.Embed(title=embedTitle, description=embedDescription, color=embedColor)

        postedMsg = await self.bot.send_message(discord.Object(id=channelToPostTo), embed=embed)
        await self.bot.add_reaction(postedMsg, "👍")
        await self.bot.add_reaction(postedMsg, "😑")
        await self.bot.add_reaction(postedMsg, "👎")
            
        if not hasPerms:
            await asyncio.sleep(5)
            await self.bot.delete_message(deletePermMsg)
        return

    @commands.command(pass_context=True)
    @checks.admin_or_permissions(manage_server=True)
    async def suggestChannel(self, ctx):
        """Toggles what channels accept and post suggestions."""

        user = ctx.message.author
        channel = ctx.message.channel
        server = channel.server
 
        try:
            self.suggestData = deepcopy(self.suggestData)
            acceptedChannels = self.suggestData[server.id]
        except KeyError:
            self.suggestData[server.id] = []
            acceptedChannels = []

        await self.bot.delete_message(ctx.message)
        if not (channel.id in self.suggestData[server.id]):
            acceptedChannels.append(channel.id)
            self.suggestData[server.id] = acceptedChannels
            dataIO.save_json(self.filePath, self.suggestData)
            deleteMsg = await self.bot.say("This channel now accepts `!suggest`ions.")
            await asyncio.sleep(5)
            await self.bot.delete_message(deleteMsg)
        else:
            acceptedChannels.remove(channel.id)
            self.suggestData[server.id] = acceptedChannels
            dataIO.save_json(self.filePath, self.suggestData)
            deleteMsg = await self.bot.say("This channel no longer accepts `!suggest`ions.")
            await asyncio.sleep(5)
            await self.bot.delete_message(deleteMsg)
        return

def check_folders():
    if not os.path.exists("data/suggestions"):
        print("Creating data/suggestions folder...")
        os.makedirs("data/suggestions")

def check_files():
    file = "data/suggestions/channelData.json"
    if not dataIO.is_valid_json(file):
        print("Creating default suggestions' channelData.json...")
        dataIO.save_json(file, {})

def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(Suggestions(bot))