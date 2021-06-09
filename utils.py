"""
This file contains all utility functions that the bot needs to use when commands are triggered.
"""

from web3 import Web3
from web3.middleware import geth_poa_middleware
import os
import requests
from replit import db
from pycoingecko import CoinGeckoAPI
from datetime import date, timedelta
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Mapping for tokens where the ID is different between zapper and coingecko APIs
ID_MAPPING = {
  'dquick': 'dragons-quick',
  'matic': 'matic-network',
  'eth': 'ethereum',
  'vision': 'apy-vision'
}

# Setup Zapper.fi constants
ZAPPER_API_KEY = "96e0cc51-a62e-42ca-acee-910ea7d2a241" #public key anyone can use

def get_balances(user_address):
  """
  Get user balances via zapper.fi API
  
  Parameters:
    - user_address (string): wallet address of the user

  Returns:
    A dict of the user's token balances per network.
  """

  networks = ['ethereum', 'polygon']
  balances = {}

  for network in networks:
    request = requests.get(
      "https://api.zapper.fi/v1/protocols/tokens/balances", 
      params={
        'addresses[]': [user_address],
        "api_key": ZAPPER_API_KEY,
        'network': network
      },
      headers={'accept': 'application/json'}
    )

    balance = request.json()

    if len(balance[user_address]['products']): # if empty balance on network, skip
      if request.status_code == 200:
        balances[network] = balance
      else:
          raise Exception(f"Unexpected status code returned: {request.status_code}")
  
  return balances

def parse_zapper_balance(balances, address, author):
  """
  Cleans the output of the Zapper.fi v1/protocols/tokens/balance API endpoint.

  Parameters:
    - balances (dict): dict of user's token balances per network
    - address (string): user's wallet address
    - author (string): name of the user that called the function

  Returns:
    A formatted message containing the user's balances.
  """
  # Start with a blank message that we fill in as we loop through the balance json
  msg = f"{author}, your wallet balance is: \n\n"
  assets_msg = ""
  meta_total = 0
  meta_assets = 0
  meta_debt = 0

  for network, data in balances.items():

    # Initial key of zapper.fi API json is always the address
    balance = data[address]

    # Assets tag contains information on individual assets owned
    assets = balance['products'][0]['assets']
  
    # Meta tag contains information about the portfolio value as a whole
    meta = balance['meta']

    # Make clear which assets come from which network
    assets_msg += f"On the {network.capitalize()} network you have:\n"

    for grouping in meta:
      if grouping['label'] == 'Total':
        meta_total += round(grouping['value'],2)
      elif grouping['label'] == 'Assets':
        meta_assets += round(grouping['value'],2)
      else:
        meta_debt += round(grouping['value'],2)

    for asset in assets:
      symbol = asset['symbol']
      token_balance = asset['balance']
      usd_value = asset['balanceUSD']
      current_rate = asset['price']
      
      assets_msg += f"{round(token_balance,4)} {symbol}: ${round(usd_value,2)} | (${current_rate}/{symbol})\n"
    
    assets_msg += '\n'

  
  msg += f"Total wallet value: ${round(meta_total,2)} \n"
  msg += f"Value of assets in wallet: ${round(meta_assets,2)} \n"
  msg += f"Total debt undertaken: ${round(meta_debt,2)} \n\n"
  msg += "------------------------------------------------\n\n"
  msg += assets_msg

  return msg

def get_leaderboard():
  """
  Create leaderboard message for bot to post

  Returns:
    Formatted leaderboard message
  """
  leaderboard = {}

  # Get score of each user
  for user in db.keys():
    user_data = db[user]
    address = user_data['address']
    balances = get_balances(address)
    current_value = 0
    prev_day_value = 0
    cg = CoinGeckoAPI()

    for network, data in balances.items():

      balance = data[address]

      assets = balance['products'][0]['assets']
      current_value += balance['meta'][0]['value']

      # Get value of tokens from previous day
      for asset in assets:
        name = asset['label'].lower()

        if name in ID_MAPPING.keys():
          name = ID_MAPPING[name]

        token_balance = asset['balance']
        yesterday = date.today() - timedelta(days=1)

        try:
          prev_price = cg.get_coin_history_by_id(name, yesterday.strftime('%d-%m-%Y'))['market_data']['current_price']['usd']
        
        # If CoinGecko throws error, likely token ID needs to be added to ID_MAPPING
        # Find proper ID using the coins list  endpoint of the CoinGecko API
        except KeyError:
          print(name) # to know which token has the error
          return f"Looks like I've run into an error trying to retreive the price of a token. Most likely the token label needs to be mapped by my master."

        prev_day_value += token_balance * prev_price

    # Calculate the percentage change from the previous day
    perc_change = portfolio_change(current_value, prev_day_value)
    leaderboard[user] = perc_change

  msg = format_leaderboard_msg(leaderboard)

  return msg

