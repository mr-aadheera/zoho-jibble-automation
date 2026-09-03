@echo off
REM ============================================================
REM  Zoho Books -> Jibble Automation - Auto Start Script
REM  Launches the Flask app and the ngrok tunnel, each in their
REM  own window, so the automation is live without manual steps.
REM
REM  IMPORTANT: Update PROJECT_DIR below to match your actual
REM  project folder path before using this script.
REM ============================================================

set PROJECT_DIR=D:\zoho-automation

REM Start Flask app in its own window
start "Flask - Zoho Jibble App" cmd /k "cd /d %PROJECT_DIR% && venv\Scripts\activate && python app.py"

REM Wait a few seconds so Flask is up before the tunnel tries to connect
timeout /t 5 /nobreak >nul

REM Start ngrok tunnel in its own window
start "Ngrok Tunnel" cmd /k "cd /d %PROJECT_DIR% && venv\Scripts\activate && python run_tunnel.py"
