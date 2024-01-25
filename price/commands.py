from discord.ext import commands
from discord.ext.commands import Context
from shared.settings import Gas

def setup_market_commands(bot: commands.Bot) -> None:
    @bot.command(name="gas")
    async def price(ctx: Context, *args) -> None:
        # Initialize the Gas class
        # If you have a method to fetch the gas prices and pass them to the Gas class, use it here
        gas = Gas()

        # Send the gas prices to the channel
        await ctx.send(gas.message)