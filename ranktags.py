import discord
from discord.ext import commands
from enum import Enum
from .utils import checks
import asyncio

class Ranks(Enum):
    BRONZE1           = "Bronze I"
    BRONZE2           = "Bronze II"
    BRONZE3           = "Bronze III"
    SILVER1           = "Silver I"
    SILVER2           = "Silver II"
    SILVER3           = "Silver III"
    GOLD1             = "Gold I"
    GOLD2             = "Gold II"
    GOLD3             = "Gold III"
    PLATINUM1         = "Platinum I"
    PLATINUM2         = "Platinum II"
    PLATINUM3         = "Platinum III"
    DIAMOND1          = "Diamond I"
    DIAMOND2          = "Diamond II"
    DIAMOND3          = "Diamond III"
    CHAMPION1         = "Champion I"
    CHAMPION2         = "Champion II"
    CHAMPION3         = "Champion III"
    GRANDCHAMPION1500 = "Grand Champion - 1500"
    GRANDCHAMPION1600 = "Grand Champion - 1600"
    GRANDCHAMPION1700 = "Grand Champion - 1700"
    GRANDCHAMPION1800 = "Grand Champion - 1800"
    GRANDCHAMPION1900 = "Grand Champion - 1900"
    GRANDCHAMPION2000 = "Grand Champion - 2000"
    
    @classmethod
    def hasRank(cls, rank):
        return any(rank == ranking.value for ranking in cls)
    
class RankColors(Enum):
    BRONZE1           = 0xbe7f48
    BRONZE2           = 0x864e1f
    BRONZE3           = 0x3b1e01
    SILVER1           = 0xb4b4b4
    SILVER2           = 0x9b9b9b
    SILVER3           = 0x7c7b7b
    GOLD1             = 0xceb505
    GOLD2             = 0xcfa809
    GOLD3             = 0xdfb41f
    PLATINUM1         = 0x7eecec
    PLATINUM2         = 0x43d8d8
    PLATINUM3         = 0x2eb9b9
    DIAMOND1          = 0x427fff
    DIAMOND2          = 0x0549d6
    DIAMOND3          = 0x0f2f89
    CHAMPION1         = 0xf999fd
    CHAMPION2         = 0xee5aee
    CHAMPION3         = 0xb62db6
    GRANDCHAMPION1500 = 0x740bfa
    GRANDCHAMPION1600 = 0x740bfa
    GRANDCHAMPION1700 = 0x740bfa
    GRANDCHAMPION1800 = 0x740bfa
    GRANDCHAMPION1900 = 0x740bfa
    GRANDCHAMPION2000 = 0x740bfa
    
