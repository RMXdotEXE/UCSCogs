import discord
from redbot.core import commands
from enum import Enum
from redbot.core import checks
import asyncio
from test.test_dummy_thread import DELAY

class Ranks(Enum):
    GRANDCHAMPION2000 = "Grand Champion - 2000"
    GRANDCHAMPION1900 = "Grand Champion - 1900"
    GRANDCHAMPION1800 = "Grand Champion - 1800"
    GRANDCHAMPION1700 = "Grand Champion - 1700"
    GRANDCHAMPION1600 = "Grand Champion - 1600"
    GRANDCHAMPION1500 = "Grand Champion - 1500"
    CHAMPION3 = "Champion III"
    CHAMPION2 = "Champion II"
    CHAMPION1 = "Champion I"
    DIAMOND3 = "Diamond III"
    DIAMOND2 = "Diamond II"
    DIAMOND1 = "Diamond I"
    PLATINUM3 = "Platinum III"
    PLATINUM2 = "Platinum II"
    PLATINUM1 = "Platinum I"
    GOLD3 = "Gold III"
    GOLD2 = "Gold II"
    GOLD1 = "Gold I"
    SILVER3 = "Silver III"
    SILVER2 = "Silver II"
    SILVER1 = "Silver I"
    BRONZE3 = "Bronze III"
    BRONZE2 = "Bronze II"
    BRONZE1 = "Bronze I"
    
    @classmethod
    def hasRank(cls, rank):
        return any(rank == ranking.value for ranking in cls)

    
class RankColors(Enum):
    GRANDCHAMPION2000 = 0x740bfa
    GRANDCHAMPION1900 = 0x740bfa
    GRANDCHAMPION1800 = 0x740bfa
    GRANDCHAMPION1700 = 0x740bfa
    GRANDCHAMPION1600 = 0x740bfa
    GRANDCHAMPION1500 = 0x740bfa
    CHAMPION3 = 0xb62db6
    CHAMPION2 = 0xee5aee
    CHAMPION1 = 0xf999fd
    DIAMOND3 = 0x0f2f89
    DIAMOND2 = 0x0549d6
    DIAMOND1 = 0x427fff
    PLATINUM3 = 0x2eb9b9
    PLATINUM2 = 0x43d8d8
    PLATINUM1 = 0x7eecec
    GOLD3 = 0xdfb41f
    GOLD2 = 0xcfa809
    GOLD1 = 0xceb505
    SILVER3 = 0x7c7b7b
    SILVER2 = 0x9b9b9b
    SILVER1 = 0xb4b4b4
    BRONZE3 = 0x3b1e01
    BRONZE2 = 0x864e1f
    BRONZE1 = 0xbe7f48

embedColor = 0x0C60E4
notified = False
    
