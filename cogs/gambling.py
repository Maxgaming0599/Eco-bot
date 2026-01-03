# cogs/gambling.py
import discord
from discord.ext import commands
import random
import asyncio
from database import get_balance, update_balance, get_user_limit

class Gambling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lottery_numbers = {}
        self.crash_values = {}

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def dice(self, ctx, amount: int):
        if amount <= 0:
            return await ctx.send("Bet must be positive!", ephemeral=True)
        balance = await get_balance(ctx.author.id)
        if balance < amount:
            return await ctx.send("Not enough funds!", ephemeral=True)
        
        roll = random.randint(1, 6)
        if roll > 3:
            win = amount * 2
            await update_balance(ctx.author.id, win)
            await ctx.send(f"🎲 Rolled {roll}! You won **{win:,}**")
        else:
            await update_balance(ctx.author.id, -amount)
            await ctx.send(f"🎲 Rolled {roll}! You lost **{amount:,}**")

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def slots(self, ctx, amount: int):
        if amount <= 0: return await ctx.send("Bet must be positive!", ephemeral=True)
        balance = await get_balance(ctx.author.id)
        if balance < amount: return await ctx.send("Not enough funds!", ephemeral=True)
        
        symbols = ["🍒", "🍋", "🍇", "💎", "7️⃣"]
        reel = [random.choice(symbols) for _ in range(3)]
        
        if reel[0] == reel[1] == reel[2]:
            if reel[0] == "7️⃣":
                win = amount * 10
            else:
                win = amount * 5
        elif reel[0] == reel[1] or reel[1] == reel[2]:
            win = amount * 2
        else:
            win = 0
        
        if win > 0:
            await update_balance(ctx.author.id, win)
            await ctx.send(f"🎰 {reel[0]} | {reel[1]} | {reel[2]} - You won **{win:,}**!")
        else:
            await update_balance(ctx.author.id, -amount)
            await ctx.send(f"🎰 {reel[0]} | {reel[1]} | {reel[2]} - You lost **{amount:,}**")

    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def blackjack(self, ctx, amount: int):
        if amount <= 0: return await ctx.send("Bet must be positive!", ephemeral=True)
        balance = await get_balance(ctx.author.id)
        if balance < amount: return await ctx.send("Not enough funds!", ephemeral=True)
        
        def get_hand_value(hand):
            value = sum(min(card, 10) for card in hand)
            aces = sum(1 for card in hand if card == 11)
            while value > 21 and aces:
                value -= 10
                aces -= 1
            return value
        
        deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11] * 4
        random.shuffle(deck)
        
        player_hand = [deck.pop(), deck.pop()]
        dealer_hand = [deck.pop(), deck.pop()]
        
        player_value = get_hand_value(player_hand)
        dealer_value = get_hand_value(dealer_hand)
        
        # Player turn
        while player_value < 21:
            await ctx.send(f"Your hand: {player_hand} = {player_value}\nDealer shows: [{dealer_hand[0]}]")
            await ctx.send("Hit or Stand? (reply)")
            
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel
            
            try:
                msg = await self.bot.wait_for('message', check=check, timeout=30)
                if msg.content.lower().startswith('h'):
                    player_hand.append(deck.pop())
                    player_value = get_hand_value(player_hand)
                    if player_value > 21:
                        await update_balance(ctx.author.id, -amount)
                        await ctx.send(f"Bust! You lose **{amount:,}**")
                        return
                else:
                    break
            except asyncio.TimeoutError:
                await ctx.send("Timeout! You lose.")
                return
        
        # Dealer turn
        while dealer_value < 17:
            dealer_hand.append(deck.pop())
            dealer_value = get_hand_value(dealer_hand)
        
        if dealer_value > 21 or player_value > dealer_value:
            win = amount * 2
            await update_balance(ctx.author.id, win)
            await ctx.send(f"You win! {player_value} vs {dealer_value}. Won **{win:,}**")
        elif player_value == dealer_value:
            await ctx.send(f"Push! {player_value} vs {dealer_value}. Bet returned.")
        else:
            await update_balance(ctx.author.id, -amount)
            await ctx.send(f"You lose! {player_value} vs {dealer_value}. Lost **{amount:,}**")

    @commands.command()
    @commands.cooldown(1, 45, commands.BucketType.user)
    async def roulette(self, ctx, amount: int, bet: str):
        if amount <= 0: return await ctx.send("Bet must be positive!", ephemeral=True)
        balance = await get_balance(ctx.author.id)
        if balance < amount: return await ctx.send("Not enough funds!", ephemeral=True)
        
        number = random.randint(0, 36)
        is_red = number in [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
        is_black = number in [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
        
        win = 0
        if bet == str(number):
            win = amount * 35
        elif bet.lower() == 'red' and is_red:
            win = amount * 2
        elif bet.lower() == 'black' and is_black:
            win = amount * 2
        elif bet.lower() == 'even' and number % 2 == 0 and number != 0:
            win = amount * 2
        elif bet.lower() == 'odd' and number % 2 == 1:
            win = amount * 2
        
        if win > 0:
            await update_balance(ctx.author.id, win)
            await ctx.send(f"🎯 {number} ({'Red' if is_red else 'Black' if is_black else 'Green'}) - You won **{win:,}**!")
        else:
            await update_balance(ctx.author.id, -amount)
            await ctx.send(f"🎯 {number} - You lost **{amount:,}**")

    @commands.command()
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def lottery(self, ctx, number: int):
        if not 1 <= number <= 10:
            return await ctx.send("Pick a number between 1-10!", ephemeral=True)
        
        cost = 1000
        balance = await get_balance(ctx.author.id)
        if balance < cost:
            return await ctx.send("Lottery costs 1,000!", ephemeral=True)
        
        await update_balance(ctx.author.id, -cost)
        winning = random.randint(1, 10)
        
        if number == winning:
            win = 10000
            await update_balance(ctx.author.id, win)
            await ctx.send(f"🎉 You won the lottery! **{win:,}**")
        else:
            await ctx.send(f"❌ Lost. Winning number was {winning}")

    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def crash(self, ctx, amount: int):
        if amount <= 0: return await ctx.send("Bet must be positive!", ephemeral=True)
        balance = await get_balance(ctx.author.id)
        if balance < amount: return await ctx.send("Not enough funds!", ephemeral=True)
        
        await update_balance(ctx.author.id, -amount)
        multiplier = 1.0
        message = await ctx.send(f"🚀 Crash starting at 1.0x")
        
        for i in range(20):
            await asyncio.sleep(1)
            multiplier += random.uniform(0.1, 0.5)
            await message.edit(content=f"🚀 Crash: {multiplier:.1f}x")
            
            if random.random() < 0.1 * (i / 20):  # Increasing crash chance
                await message.edit(content=f"💥 CRASH at {multiplier:.1f}x! You lost.")
                return
        
        win = int(amount * multiplier)
        await update_balance(ctx.author.id, win)
        await message.edit(content=f"✅ You cashed out at {multiplier:.1f}x! Won **{win:,}**")

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def highlow(self, ctx, amount: int, guess: str):
        if amount <= 0: return await ctx.send("Bet must be positive!", ephemeral=True)
        balance = await get_balance(ctx.author.id)
        if balance < amount: return await ctx.send("Not enough funds!", ephemeral=True)
        
        card1 = random.randint(1, 13)
        card2 = random.randint(1, 13)
        
        if guess.lower() == 'high':
            win = card2 > card1
        else:
            win = card2 < card1
        
        if win:
            win_amount = amount * 2
            await update_balance(ctx.author.id, win_amount)
            await ctx.send(f"Cards: {card1} vs {card2} - You won **{win_amount:,}**!")
        else:
            await update_balance(ctx.author.id, -amount)
            await ctx.send(f"Cards: {card1} vs {card2} - You lost **{amount:,}**")

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def poker(self, ctx, amount: int):
        if amount <= 0: return await ctx.send("Bet must be positive!", ephemeral=True)
        balance = await get_balance(ctx.author.id)
        if balance < amount: return await ctx.send("Not enough funds!", ephemeral=True)
        
        # Simplified poker: 5 card draw, compare hand strength
        deck = list(range(1, 14)) * 4
        random.shuffle(deck)
        hand = [deck.pop() for _ in range(5)]
        
        # Check for pairs, three of a kind, etc.
        counts = {}
        for card in hand:
            counts[card] = counts.get(card, 0) + 1
        
        max_count = max(counts.values())
        
        if max_count == 5:
            win = amount * 100  # Five of a kind (improbable but possible)
        elif max_count == 4:
            win = amount * 25   # Four of a kind
        elif max_count == 3 and 2 in counts.values():
            win = amount * 10   # Full house
        elif max_count == 3:
            win = amount * 5    # Three of a kind
        elif list(counts.values()).count(2) == 2:
            win = amount * 3    # Two pair
        elif max_count == 2:
            win = amount * 1.5  # One pair
        else:
            win = 0
        
        if win > 0:
            await update_balance(ctx.author.id, int(win))
            await ctx.send(f"🃏 Hand: {hand} - You won **{int(win):,}**!")
        else:
            await update_balance(ctx.author.id, -amount)
            await ctx.send(f"🃏 Hand: {hand} - You lost **{amount:,}**")

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def guessnumber(self, ctx, amount: int, guess: int):
        if amount <= 0: return await ctx.send("Bet must be positive!", ephemeral=True)
        balance = await get_balance(ctx.author.id)
        if balance < amount: return await ctx.send("Not enough funds!", ephemeral=True)
        
        number = random.randint(1, 100)
        if guess == number:
            win = amount * 50
            await update_balance(ctx.author.id, win)
            await ctx.send(f"🎯 Exact match! You won **{win:,}**!")
        elif abs(guess - number) <= 5:
            win = amount * 5
            await update_balance(ctx.author.id, win)
            await ctx.send(f"🎯 Close! ({number}) You won **{win:,}**!")
        else:
            await update_balance(ctx.author.id, -amount)
            await ctx.send(f"❌ Wrong. Number was {number}. Lost **{amount:,}**")

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def coinflip(self, ctx, amount: int, choice: str):
        if amount <= 0: return await ctx.send("Bet must be positive!", ephemeral=True)
        balance = await get_balance(ctx.author.id)
        if balance < amount: return await ctx.send("Not enough funds!", ephemeral=True)
        
        result = random.choice(["heads", "tails"])
        if choice.lower() == result:
            win = amount * 2
            await update_balance(ctx.author.id, win)
            await ctx.send(f"🪙 {result.title()}! You won **{win:,}**!")
        else:
            await update_balance(ctx.author.id, -amount)
            await ctx.send(f"🪙 {result.title()}! You lost **{amount:,}**")

async def setup(bot):
    await bot.add_cog(Gambling(bot))
