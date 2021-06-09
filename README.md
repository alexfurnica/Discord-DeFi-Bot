# Gainsley - the friendly DeFi bot

Gainsley is a Discord bot that intends to help foster a community of DeFi explorers. This imagined community would present an opportunity for friends that are interested in exploring the DeFi space to learn from each other in the context of a friendly competition.

Gainsley will help users understand the current state of their portfolio, as well as the change in dollar value of their portfolio in the past 24 hours.

This bot build was prompted by the [1729.com Discord replit task](https://1729.com/replit-discord). As such, time limit to complete this task was a major factor in deciding which features would be in. There are many possibilities for upgrading this bot, some of which I've outlined in the "Potnetial new features" section.

Many thanks to AllAwesome497 for providing a great starting point with his [Discord.py bot template](https://replit.com/@templates/Discordpy-bot-template-with-commands-extension). I've left in most of the original explanation on how to setup the bot since it is still essential to using this app and making it your own.

## Features

### Registering a user's address

Since many DeFi-related actions and commands require a wallet address, the bot would be very cumbersome to use if you had to type your wallet address every time. As such, a user can register their address with Gainsley using the `!register` command. 

Example: `!register 0x00275072a952f7731d507dc5dec9bcb27c13cfc3`

![Register response](https://imgur.com/KLAMrmy.png)

Future commands that will require a wallet address will use this address for the user by default.

### De-registering a user's address

If a user would like to remove their address from the bot's memory, they are the only one that can do so. This is achieved by running the `!deregister` command with no other parameters.

![Deregister response](https://imgur.com/0sUBFcx.png)

### Balance querying

Using the [zapper.fi API](https://docs.zapper.fi/zapper-api/api-getting-started) Gainsley can query a user's wallet address for its token balances. By typing `!balance` or `!bl`, Gainsley will query zapper with the user's registered wallet address as input.

![Balance query](https://imgur.com/tIED007.png)

### Leaderboard

The leaderboard is the main community feature of this bot. When a user types `!leaderboard` in the chat, the bot will look up the balances of all registered users. It will then calculate the percentage change in the portfolio value from the day before till today.

If there is a clear winner, the bot will declare a winner and encourage them to share their portfolio with the group. After all, the community should be built around shared learning. Together, we can get the best gains!

![leaderboard](https://imgur.com/eA3bRhX.png)

### News feed

To keep the community up-to-date on the latest in DeFi news and opportunities, the bot can post articles from the rekt.news feed.

Any user can use the `!news [num articles]` command. Providing the desired number of articles is optional and defaults to 3 articles. After the command is called, the bot will post the articles with their links to the channel.

Every 24 hours the bot will check the rekt news feed and update the list of articles internally.

![news](https://imgur.com/uJV5rHo.png)

## Bot setup
### Pre-Setup

If you don't already have a discord bot, click [here](https://discordapp.com/developers/), accept any prompts then click "New Application" at the top right of the screen.  Enter the name of your bot then click accept.  Click on Bot from the panel from the left, then click "Add Bot."  When the prompt appears, click "Yes, do it!" 

![Left panel](https://i.imgur.com/hECJYWK.png)

Then, click copy under token to get your bot's token. Your bot's icon can also be changed by uploading an image.

![Bot token area](https://i.imgur.com/da0ktMC.png)

### Setup

Use the "Secrets" tab on the left of the repl. This is where you can add environment variables that hold data that you'd like to keep private. 

Add a secret called `DISCORD_BOT_SECRET` and fill it with your bot's token.

After adding your bot token to your secrets, add a secret called `DISCORD_AUTHOR_ID` with your Discord author ID as well. To get your id, ensure developer mode is enabled (Settings->Appearance->Advanced->Developer Mode) then right-click on yourself in one of your servers and click copy ID.

When you hit start everything should startup fine.

### Uptime

So now, all you have to do to keep your bot up is setup something to ping the site your bot made every 5 minutes or so.

Go to [uptimerobot.com](https://uptimerobot.com/) and create an accout if you dont have one.  After verifying your account, click "Add New Monitor".

+ For Monitor Type select "HTTP(s)"
+ In Friendly Name put the name of your bot
+ For your url, put the url of the website created by your repl when the server is activated.
+ Select any alert contacts you want, then click "Create Monitor" 

![Uptime robot example](https://i.imgur.com/Qd9LXEy.png)

Your bot should now be good to go, with near 100% uptime.

## Potential new features

I may work on this bot more in the future and this is just what I managed to get done in time for the 1729.com task. That being said, feel free to fork the code and upgrade it with features that you think would be helpful!

- Supporting more networks (currently only Polygon & Ethereum are supported)
- Supporting multiple channels within the same Discord server
- Detect token purchase and sell-off to not include them in leaderboard calculation
- Make leaderboard more efficient by storing previous day in DB instead of querying
- Option to only allow balance and portfolio details in private message
- Post notifications about a new protocol getting rekt from [rekt.news](rekt.news)
- Get latest DeFi rates from [defirates.com](defirates.com), [apy.vision](apy.vision), and/or [zapper.fi](zapper.fi)
- Support for liquidity pool tokens
- Support for interest-bearing tokens e.g. Aave aTokens
- Let users query the balance of any wallet address on supported networks
- Support for multiple addresses per user
- Unit tests
- More extensive error handling

## Contact

If you like the concept of the bot or want to contact me to chat about all things blockchain and DeFi, hit me up @alexfurnica on Twitter.

## Acknowledgements

Thank you to [Zapper](zapper.fi) for making the best portfolio tool in DeFi that I've encountered and on top of that making *both the tool and their API free*. That's an invaluable contribution to the community and I am very grateful to them for it.

Definitely check out their tool and API for your own projects.

![Powered by Zapper](https://gblobscdn.gitbook.com/assets%2F-M5uNzoH28DRNpZdcArj%2F-MXCoKNsFpOZtmNysZlR%2F-MXD4qmrgRCcOC7XcEIm%2Fpower-zap-gray.svg)

A big thank you also to [CoinGecko](https://www.coingecko.com/), who also have their API for free.