def portfolio_change(current_value, prev_value):
  """
  Calculate the percentage change in the user's portfolio

  Parameters:
    - current_value (float): current value of the user's portfolio
    - prev_value (float): value of the portfolio from previous 24 hours

  Returns:
    The percentage change in portfolio value expressed as 50% not 0.5   
  """
  if current_value > prev_value:
    return round(((current_value - prev_value) / prev_value) * 100, 2)
  else:
    return round(((prev_value - current_value) / prev_value)* 100 * -1, 2)

def format_leaderboard_msg(leaderboard):
  """
  Format the message that the bot sends based on the calculated leaderboard

  Parameters:
    - leaderboard (dict): users as keys and portfolio changes as values

  Returns:
    Formatted leaderboard message
  """
  
  # Sort the leaderboard descending
  sorted_board = {k:v for k,v in sorted(leaderboard.items(), key= lambda item: item[1], reverse=True)}
  msg = ""
  counter = 1

  # Format the leaderboard message
  for user, perc_change in sorted_board.items():
    if counter == 1:
      # If first place has negative return, laugh at all the degens
      if perc_change < 0:
        msg += "Looks like none of you did that great this time. Maybe try stables?\nBetter luck next time!"
      else:
        msg += f"Looks like {user}'s portfolio did the best in the past 24 hours!\nDo share your strategy with the rest of the group."
      msg += '\n----------------------------------\n'
      
      if perc_change > 0:
        msg += f"#{counter} {user}: +{perc_change}%\n"
      else:
        msg += f"#{counter} {user}: {perc_change}%\n"
    else:
      if perc_change > 0:
        msg += f"#{counter} {user}: +{perc_change}%\n"
      else:
        msg += f"#{counter} {user}: {perc_change}%\n"

    counter += 1

  return msg

def get_top_rekt_posts():
  """
  Get all posts from feed.rekt.news front page.

  Returns:
    List of dict where key is article title and value is link to article
  """

  latest_news = []

  chrome_options = Options()
  chrome_options.add_argument('--no-sandbox')
  chrome_options.add_argument('--disable-dev-shm-usage')

  driver = webdriver.Chrome(options=chrome_options)
  driver.get("http://feed.rekt.news")
  soup = BeautifulSoup(driver.page_source, 'html.parser')

  for post in soup.find_all('li', class_='my-1'):
    a = post.find('a', href=True)
    latest_news.append({
      'title': a.string,
      'link': a['href']
    })

  return latest_news

def parse_rekt_feed(latest_news):
  """
  Creates a formatted message out of the stored latest news articles.

  Parameters:
    - latest_news (list): List of all news articles

  Returns:
    Formatted message containing article links.
  """

  msgs = []

  for i in range(len(latest_news)):
    item = latest_news[i]
    msgs.append(f"{item['title']}:\n {item['link']}")

  return msgs


# --- WIP FEATURES ---
from unused import thegraph
from unused.contracts import MATIC_CONTRACTS

### Web3 info should depend on the network selected
# Setup web3 with Infura
w3 = Web3(Web3.HTTPProvider(f"https://polygon-mainnet.infura.io/v3/{os.environ['INFURA_PROJECT_ID']}"))

# To process Matic blocks, which are different to Ethereum in block size
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Function to get balance of given user directly from smart contract
# Can be used for custom tokens not supported by zapper.fi
# network currently not being used, only MATIC in v1
def get_balance_custom(user_address, network, token):
  """
  Get user's balance for a particular token.

  Parameters:
    - user_address (string): user's wallet address
    - network (string): the network on which the token is deployed
    - token (string): name of token to look for

  Returns:
    The user's balance of chosen token.
  """
  contract = w3.eth.contract(MATIC_CONTRACTS[token]['address'], abi=MATIC_CONTRACTS[token]['abi'])
  
  if token == 'MATIC':
    balance = w3.eth.get_balance('0xb3e3D434c074272C8E99c88D40F188b92274A891')
  else:
    balance = contract.functions.balanceOf(user_address).call()
  ndecimals = contract.functions.decimals().call()
  decimals = 10 ** ndecimals

  return round(balance / decimals, 4)

def query_graph(subgraph,query):
  """
  Query a subgraph stored on the Graph with provided query.

  Parameters:
    - subgraph (string): Address of subgraph to query
    - query (string): query to send to subgraph

  Returns:
    The JSON response from the subgraph.
  """

  # Hardcoded to quickswap subgraph on Polygon
  subgraph = thegraph.QUICKSWAP_GRAPH_ADDRESS

  # Hardcoded for testing purposes
  query = thegraph.test_uni_lp_query

  r = requests.post(subgraph, json={'query': query})

  if r.status_code == 200:
    return r.json()
  else:
    raise Exception(f"Unexpected status code returned: {r.status_code}")