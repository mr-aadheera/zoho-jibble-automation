# Zoho Books → Jibble Automation

Automatically creates a **Jibble project** the moment a **new Customer is added in Zoho Books**, using the customer's name and Zoho Customer ID — no manual data entry required.

Built for [Aarif & Associates LLP](https://auditoraarif.com/), Trichy, as part of an internal office automation stack that also includes WhatsApp (WATI) invoice/payment automation and Vi CPaaS call handling.

---

## How it works

```
New Customer created in Zoho Books
            │
            ▼
   Zoho Books Workflow Webhook (fires automatically)
            │
            ▼
   Local Flask server (this repo) receives the webhook
            │
            ▼
   Flask app authenticates with Jibble (OAuth2 client credentials)
            │
            ▼
   New Project created in Jibble, named after the customer,
   with the Zoho Customer ID stored in the description field
```

Since Zoho Books needs a public HTTPS URL to send its webhook to, this project uses **ngrok** to expose the local Flask server to the internet during development/testing. For production use, this should instead be deployed on an always-on server (e.g. a NAS or cloud VM) — see [Production Notes](#production-notes) below.

---

## Features

- Zero manual entry — new Zoho Books customers automatically get a Jibble project
- Secrets kept out of source control via `.env` (see [Security](#security))
- Simple health-check endpoint for monitoring
- Auto-start script so the whole stack comes up automatically when the PC boots

---

## Prerequisites

- Python 3.10+
- A [Zoho Books](https://www.zoho.com/us/books/) account with Workflow/Webhook access
- A [Jibble](https://www.jibble.io/) account with API Credentials access
- A free [ngrok](https://ngrok.com/) account (for local testing)

---

## Setup

### 1. Clone the repo and install dependencies

```bash
git clone https://github.com/mr-aadheera/zoho-jibble-automation.git
cd zoho-jibble-automation
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

### 2. Get your Jibble API credentials

1. Log into Jibble → **Organization Settings** → **API Credentials** tab.
2. Click **Create New Secret**, name it, and copy the **Client ID** and **Client Secret**.

> 📸 *Screenshot: Jibble API Credentials screen — `docs/screenshots/jibble-api-credentials.png`*

### 3. Get your ngrok auth token

1. Sign up / log in at [dashboard.ngrok.com](https://dashboard.ngrok.com/).
2. Go to **Your Authtoken** and copy it.

### 4. Configure your secrets

Copy the example env file and fill in your real values:

```bash
copy .env.example .env        # Windows
# cp .env.example .env        # macOS/Linux
```

Edit `.env`:
```
JIBBLE_CLIENT_ID=your_jibble_client_id
JIBBLE_CLIENT_SECRET=your_jibble_client_secret
NGROK_AUTH_TOKEN=your_ngrok_auth_token
```

### 5. Run the Flask app

```bash
python app.py
```

You should see:
```
Running on http://0.0.0.0:5000
```

> 📸 *Screenshot: Flask server running successfully — `docs/screenshots/flask-running.png`*

### 6. Start the ngrok tunnel (in a separate terminal)

```bash
venv\Scripts\activate
python run_tunnel.py
```

This prints a public URL, e.g.:
```
Your public URL: https://your-random-name.ngrok-free.dev
```

> ⚠️ On the free ngrok plan, this URL changes every time the tunnel restarts. Update your Zoho Books webhook URL whenever that happens.

### 7. Test locally before connecting Zoho Books

```bash
curl -X POST https://your-random-name.ngrok-free.dev/create-jibble-project ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"Test Client\",\"customer_id\":\"CUST-001\"}"
```

Expected response: `"status": 201` and a matching project appears in Jibble.

> 📸 *Screenshot: Successful curl test + matching Jibble project — `docs/screenshots/curl-test-success.png`*

### 8. Set up the webhook in Zoho Books

1. Go to **Zoho Books** → **Settings** → **Automation** → **Workflows**.
2. Click **New Workflow Rule**.
3. **Module**: `Customers`.
4. Leave the trigger as **"executed when Customers is created."**
5. Under **Immediate Actions**, select **Webhooks** → **Add New Webhook**.
6. Configure:
   - **Method**: `POST`
   - **URL**: `https://your-ngrok-url/create-jibble-project`
   - **Header**: `Content-Type: application/json`
   - Leave **"I want to secure this webhook"** unchecked (this basic setup doesn't validate the secret yet)
   - **Body**: select **Raw**, then build:
     ```json
     {
       "name": "${Contacts.Customer Name}",
       "customer_id": "${Contacts.Customer ID}"
     }
     ```
     Use the **Insert Placeholder** dropdown to insert the actual field tags rather than typing them by hand.
7. Save and activate the rule.

> 📸 *Screenshot: Completed Zoho Books webhook configuration — `docs/screenshots/zoho-webhook-config.png`*

### 9. Test end-to-end

1. Create a real test customer in Zoho Books.
2. Confirm a `POST` request appears automatically in the Flask terminal.
3. Confirm a matching project appears in Jibble.

---

## Auto-start on PC boot (Windows)

To keep this running automatically without manually opening terminals every time:

### Option A: Startup folder (simplest)

1. Edit `start_automation.bat` in this repo and set `PROJECT_DIR` to your actual project path.
2. Press `Win + R`, type `shell:startup`, hit Enter.
3. Place a shortcut to `start_automation.bat` in that folder.
4. On next boot, both the Flask server and ngrok tunnel will launch automatically in their own windows.

### Option B: Task Scheduler (more reliable, recommended)

1. Open **Task Scheduler** → **Create Task**.
2. **General tab**: name it "Zoho Jibble Automation", check **"Run whether user is logged on or not."**
3. **Triggers tab**: New → **At log on**.
4. **Actions tab**: New → **Start a program** → point it at `start_automation.bat`.
5. **Conditions tab**: uncheck **"Start the task only if the computer is on AC power"** if this runs on a laptop.
6. Save. Restart your PC to confirm both windows launch automatically.


---

## Security

- **Never commit your `.env` file.** It's already excluded via `.gitignore`.
- `.env.example` is provided as a template only — it contains no real credentials.
- If you accidentally commit a real secret, treat it as compromised: regenerate it immediately in Jibble/ngrok's dashboard.
- The Zoho Books webhook is currently unauthenticated (no shared secret validation) — acceptable for internal/testing use, but see Production Notes below before exposing this more broadly.

---

## Production Notes

This setup is designed for local development and testing. For continuous, reliable use in an office environment, consider:

- Hosting the Flask app on an always-on machine (e.g. a Synology NAS via Docker, or a small cloud VM) instead of a personal PC + ngrok.
- Using a fixed domain (via reverse proxy + DDNS, or a paid ngrok static domain) so the webhook URL never needs to be manually updated.
- Adding webhook signature verification (Zoho Books' "secure this webhook" option) to confirm requests are genuinely from Zoho.
- Adding retry logic and failure alerting (e.g. a WhatsApp notification via WATI) if the Jibble API call fails.
- Adding duplicate-prevention logic (checking if a project already exists for a given Customer ID before creating a new one).

---

## Tech Stack

- Python 3 / Flask — webhook receiver
- Jibble REST API — project creation
- Zoho Books Workflows/Webhooks — trigger source
- ngrok — local tunnel for development/testing

---

## Author

**Aadhil Mohamed** — ANFI Technologies, Tiruchirappalli
Built for [Aarif & Associates LLP](https://auditoraarif.com/)

## License

MIT
