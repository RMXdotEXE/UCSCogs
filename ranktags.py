import discord
from discord.ext import commands
from enum import Enum
from .utils import checks
import asyncio

class Ranks(Enum):
    GRANDCHAMPION2000 = "Grand Champion - 2000"
    GRANDCHAMPION1900 = "Grand Champion - 1900"
    GRANDCHAMPION1800 = "Grand Champion - 1800"
    GRANDCHAMPION1700 = "Grand Champion - 1700"
    GRANDCHAMPION1600 = "Grand Champion - 1600"
    GRANDCHAMPION1500 = "Grand Champion - 1500"
    CHAMPION3         = "Champion III"
    CHAMPION2         = "Champion II"
    CHAMPION1         = "Champion I"
    DIAMOND3          = "Diamond III"
    DIAMOND2          = "Diamond II"
    DIAMOND1          = "Diamond I"
    PLATINUM3         = "Platinum III"
    PLATINUM2         = "Platinum II"
    PLATINUM1         = "Platinum I"
    GOLD3             = "Gold III"
    GOLD2             = "Gold II"
    GOLD1             = "Gold I"
    SILVER3           = "Silver III"
    SILVER2           = "Silver II"
    SILVER1           = "Silver I"
    BRONZE3           = "Bronze III"
    BRONZE2           = "Bronze II"
    BRONZE1           = "Bronze I"
    
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
    CHAMPION3         = 0xb62db6
    CHAMPION2         = 0xee5aee
    CHAMPION1         = 0xf999fd
    DIAMOND3          = 0x0f2f89
    DIAMOND2          = 0x0549d6
    DIAMOND1          = 0x427fff
    PLATINUM3         = 0x2eb9b9
    PLATINUM2         = 0x43d8d8
    PLATINUM1         = 0x7eecec
    GOLD3             = 0xdfb41f
    GOLD2             = 0xcfa809
    GOLD1             = 0xceb505
    SILVER3           = 0x7c7b7b
    SILVER2           = 0x9b9b9b
    SILVER1           = 0xb4b4b4
    BRONZE3           = 0x3b1e01
    BRONZE2           = 0x864e1f
    BRONZE1           = 0xbe7f48
    
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
    async def printHierarchy(self, ctx):
        server = ctx.message.server
        missingRolesMsg = ""
        
        for role in server.role_hierarchy:
            missingRolesMsg += "INDEX {}: {}\n".format(server.role_hierarchy.index(role), role.name)
        await self.bot.say(missingRolesMsg)
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
        alreadyDone = False
        rolesMsg = None
        
        for rank in Ranks:
            #requiredRoles.append("{}\'".format(rank.value))
            requiredRoles.append(rank.value)
        for rank in Ranks:
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
            await self.bot.say("All roles are already implemented in the server. \n Would you like to re-order them anyways?")
            alreadyDone = True
        else:
            rolesMsg = await self.bot.say("These roles are missing from the server: \n{}".format(missingRolesMsg))
            await self.bot.say("Would you like me to automatically create the missing roles?")
        answer = await self.bot.wait_for_message(timeout=15, author=ctx.message.author)
        if not rolesMsg is None:
            await self.bot.delete_message(rolesMsg)
        
        if answer is None:
            await self.bot.say("Cancelling operation; no response.")
            await asyncio.sleep(10)
            return
        answer = answer.content
        
        if answer == "yes":
            await self.bot.say("Say the role that will be the first role above the RL Rank hierarchy.")
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
            if not alreadyDone:
                await self.bot.say("Adding roles...")
                for entry in missingRoles:
                    await self.bot.create_role(server, name=entry)
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
            else:
                await self.bot.say("Reordering roles; some time will take before they are fully ordered correctly.")
            await self.reOrderRoles(ctx, requiredRoles, roleResponse)
        return
    
    @commands.command(pass_context=True)
    @checks.admin_or_permissions(manage_server=True)
    async def reSortRanks(self, ctx):
        server = ctx.message.server
        await self.bot.say("Say the role that will be the first role above the RL Rank hierarchy.")
        answer = await self.bot.wait_for_message(timeout=30, author=ctx.message.author)
        if answer is None:
            await self.bot.say("Cancelling operation; no response.")
            await asyncio.sleep(10)
            return
        answer = answer.content
        roleResponse = discord.utils.get(server.roles, name=answer)
        if roleResponse is None:
            await self.bot.say("That role doesn't exist. Cancelling operation incase of unwanted results.")
            await asyncio.sleep(10)
            return
        
        requiredRoles = []
        for rank in Ranks:
            requiredRoles.append(rank.value)
        for rank in Ranks:
            requiredRoles.append("{}\'".format(rank.value))
        await self.bot.say("Reordering roles; some time will take before they are fully ordered correctly.")
        await self.reOrderRoles(ctx, requiredRoles, roleResponse)
        
    async def reOrderRoles(self, ctx, requiredRoles, roleResponse):
        server = ctx.message.server
        tmp = 1
        for rlRole in requiredRoles:
            role = discord.utils.get(server.roles, name=rlRole)
            try:
                await self.bot.move_role(server, role, roleResponse.position - tmp)
                tmp += 1
            except discord.errors.HTTPException:
                await self.bot.say("Apparently I don't have permissions, but this is Discord's fault. Give me the \"Manage Roles\" permission just to be safe.")
                break
            except AttributeError:
                await self.bot.say("**WARNING:** The **{}** role is not implemented in this server. \n This may cause the operation to break. Please use `!scanRanks` " \
                                   "or manually add the command, and then try sorting them again. Skipping for now...".format(rlRole))
            await asyncio.sleep(1)
        await self.bot.say("The roles have been ordered; navigate to Server Settings and modify the roles to suit " \
                           "your liking.")
        
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