"""
Zoho Books -> Jibble Automation
--------------------------------
Listens for a webhook from Zoho Books (fired when a new Customer is created)
and automatically creates a matching Project in Jibble, storing the Zoho
Customer ID in the project's description field for reference.

Author: Aadhil Mohamed / ANFI Technologies
"""

import os
from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv

# Load secrets from a local .env file (never committed to GitHub)
load_dotenv()

app = Flask(__name__)

JIBBLE_CLIENT_ID = os.getenv("JIBBLE_CLIENT_ID")
JIBBLE_CLIENT_SECRET = os.getenv("JIBBLE_CLIENT_SECRET")

JIBBLE_TOKEN_URL = "https://identity.prod.jibble.io/connect/token"
JIBBLE_PROJECTS_URL = "https://workspace.prod.jibble.io/v1/Projects"


def get_jibble_token():
    """Fetch a fresh Jibble access token using client-credentials grant."""
    resp = requests.post(
        JIBBLE_TOKEN_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": JIBBLE_CLIENT_ID,
            "client_secret": JIBBLE_CLIENT_SECRET,
        },
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


@app.route("/create-jibble-project", methods=["POST"])
def create_jibble_project():
    """
    Expects JSON body:
    {
        "name": "<Customer Name>",
        "customer_id": "<Zoho Customer ID>"
    }
    """
    data = request.json or {}
    name = data.get("name")
    customer_id = data.get("customer_id")

    if not name:
        return jsonify({"error": "Missing 'name' in request body"}), 400

    token = get_jibble_token()
    resp = requests.post(
        JIBBLE_PROJECTS_URL,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json={"name": name, "description": customer_id},
    )

    return jsonify({"status": resp.status_code, "response": resp.json()}), resp.status_code


@app.route("/health", methods=["GET"])
def health_check():
    """Simple endpoint to confirm the server is alive (useful for testing)."""
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
