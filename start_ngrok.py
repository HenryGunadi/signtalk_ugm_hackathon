import subprocess
import os
from dotenv import load_dotenv
import argparse
import time

if os.path.exists(".env"):
    load_dotenv()
    print("ENV loaded")
    
FRONTEND_PORT = os.getenv("FRONTEND_PORT", "5173")
FLASK_PORT = os.getenv("FLASK_PORT", "5000")
WS_PORT = os.getenv("WS_PORT", "8765")
NGROK_AUTHTOKEN = os.getenv("NGROK_AUTHTOKEN")

if not NGROK_AUTHTOKEN:
    print("NGROK_AUTHTOKEN not found in environment!")
    exit(1)
    
ngrok_config_path = "ngrok.yml"

# Dynamically create ngrok.yml with the token from env
with open(ngrok_config_path, "w") as f:
    f.write(f"""version: '2'
authtoken: {NGROK_AUTHTOKEN}

tunnels:
  flask:
    addr: {FLASK_PORT}
    proto: http
  websocket:
    addr: {WS_PORT}
    proto: http
  frontend:
    addr: {FRONTEND_PORT}
    proto: http
""")

processes = []

def start_process(label, command, cwd=None):
    print(f"Starting {label}...")
    proc = subprocess.Popen(command, shell=True, cwd=cwd)
    processes.append((label, proc))

# Start local dev servers
start_process("Frontend", "npm run dev", cwd="client")  # adjust path if needed
start_process("Backend", f"python app.py", cwd="backend/src")  # adjust

# Give servers time to start
time.sleep(5)

# Start ngrok tunnels
start_process("Ngrok All Tunnels", "ngrok start --all --config=ngrok.yml")

# Trap Ctrl+C
try:
    print("All services running. Press Ctrl+C to stop.")
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Shutting down all processes...")
    for label, proc in processes:
        print(f"Terminating {label}")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
    print("✅ Clean shutdown complete.")