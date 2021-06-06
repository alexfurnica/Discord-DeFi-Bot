from web3 import Web3
from web3.middleware import geth_poa_middleware
import os
import requests
from replit import db
from pycoingecko import CoinGeckoAPI
from datetime import date, timedelta

# Mapping for tokens where the ID is different between zapper and coingecko APIs
ID_MAPPING = {
  'dquick': 'dragons-quick',
  'matic': 'matic-network'
}

# Setup Zapper.fi constants
ZAPPER_API_KEY = "96e0cc51-a62e-42ca-acee-910ea7d2a241" #public key anyone can use

def get_balances(user_address):
  """Get user balances via zapper.fi API"""

  request = requests.get(
    "https://api.zapper.fi/v1/protocols/tokens/balances", 
    params={
      'addresses[]': [user_address],
      "api_key": ZAPPER_API_KEY,
      'network': 'polygon'
    },
    headers={'accept': 'application/json'}
  )

  if request.status_code == 200:
      return request.json()
  else:
      raise Exception(f"Unexpected status code returned: {request.status_code}")

def parse_zapper_balance(balance, address, author):
  """
  Cleans the output of the Zapper.fi v1/protocols/tokens/balance API endpoint.
  """

  # Initial key of zapper.fi API json is always the address
  balance = balance[address]

  # Assets tag contains information on individual assets owned
  assets = balance['products'][0]['assets']
  
  # Meta tag contains information about the portfolio value as a whole
  meta = balance['meta']

  # Start with a blank message that we fill in as we loop through the balance json
  msg = f"{author}, your wallet balance is: \n\n"

  for grouping in meta:
    if grouping['label'] == 'Total':
      msg += f"Total wallet value: ${round(grouping['value'],2)} \n"
    elif grouping['label'] == 'Assets':
      msg += f"Value of assets in wallet: ${round(grouping['value'],2)} \n"
    else:
      msg += f"Total debt undertaken: ${round(grouping['value'],2)} \n\n"

  msg += "------------------------------------------------\n\n"

  for asset in assets:
    symbol = asset['symbol']
    token_balance = asset['balance']
    usd_value = asset['balanceUSD']
    current_rate = asset['price']
    
    msg += f"{round(token_balance,4)} {symbol}: ${round(usd_value,2)} | (${current_rate}/{symbol})\n"

  return msg

def get_leaderboard():
  """Create leaderboard message for bot to post"""
  leaderboard = {}

  # Get score of each user
  for user in db.keys():
    data = db[user]
    address = data['address']
    balance = get_balances(address)[address]

    assets = balance['products'][0]['assets']
    current_value = balance['meta'][0]['value']
    prev_day = 0
    cg = CoinGeckoAPI()

    # Get value of tokens from previous day
    for asset in assets:
      name = asset['label'].lower()
      if name in ID_MAPPING.keys():
        name = ID_MAPPING[name]

      token_balance = asset['balance']
      yesterday = date.today() - timedelta(days=1)
      prev_price = cg.get_coin_history_by_id(name, yesterday.strftime('%d-%m-%Y'))['market_data']['current_price']['usd']
      print(f'{name}: {token_balance} balance, {prev_price} price')
      prev_day += token_balance * prev_price

    # Calculate the percentage change from the previous day
    perc_change = portfolio_change(current_value, prev_day)
    leaderboard[user] = perc_change

  msg = format_leaderboard_msg(leaderboard)

  return msg

def portfolio_change(current_value, prev_value):
  """Calculate the percentage change in the user's portfolio"""
  if current_value > prev_value:
    return round(((current_value - prev_value) / prev_value) * 100, 2)
  else:
    return round(((prev_value - current_value) / prev_value)* 100 * -1, 2)

def format_leaderboard_msg(leaderboard):
  """Format the message that the bot sends based on the calculated leaderboard"""
  
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
      msg += f"#{counter} {user}: {perc_change}%"
    else:
      msg += f"#{counter} {user}: {perc_change}%"

  return msg


# --- WIP FEATURES ---
from unused import thegraph

### Web3 info should depend on the network selected
# Setup web3 with Infura
w3 = Web3(Web3.HTTPProvider(f"https://polygon-mainnet.infura.io/v3/{os.environ['INFURA_PROJECT_ID']}"))

# To process Matic blocks, which are different to Ethereum in block size
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Function to get balance of given user directly from smart contract
# Can be used for custom tokens not supported by zapper.fi
# network currently not being used, only MATIC in v1
def get_balance_custom(user_address, network, token):
  # instantiate contract
  contract = w3.eth.contract(CONTRACTS[token]['address'], abi=CONTRACTS[token]['abi'])
  
  if token == 'MATIC':
    balance = w3.eth.get_balance('0xb3e3D434c074272C8E99c88D40F188b92274A891')
  else:
    balance = contract.functions.balanceOf(user_address).call()
  ndecimals = contract.functions.decimals().call()
  decimals = 10 ** ndecimals

  return round(balance / decimals, 4)

def query_graph(subgraph,query):

  # Hardcoded to quickswap subgraph on Polygon
  subgraph = thegraph.QUICKSWAP_GRAPH_ADDRESS

  # Hardcoded for testing purposes
  query = thegraph.test_uni_lp_query

  r = requests.post(subgraph, json={'query': query})

  if r.status_code == 200:
    return r.json()
  else:
    raise Exception(f"Unexpected status code returned: {r.status_code}")