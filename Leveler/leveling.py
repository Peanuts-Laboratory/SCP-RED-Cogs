import time
import random
import discord
from pymongo import MongoClient
import pymongo
from redbot.core import Config, commands, checks


class Level(commands.Cog):
    """Leveling Command"""

    def __init__(self, bot):
        self.config = Config.get_conf(self, identifier=1072001)
        default_guild = {
            "MinXP" : 1, "MaxXP" : 25, "Enabled" : False}
        self.config.register_guild(**default_guild)
        self.bot = bot

    async def _requiredXP(self, lvl):
        requiredXP = pow(lvl, 1.75)
        return requiredXP * 50

    @commands.group(name="levelsettings")
    @checks.mod_or_permissions()
    async def settings(self, ctx):
        """Settings for Leveling Command"""
        pass

    @settings.command(name="enabled")
    @checks.mod_or_permissions()
    async def enabled(self, ctx : commands.Context, Enabled : bool = None):
        """If you want to enable. Do settings enabled true"""
        mongo_url = "placeholder"
        cluster = MongoClient(mongo_url)
        db = cluster["Leveler"]
        DBCollection = db[str(ctx.guild.id)]
        if Enabled is None:
            await ctx.send(f"Run {ctx.prefix} settings enabled True")
            return
        await self.config.guild(ctx.guild).Enabled.set(Enabled)
        await ctx.send(f"Leveler has been set to " + str(Enabled))

    @settings.group(name="general")
    @checks.admin()
    async def general(self, ctx):
        """General Bot Settings"""
        pass

    @settings.group(name="xp")
    @checks.mod_or_permissions()
    async def xp(self, ctx):
        """XP Leveling Settings"""
        pass

    @xp.command(name="min")
    @checks.admin()
    async def min_XP(self, ctx : commands.Context, Value : int):
        """Minimum XP Value"""
        await self.config.guild(ctx.guild).MinXP.set(Value)
        await ctx.send(f"The Minimum XP Value has been set to : **{Value}**")

    @xp.command(name="max")
    @checks.admin()
    async def max_XP(self, ctx: commands.Context, Value: int):
        """Minimum XP Value"""
        await self.config.guild(ctx.guild).MaxXP.set(Value)
        await ctx.send(f"The Maximum XP Value has been set to : **{Value}**")

    @commands.command(name="ranking")
    async def ranking(self, ctx):
        """View the Leaderboard"""
        Enabled = await self.config.guild(ctx.guild).Enabled()
        if not Enabled:
            return
        mongo_url = "placeholder"
        cluster = MongoClient(mongo_url)
        db = cluster["Leveler"]
        DBCollection = db[str(ctx.guild.id)]

        guild = ctx.guild

        rankings = ""

        list = DBCollection.find().sort("Rank", pymongo.DESCENDING).limit(10)
        for x in list:
            Rank = (x["Rank"])
            ID = (x["_id"])

            rankings = rankings + f"\n<@!{ID}> -- (Rank : {Rank})"
        embed = discord.Embed(title=f"Leaderboard", description=rankings, color=discord.Color.red())
        await ctx.send(embed=embed)


    @commands.command(name="rank")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def rank(self, ctx : commands.Context, User : discord.Member = None):
        Enabled = await self.config.guild(ctx.guild).Enabled()
        if not Enabled:
            return
        mongo_url = "placeholder"
        cluster = MongoClient(mongo_url)
        db = cluster["Leveler"]
        DBCollection = db[str(ctx.guild.id)]
        if User is None:
            User = ctx.author

        try:
            insertData = DBCollection.insert_one({"_id" : User.id, "Rank" : 1, "XP" : 10, "LastMessage" : "None", "LastTime" : time.time()})

            Result = DBCollection.find({"_id": User.id})
            for results in Result:
                Rank = (results['Rank'])
                XP = (results['XP'])
            embed = discord.Embed(title=f"{User.display_name}'s Level", color=discord.Color.gold())
            embed.add_field(name="Current Level", value=f"**{Rank}**")
            requiredXP = await self._requiredXP(Rank)
            getNum = (XP / requiredXP) * 100
            getNearstNum = (round(getNum / 10) * 10) / 10
            Bars = "▋"
            for x in range(0, int(getNearstNum - 1)):
                Bars = Bars + "▋"
            RemainingBars = "#"
            Meth = 10 - int(getNearstNum)
            for i in range(0, Meth - 1):
                RemainingBars = RemainingBars + "#"
            embed.add_field(name="XP %", value=f"[{Bars}{RemainingBars}] {round(getNum, 2)} % to the next level", inline=False)
            await ctx.send(embed=embed)

        except pymongo.errors.PyMongoError:
            Result = DBCollection.find({"_id": User.id})
            for results in Result:
                Rank = (results['Rank'])
                XP = (results['XP'])

            embed = discord.Embed(title=f"{User.display_name}'s Level", color=discord.Color.gold())
            embed.add_field(name="Current Level", value=f"**{Rank}**")
            requiredXP = await self._requiredXP(Rank)
            getNum = (XP / requiredXP) * 100
            getNearstNum = (round(getNum / 10) * 10) / 10
            Bars = "▋"
            for x in range(0, int(getNearstNum - 1)):
                Bars = Bars + "▋"
            RemainingBars = "▁"
            Meth = 10 - int(getNearstNum)
            for i in range(0, Meth - 1):
                RemainingBars = RemainingBars + "▁"
            embed.add_field(name="XP %", value=f"[{Bars}{RemainingBars}] {round(getNum, 2)} % to the next level", inline=False)
            await ctx.send(embed=embed)

    @commands.Cog.listener("on_message_without_command")
    async def on_message(self, message: discord.Message):
        Enabled = await self.config.guild(message.guild).Enabled()
        if not Enabled:
            return

        mongo_url = "placeholder"
        cluster = MongoClient(mongo_url)
        db = cluster["Leveler"]
        DBCollection = db[str(message.guild.id)]
        author = message.author
        if len(message.content) <= 8:
            return

        if author.bot:
            return
        curr_time = time.time()

        MinXP = await self.config.guild(message.guild).MinXP()
        MaxXP = await self.config.guild(message.guild).MaxXP()



        XPGive = random.randint(MinXP, MaxXP)

        try:
            insertData = DBCollection.insert_one({"_id": author.id, "Rank": 1, "XP": XPGive, "LastMessage": message.content, "LastTime" : time.time()})
        except pymongo.errors.PyMongoError:
            results = DBCollection.find({"_id" : author.id})
            for result in results:
                Rank = (result['Rank'])
                CurrentXP = (result["XP"])
                PrevMessage = (result["LastMessage"])
                LastTime = (result["LastTime"])

            if curr_time - LastTime >= 60:
                pass
            else:
                return

            if message.content == PrevMessage:
                return

            RequiredXP = await self._requiredXP(Rank)
            if (CurrentXP >= RequiredXP):
                await message.channel.send(f"{author.mention} **you have leveled up to Level {Rank + 1}!**")
                UpdateRank = DBCollection.update_one({"_id" : author.id}, {"$inc" : {"Rank" : 1}})
                XPUpdate = DBCollection.update_one({"_id": author.id}, {"$set": {"XP": 0}})
                pass
            else:
                pass

            UpdateXP = DBCollection.update_one({"_id" : author.id}, {"$inc" : {"XP" : XPGive}})
            UpdateMessage = DBCollection.update_one({"_id" : author.id}, {"$set" : {"LastMessage" : message.content}})
            return








