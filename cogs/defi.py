"""
File containing all DeFi-related bot commands and behaviors.
"""

from discord.ext import commands, tasks
import utils
from replit import db

# Commands pertaining to smart contract and wallet inspection and reporting
# Currently only works with Polygon network. To be extended further at a later point.
class DefiCommands(commands.Cog, name='DeFi Commands'):
  '''Commands for DeFi operations '''

  def __init__(self, bot):
    self.bot = bot
    self.latest_news = []
    self.update_news_feed.start()

  @commands.Cog.listener()
  async def on_member_join(self, ctx, member):
    """Trigger welcome message on new user join."""
    await ctx.send(f"Hi there {member.name}. Welcome to our DeFi discussion board.")
    await ctx.send("Type !help if you wanna learn what I can do.")
    await ctx.send(
      "If you'd like to join our friendly portfolio competition " +
      "use the !register command to register your wallet address."
    )

  @commands.command(name='register')
  async def register_wallet(self, ctx, address):
    """Used to register user's wallet address into replit db"""
    db[str(ctx.author)] = {}
    db[str(ctx.author)]['address'] = address.lower()
    await ctx.send(f'Thanks {ctx.author}! Your wallet address has been registered.')

  @commands.command(name='deregister')
  async def deregister_wallet(self, ctx):
    """Used to remove user's information from replit db"""
    del db[str(ctx.author)]
    await ctx.send(f"Have no fear {ctx.author}, I won't store your data anymore!")

  @commands.command(name='balance', aliases=['bl'])
  async def get_user_balance(self, ctx):
    """Reports token balances on user's registered address"""
    # Check if user has wallet registered in db
    try:
      author = str(ctx.author)
      address = db[author]['address']
    except KeyError:
      await ctx.send(
        "Looks like you didn't register your wallet.\n" +
        "Please use the !register command to add your wallet to my database."
      )

    balances = utils.get_balances(address)
    balances = utils.parse_zapper_balance(balances, address.lower(), author)
    await ctx.send(balances)

  @commands.command(name='leaderboard')
  async def leaderboard(self, ctx):
    """Create user leaderboard based on 24hr portfolio changes"""
    await ctx.send('Fetching leaderboard data...')
    msg = utils.get_leaderboard()
    await ctx.send(msg)

  @commands.command(name='news')
  async def news(self, ctx, num_articles=3):
    """Post top X articles from the rekt newsfeed."""
    msgs = utils.parse_rekt_feed(self.latest_news[0:num_articles])
    for msg in msgs:
      await ctx.send(msg)

  @tasks.loop(hours=24)
  async def update_news_feed(self):
    """Update list of top articles every 24 hours"""
    print('updating news feed...')
    self.latest_news = utils.get_top_rekt_posts()
    print('finised updating news feed')

  @commands.command(name='custombalance', aliases=['cb'])
  async def custom_balance(self, ctx, token: str.upper):
    """Used to report balance of particular token in user's wallet"""

    network = 'MATIC' #hardcoded for now
    
    # Check if user has wallet registered in db
    try:
      address = db[str(ctx.author)]
      balance = utils.get_balance_custom(address, network, token)
      await ctx.send(f'On {network} network you have {balance} {token}')
    except KeyError:
      await ctx.send(
        "Looks like you didn't register your wallet.\n" +
        "Please use the !register command to add your wallet to my database."
      )
    
  @custom_balance.error
  async def custom_balance_error(self, ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
      await ctx.send(f"You forgot to add the {error.param.name} you want me to look for.")

    
def setup(bot):
  bot.add_cog(DefiCommands(bot))