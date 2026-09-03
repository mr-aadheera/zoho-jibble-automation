"""
Starts an ngrok tunnel pointing to the local Flask app (port 5000),
so Zoho Books can reach it over the internet.

Note: On the ngrok free plan, this URL changes every time this script
restarts. Update the webhook URL in Zoho Books whenever that happens.
"""

import os
from pyngrok import ngrok
from dotenv import load_dotenv

load_dotenv()

NGROK_AUTH_TOKEN = os.getenv("NGROK_AUTH_TOKEN")

if NGROK_AUTH_TOKEN:
    ngrok.set_auth_token(NGROK_AUTH_TOKEN)

public_url = ngrok.connect(5000)
print("Your public URL:", public_url)
print("Use this + /create-jibble-project as your Zoho Books webhook URL")

input("Press Enter to stop the tunnel...")