class RankTags:
    """The RankTags cog that controls users' desires to opt-in/out of taggable versions of their roles."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def toggleTags(self, ctx):
        """Add/remove a taggable version of your rank role."""
        
        user = ctx.message.author
        userRoles = user.roles
        
        for role in userRoles:
            if Ranks.hasRank(role.name):
                await self.adjustRole(ctx, "{}\'".format(role.name))
                return
            
        deleteMsg = await self.bot.say("{}\nYou don't have an RL Rank role. Contact staff to assign a role to you.".format(user.mention))
        await asyncio.sleep(10)
        await self.bot.delete_message(deleteMsg)
        return
                
    async def adjustRole(self, ctx, role):
        user = ctx.message.author
        server = ctx.message.server
        await self.bot.delete_message(ctx.message)
        grabbedRole = discord.utils.get(server.roles, name=role)
        if grabbedRole is None:
            await self.bot.say("The role **{}** doesn't exist yet!".format(role))
            return
        if grabbedRole in user.roles:
            await self.bot.remove_roles(user, grabbedRole)
            deleteMsg = await self.bot.say("{}\nYou will no longer receive **{}** pings.".format(user.mention, grabbedRole.name[:-1]))
        else:
            await self.bot.add_roles(user, grabbedRole)
            deleteMsg =  await self.bot.say("{}\nYou will now receive **{}** pings.".format(user.mention, grabbedRole.name[:-1]))
        await asyncio.sleep(10)
        await self.bot.delete_message(deleteMsg)
        return
            
    @commands.command(pass_context=True)
    @checks.admin_or_permissions(manage_server=True)
    async def scanRanks(self, ctx):
        """Creates place-holding roles that don't currently exist."""

        server = ctx.message.server
        serverRoles = []
        missingRoles = []
        requiredRoles = []
        missingRolesMsg = ""
        
        for rank in Ranks:
            requiredRoles.append(rank.value)
            requiredRoles.append("{}\'".format(rank.value))
            
        for roleObject in server.roles:
            serverRoles.append(roleObject.name)

        for entry in requiredRoles:
            if not (entry in serverRoles):
                missingRoles.append(entry)
        
        for entry in missingRoles:
            missingRolesMsg += "{}\n".format(entry)
            x = entry
        
        if missingRolesMsg == "":
            await self.bot.say("All roles are already implemented in the server.")
            return
        else:
            rolesMsg = await self.bot.say("These roles are missing from the server: \n{}".format(missingRolesMsg))
            
        await self.bot.say("Would you like me to automatically create the missing roles?")
        answer = await self.bot.wait_for_message(timeout=15, author=ctx.message.author)
        await self.bot.delete_message(rolesMsg)
        
        if answer is None:
            await self.bot.say("Cancelling operation; no response.")
            await asyncio.sleep(10)
            return
        answer = answer.content
        
        if answer == "yes":
            await self.bot.say("Say the role that will be the first role lower than the RL Rank hierarchy.")
        else:
            await self.bot.say("Cancelling operation.")
            await asyncio.sleep(10)
            return
        
        answer = await self.bot.wait_for_message(timeout=30, author=ctx.message.author)
        if answer is None:
            await self.bot.say("Cancelling operation; no response.")
            await asyncio.sleep(10)
            return
        answer = answer.content
        
        if "@" in answer:
            answer = answer[1:]
        roleResponse = discord.utils.get(server.roles, name=answer)
        if roleResponse is None:
            await self.bot.say("That role doesn't exist. Cancelling operation incase of unwanted results.")
            await asyncio.sleep(10)
            return
        else:
            await self.bot.say("Adding roles...")
            underRole = int(roleResponse.position) - 1
            missingRoles.reverse()
            for entry in missingRoles:
                await self.bot.create_role(server, name=entry)
                underRole += 1
            requiredRoles.reverse()
            for rlRole in requiredRoles:
                role = discord.utils.get(server.roles, name=rlRole)
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
                await self.bot.edit_role(server, role,
                                         color=color,
                                         mentionable=mentionable,
                                         hoist=hoist,
                                         permissions=perms)
            await self.bot.say("The roles have been created; some time will take before they are fully ordered correctly.")
            requiredRoles.reverse()
            underRole = roleResponse.position
            for rlRole in requiredRoles:
                role = discord.utils.get(server.roles, name=rlRole)
                try:
                    await self.bot.move_role(server, role, underRole)
                except discord.errors.HTTPException:
                    await self.bot.say("Apparently I don't have permissions, but this is Discord's fault. Give me the \"Manage Roles\" permission just to be safe.")
                    break
                await asyncio.sleep(1)
            await self.bot.say("The roles have been ordered; navigate to Server Settings and modify the roles to suit " \
                               "your liking.")
        return
        
        
    @commands.command(pass_context=True)
    @checks.admin_or_permissions(manage_server=True)
    async def deleteAllRanks(self, ctx, deleteAll:bool=False, areUSure:bool=False, absolutelySure:bool=False):
        """Deletes all RL Rank roles. USE WISELY."""
        
        await self.bot.say("Deleting all RL Rank roles...")
        
        server = ctx.message.server
        rlRankRoles = []
        for rank in Ranks:
            rlRankRoles.append(rank.value)
            rlRankRoles.append("{}\'".format(rank.value))
            
        for role in rlRankRoles:
            deleteRole = discord.utils.get(server.roles, name=role)
            if deleteRole is None:
                continue
            if (not ("\'" in deleteRole.name)) and deleteAll and areUSure and absolutelySure:
                await self.bot.delete_role(server, deleteRole)
            else:
                if "\'" in deleteRole.name:
                    await self.bot.delete_role(server, deleteRole)
            
        await self.bot.say("All RL ranks deleted. Use `!scanRanks` to reinstantiate them.")

def setup(bot):
    bot.add_cog(RankTags(bot))