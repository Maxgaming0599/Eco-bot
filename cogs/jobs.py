# cogs/jobs.py
import discord
from discord.ext import commands
import random
from datetime import datetime, timedelta
from database import (
    get_user_job, set_user_job, update_last_worked, get_job_details,
    get_all_jobs, add_job, remove_job, update_balance, get_balance,
    get_user_limit
)
from config import OWNER_ID

class Jobs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def work(self, ctx):
        user_id = ctx.author.id
        job_data = await get_user_job(user_id)
        
        if not job_data:
            return await ctx.send("You don't have a job! Use `-jobs` to see available jobs.", ephemeral=True)
        
        job_name = job_data['job_name']
        last_worked = job_data['last_worked']
        
        if last_worked:
            last_time = datetime.fromisoformat(last_worked)
            if datetime.now() < last_time + timedelta(seconds=3600):
                remaining = (last_time + timedelta(seconds=3600) - datetime.now()).total_seconds()
                return await ctx.send(f"⏳ You can work again in {int(remaining)} seconds!", ephemeral=True)
        
        job_details = await get_job_details(job_name)
        if not job_details:
            return await ctx.send("Job not found!", ephemeral=True)
        
        # Check admin limits
        limit = await get_user_limit(user_id)
        if limit > 0:
            balance = await get_balance(user_id)
            if balance >= limit:
                return await ctx.send("You've reached your limit!", ephemeral=True)
        
        earnings = random.randint(job_details['min_pay'], job_details['max_pay'])
        await update_balance(user_id, earnings)
        await update_last_worked(user_id)
        
        embed = discord.Embed(title="💼 Work Complete", color=0xFFD700)
        embed.add_field(name="Job", value=job_name, inline=False)
        embed.add_field(name="Earnings", value=f"{earnings:,}", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def jobs(self, ctx):
        jobs = await get_all_jobs()
        if not jobs:
            return await ctx.send("No jobs available!", ephemeral=True)
        
        embed = discord.Embed(title="Available Jobs", color=0x1E90FF)
        for job in jobs:
            embed.add_field(
                name=job[0],
                value=f"Pay: {job[1]:,}-{job[2]:,} | Unlock: {job[3]:,}",
                inline=False
            )
        await ctx.send(embed=embed)

    @commands.command()
    async def applyjob(self, ctx, job_name: str):
        job_details = await get_job_details(job_name)
        if not job_details:
            return await ctx.send("Job not found!", ephemeral=True)
        
        balance = await get_balance(ctx.author.id)
        if balance < job_details['unlock_cost']:
            return await ctx.send(f"You need {job_details['unlock_cost']:,} to unlock this job!", ephemeral=True)
        
        await update_balance(ctx.author.id, -job_details['unlock_cost'])
        await set_user_job(ctx.author.id, job_name)
        await ctx.send(f"✅ You are now a **{job_name}**!")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def addjob(self, ctx, name: str, min_pay: int, max_pay: int, unlock_cost: int):
        await add_job(name, min_pay, max_pay, unlock_cost)
        await ctx.send(f"✅ Added job: {name}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def removejob(self, ctx, name: str):
        await remove_job(name)
        await ctx.send(f"✅ Removed job: {name}")

async def setup(bot):
    await bot.add_cog(Jobs(bot))
