import sys
from dotenv import load_dotenv
load_dotenv()

from flask import Flask
# from aiortc import RTCPeerConnection, MediaStreamTrack
from flask_socketio import SocketIO
from flask_cors import CORS
import os
from supabase import create_client
from flask_jwt_extended import JWTManager, jwt_required
from controllers import controllers
from ws_server import App, Server
import asyncio
from config import init_config
import threading
from asyncio import Future

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
secret_key = os.environ.get("SECRET_KEY")
jwt_cookie_secure = os.environ.get("JWT_COOKIE_SECURE")
port = int(os.environ.get("PORT", 5000))

supabase = create_client(url, key)

app = Flask(__name__, template_folder="templates")
socketio = SocketIO(app)

jwt = JWTManager(app)

# websocket server
ws_app = App()
ws_server = Server(ws_app)

# cors settings
CORS(
    app,
    resources={r"/*": {"origins": "http://localhost:3000"}}, # <-- fix it later in production
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE"],
    supports_credentials=True
)

# initialize config
init_config(app=app,
            secret_key=secret_key,
            jwt_cookie_secure=jwt_cookie_secure)

# controllers
index_controller = controllers.create_index_bp(supabase)
auth_controller = controllers.create_auth_bp(supabase)

app.register_blueprint(index_controller)
app.register_blueprint(auth_controller)

async def shutdown(tasks, flask_thread):
    await asyncio.sleep(3)

    for task in tasks:
        if isinstance(task, asyncio.Task):
            task.cancel()

    if flask_thread.is_alive():
        print("Stopping Flask server...")
        os._exit(0)

    await asyncio.sleep(1)

def run_flask():
    app.run(debug=True, port=port, host="0.0.0.0", use_reloader=False)

async def run_ws_server():
    await ws_server.run()

async def init_app():
    try:
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start() 

        ws_task = asyncio.create_task(run_ws_server())
        tasks = [ws_task]

        await asyncio.gather(*tasks)
    except (asyncio.CancelledError, KeyboardInterrupt):
        print("Received exit signal, shutting down...")
        await shutdown(tasks, flask_thread)
        sys.exit()

if __name__ == "__main__":
    asyncio.run(init_app())
