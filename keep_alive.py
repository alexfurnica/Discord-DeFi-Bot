"""
This file contains the code to keep a running server and make sure the bot stays alive. Without constant pings to the server, replit will close the bot after some time due to inactivity.
"""
from flask import Flask
from threading import Thread
import random

app = Flask('')

@app.route('/')
def home():
	return 'Im in!'

def run():
  app.run(
		host='0.0.0.0',
		port=random.randint(2000,9000)
	)

def keep_alive():
  t = Thread(target=run, daemon=True)
  t.start()