class RankTags(commands.Cog):
    """The RankTags cog that controls users' desires to opt-in/out of taggable versions of their roles."""

    @commands.command(aliases=['tp'])
    async def togglePings(self, ctx):
        """Add/remove a taggable version of your rank role."""
        
        user = ctx.author
        userRoles = user.roles
        
        try:
            await ctx.message.delete()
        except discord.errors.Forbidden:
            global notified
            notified = notified
            if not notified:
                await ctx.send("I require permissions to delete messages. This won't stop the function, but allows me to automatically delete messages.")
                notified = True
        
        for role in userRoles:
            if Ranks.hasRank(role.name):
                await self.adjustRole(ctx, "{}\'".format(role.name))
                return
            
        msgString = "{}\nYou don't have an RL Rank role. Contact staff to assign a role to you.".format(user.mention)
        await self.concludeFunction(ctx, msgString)
        return
                
    async def adjustRole(self, ctx, role):
        user = ctx.author
        guild = ctx.guild
        await ctx.message.delete()
        grabbedRole = discord.utils.get(guild.roles, name=role)
        if grabbedRole is None:
            msgString = "The role **{}** doesn't exist yet!".format(role)
        if grabbedRole in user.roles:
            await user.remove_roles(grabbedRole)
            msgString = "{}\nYou will no longer receive **{}** pings.".format(user.mention, grabbedRole.name[:-1])
        else:
            await user.add_roles(grabbedRole)
            msgString = "{}\nYou will now receive **{}** pings.".format(user.mention, grabbedRole.name[:-1])
        await self.concludeFunction(ctx, msgString)
        return

    @commands.command(aliases=['sr'])
    @checks.admin_or_permissions(manage_guild=True)
    async def scanRanks(self, ctx):
        """Creates place-holding roles that don't currently exist."""

        def embedMsg(text, _title:str = "**Scanning Ranks**"):
            return discord.Embed(title=_title, description=text, color=embedColor)
        
        guild = ctx.guild
        user = ctx.author
        guildRoles = []
        missingRoles = []
        requiredRoles = []
        missingRolesMsg = ""
        alreadyDone = False
        
        try:
            await ctx.message.delete()
        except discord.errors.Forbidden:
            global notified
            notified = notified
            if not notified:
                await ctx.send("I require permissions to delete messages. This won't stop the function, but allows me to automatically delete messages.")
                notified = True

        for rank in Ranks:
            requiredRoles.append(rank.value)
        for rank in Ranks:
            requiredRoles.append("{}\'".format(rank.value))
            
        for roleObject in guild.roles:
            guildRoles.append(roleObject.name)

        for entry in requiredRoles:
            if not (entry in guildRoles):
                missingRoles.append(entry)
        
        tmp = 0
        for entry in missingRoles:
            if tmp < 10:
                missingRolesMsg += "{}\n".format(entry)
            tmp += 1
            
        if tmp >= 10:
            missingRolesMsg += "+ {} more...".format(tmp)
        
        if missingRolesMsg == "":
            # Roles already implemented, dont go in loop.
            alreadyDone = True
            msgText = "All roles are already implemented in the server. \n Would you like to re-order them anyways?"
            msg = await ctx.send(embed=embedMsg(msgText))
            await msg.add_reaction('✅')
            await msg.add_reaction('🚫')
        else:
            # Some roles not implemented, go in the loop.
            msgText = "These roles are missing from the server: \n{}\nWould you like me to automatically create them?".format(missingRolesMsg)
            msg = await ctx.send(embed=embedMsg(msgText))
            await msg.add_reaction('✅')
            await msg.add_reaction('🚫')

        # ✅: First create roles if not alreadyDone, then call reorder
        try:
            reaction, user = await ctx.bot.wait_for('reaction_add', check=lambda r, u: \
                (u == user and (str(r.emoji) == '✅' or str(r.emoji) == '🚫')), timeout=15)
        except asyncio.TimeoutError:
            await msg.clear_reactions()
            await msg.edit(embed=embedMsg("Cancelling operation; no response."))
            await self.killMsg(msg)
            return
        
        if str(reaction.emoji) == '✅':
            await msg.clear_reactions()
            msgText = "Say the role that will be the first role above the RL Rank hierarchy."
            await msg.edit(embed=embedMsg(msgText))
        elif str(reaction.emoji) == '🚫':
            await msg.clear_reactions()
            await msg.edit(embed=embedMsg("Cancelling operation; user denied action."))
            await self.killMsg(msg)
            return
        
        try:   
            msgResponse = await ctx.bot.wait_for('message', check=lambda m: (m.author == user), timeout=15)
        except asyncio.TimeoutError:
            await msg.edit(embed=embedMsg("Cancelling operation; no response."))
            await self.killMsg(msg)
            return
        answer = msgResponse.content
        await msgResponse.delete()
        # answer is in form of either "ExampleRole" or "@ExampleRole". Remove the @ if present
        if "@" in answer:
            answer = answer[1:]

        # Grab the role
        roleResponse = discord.utils.get(guild.roles, name=answer)
        if roleResponse is None:
            msgText = "That role doesn't exist. Cancelling operation incase of unwanted results."
            await msg.edit(embed=embedMsg(msgText))
            return
        else:
            # all good, start process. create roles if not alreadyDone
            if not alreadyDone:
                await msg.edit(embed=embedMsg(text="Adding the required roles...", _title="**Adding Roles**"))
                for entry in missingRoles:
                    await guild.create_role(name=entry)
                for rlRole in requiredRoles:
                    role = discord.utils.get(guild.roles, name=rlRole)
                    perms = role.permissions
                    perms.update(mention_everyone=False, send_tts_messages=True)
                    if "\'" in rlRole:
                        color = RankColors[Ranks(rlRole[:-1]).name]
                        mentionable = True
                        hoist = False
                    else:
                        color = RankColors[Ranks(rlRole).name]
                        mentionable = False
                        hoist = True
                    await role.edit(color=color,
                                    mentionable=mentionable,
                                    hoist=hoist,
                                    permissions=perms)
                    msgText = "The roles have been created; reordering them around __{}__. This may take time.".format(answer)
                await msg.edit(embed=embedMsg(msgText))
            else:
                msgText = "Reordering roles about __{}__. This may take time.".format(answer)
                await msg.edit(embed=embedMsg(msgText, _title="**Reordering Roles**"))
            await self.reOrderRoles(ctx, requiredRoles, roleResponse)
            msgText = "The roles have been managed. If there are any problems, DM @RMX."
            await msg.edit(embed=embedMsg(msgText))
            await self.killMsg(msg)
        return
    
    @commands.command(pass_context=True)
    @checks.admin_or_permissions(manage_guild=True)
    async def reSortRanks(self, ctx):
        
        def embedMsg(text):
            return discord.Embed(title="**Reordering Roles**", description=text, color=embedColor)
        
        guild = ctx.guild

        try:
            await ctx.message.delete()
        except discord.errors.Forbidden:
            global notified
            notified = notified
            if not notified:
                await ctx.send("I require permissions to delete messages. This won't stop the function, but allows me to automatically delete messages.")
                notified = True

        msgText = "Say the role that will be the first role above the RL Rank hierarchy."
        msg = await ctx.send(embed=embedMsg(msgText))
        try:   
            answer = await ctx.bot.wait_for('message', check=lambda m: (m.author == user), timeout=15)
        except asyncio.TimeoutError:
            await msg.edit(embed=embedMsg("Cancelling operation; no response."))
            await self.killMsg(msg)
            return
        answer = answer.content
        if "@" in answer:
            answer = answer[1:]
        roleResponse = discord.utils.get(guild.roles, name=answer)
        if roleResponse is None:
            msgText = "That role doesn't exist. Cancelling operation incase of unwanted results."
            await msg.edit(embed=embedMsg(msgText))
            await self.killMsg(msg)
            return
        
        requiredRoles = []
        for rank in Ranks:
            requiredRoles.append(rank.value)
        for rank in Ranks:
            requiredRoles.append("{}\'".format(rank.value))
            
        msgText = "Reordering roles; some time will take before they are fully ordered correctly."
        await msg.edit(embed=embedMsg(msgText))
        await self.reOrderRoles(ctx, requiredRoles, roleResponse)
        msgText = "The roles have been reordered. If there are any problems, DM @RMX."
        await msg.edit(embed=embedMsg(msgText))
        await self.killMsg(msg)

    async def reOrderRoles(self, ctx, requiredRoles, roleResponse):
        guild = ctx.guild
        tmp = 1
        for rlRole in requiredRoles:
            role = discord.utils.get(guild.roles, name=rlRole)
            try:
                await role.edit(position=roleResponse.position - tmp)
                tmp += 1
            except discord.errors.HTTPException:
                await ctx.send("Apparently I don't have permissions, but this is Discord's fault. Give me the \"Manage Roles\" permission just to be safe. Roles may not be done correctly.")
                break
            except AttributeError:
                await ctx.send("**WARNING:** The **{}** role is not implemented in this server. \n This may cause the operation to break. Please use `!scanRanks` " \
                                   "or manually add the role, and then try sorting them again. Skipping for now...".format(rlRole))
        return
        
    @commands.command(aliases=['del'])
    @checks.admin_or_permissions(manage_guild=True)
    async def deleteAllRanks(self, ctx, deleteAll:bool=False):
        
        def embedMsg(text, _title:str = "**Deleting RL Roles**"):
            return discord.Embed(title=_title, description=text, color=embedColor)
        
        """Deletes all RL Rank roles. USE WISELY."""
        
        try:
            await ctx.message.delete()
        except discord.errors.Forbidden:
            global notified
            notified = notified
            if not notified:
                await ctx.send("I require permissions to delete messages. This won't stop the function, but allows me to automatically delete messages.")
                notified = True

        msg = await ctx.send(embed=embedMsg("Deleting all RL Rank roles..."))
        
        guild = ctx.guild
        rlRankRoles = []
        for rank in Ranks:
            rlRankRoles.append(rank.value)
            rlRankRoles.append("{}\'".format(rank.value))
            
        for role in rlRankRoles:
            deleteRole = discord.utils.get(guild.roles, name=role)
            if deleteRole is None:
                continue
            if (not ("\'" in deleteRole.name)) and deleteAll:
                await deleteRole.delete()
            else:
                if "\'" in deleteRole.name:
                    await deleteRole.delete()
            
        await msg.edit(embed=embedMsg("All RL ranks deleted. Use `!scanRanks` to reinstantiate them."))
        await self.killMsg(msg)
        
    async def concludeFunction(self, ctx, msgString, delay:int=10):
        msg = await ctx.send(msgString)
        await self.killMsg(msg, delay)
        return
    
    async def killMsg(self, msg, delay:int=10):
        await asyncio.sleep(delay)
        await msg.delete()
        return


def setup(bot):
    bot.add_cog(RankTags(bot))
